// Casual leaderboard: sessions, atomic single-use submissions and plausibility checks.
// Scores originate in a browser; this is not a competition-grade anti-cheat system.
const json = (data, status=200) => Response.json(data, {status, headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
export async function onRequest({request, env}) {
  if (!env.BLOCKS_DB) return json({error:'Shared leaderboard is not configured yet.'},503);
  try {
    if (request.method === 'GET') {
      const {results} = await env.BLOCKS_DB.prepare('SELECT name, score, lines FROM blocks_scores ORDER BY score DESC, created ASC LIMIT 10').all();
      return json({scores:results});
    }
    if (request.method !== 'POST') return new Response(null,{status:405,headers:{Allow:'GET, POST'}});
    if (request.headers.get('Origin') !== new URL(request.url).origin) return json({error:'Same-origin requests required.'},403);
    if (!(request.headers.get('Content-Type') || '').startsWith('application/json')) return json({error:'JSON required.'},415);
    // Bound actual streamed bytes, not just the untrusted Content-Length.
    const reader=request.body?.getReader(); if(!reader) return json({error:'Missing body.'},400);
    let length=0, chunks=[];
    while(true) { const {done,value}=await reader.read(); if(done) break; length+=value.length; if(length>1024) {await reader.cancel();return json({error:'Request too large.'},413);} chunks.push(value); }
    const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
    let body; try {body=JSON.parse(new TextDecoder().decode(bytes));} catch {return json({error:'Invalid JSON.'},400);}
    if(!body || typeof body !== 'object') return json({error:'Invalid request.'},400);
    const now=Math.floor(Date.now()/1000);
    if(body.action === 'start') {
      // Daily rotating hash; no raw IP addresses are stored. Old hashes expire after one day.
      const ip=request.headers.get('CF-Connecting-IP') || 'unknown';
      const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(ip+':'+Math.floor(now/86400)));
      const rate=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
      const id=crypto.randomUUID();
      await env.BLOCKS_DB.prepare('DELETE FROM blocks_sessions WHERE created < ?').bind(now-86400).run();
      // One atomic statement prevents parallel requests from racing the rate limit.
      const result=await env.BLOCKS_DB.prepare('INSERT INTO blocks_sessions(id,created,rate_key) SELECT ?,?,? WHERE (SELECT COUNT(*) FROM blocks_sessions WHERE rate_key=? AND created>?) < 30').bind(id,now,rate,rate,now-3600).run();
      if(!result.meta.changes) return json({error:'Leaderboard limit reached. Play locally and try sharing again later.'},429);
      return json({token:id},201);
    }
    const {token,name,score,lines}=body;
    if(typeof token!=='string' || !/^[a-f0-9-]{36}$/.test(token) || typeof name!=='string' || !/^[A-Za-z0-9 _-]{1,16}$/.test(name) || !name.trim() || !Number.isInteger(score) || score<1 || score>10000000 || !Number.isInteger(lines) || lines<0 || lines>10000) return json({error:'Use a name of 1–16 letters, numbers, spaces, underscores or hyphens and a valid score.'},400);
    const session=await env.BLOCKS_DB.prepare('SELECT created,used FROM blocks_sessions WHERE id=?').bind(token).first();
    if(!session || session.used || now-session.created<3 || now-session.created>21600) return json({error:'This game session has expired or was already shared.'},400);
    const seconds=now-session.created;
    if(lines>seconds*2 || score>seconds*2000 || score<lines*25) return json({error:'Score could not be validated.'},400);
    // The insert and consume run in one D1 batch transaction; only one caller wins.
    const results=await env.BLOCKS_DB.batch([
      env.BLOCKS_DB.prepare('INSERT INTO blocks_scores(id,name,score,lines,created) SELECT id,?,?,?,? FROM blocks_sessions WHERE id=? AND used=0').bind(name.trim(),score,lines,now,token),
      env.BLOCKS_DB.prepare('UPDATE blocks_sessions SET used=1 WHERE id=?').bind(token),
      env.BLOCKS_DB.prepare('DELETE FROM blocks_scores WHERE id NOT IN (SELECT id FROM blocks_scores ORDER BY score DESC,created ASC LIMIT 100)')
    ]);
    if(!results[0].meta.changes) return json({error:'This score was already shared.'},409);
    return json({ok:true},201);
  } catch(error) {
    console.error('Blocks leaderboard unavailable', error?.message);
    return json({error:'Shared leaderboard is temporarily unavailable. Your personal best stays on this device.'},503);
  }
}
