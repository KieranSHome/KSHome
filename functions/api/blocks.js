// Casual leaderboard: sessions, atomic single-use submissions and plausibility checks.
// Scores originate in a browser; this is not a competition-grade anti-cheat system.
const json = (data, status=200, headers={}) => Response.json(data, {status, headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Strict-Transport-Security':'max-age=86400',...headers}});
// Each database statement is atomic, including simultaneous requests for the same key.
const WRITE_RATE_SQL = `INSERT INTO blocks_request_limits(rate_key,window,requests) VALUES (?,?,1) ON CONFLICT(rate_key) DO UPDATE SET window=excluded.window, requests=CASE WHEN blocks_request_limits.window=excluded.window THEN blocks_request_limits.requests+1 ELSE 1 END WHERE blocks_request_limits.window<>excluded.window OR blocks_request_limits.requests<60 RETURNING requests`;
const SESSION_CLEANUP_SQL = `DELETE FROM blocks_sessions WHERE id IN (SELECT id FROM blocks_sessions WHERE created < ? ORDER BY created LIMIT 100)`;
const RATE_CLEANUP_SQL = `DELETE FROM blocks_request_limits WHERE rate_key IN (SELECT rate_key FROM blocks_request_limits WHERE window < ? ORDER BY window LIMIT 100)`;
export async function onRequest({request, env, waitUntil}) {
  if (!env.BLOCKS_DB) return json({error:'Shared leaderboard is not configured yet.'},503);
  // Only public scores are cached. Ignore query strings and caller headers, isolate by origin.
  const cache=globalThis.caches?.default;
  const cacheKey=new Request(new URL('/api/blocks',request.url));
  try {
    if (request.method === 'GET') {
      try {
        const cached=await cache?.match(cacheKey);
        if(cached) {const response=new Response(cached.body,cached);response.headers.set('Cache-Control','no-store');return response;}
      } catch { /* A cache outage must not disable the leaderboard. */ }
      const {results} = await env.BLOCKS_DB.prepare('SELECT name, score, lines FROM blocks_scores ORDER BY score DESC, created ASC LIMIT 10').all();
      const response=json({scores:results});
      if(cache) {
        const stored=response.clone();stored.headers.set('Cache-Control','public, max-age=10');
        const write=cache.put(cacheKey,stored).catch(()=>{});
        if(waitUntil) waitUntil(write); else await write;
      }
      return response;
    }
    if (request.method !== 'POST') return new Response(null,{status:405,headers:{Allow:'GET, POST'}});
    if (request.headers.get('Origin') !== new URL(request.url).origin) return json({error:'Same-origin requests required.'},403);
    if (!(request.headers.get('Content-Type') || '').startsWith('application/json')) return json({error:'JSON required.'},415);
    const now=Math.floor(Date.now()/1000);
    // Hash before storing; apply a shared per-IP write budget before reading/parsing the body.
    const ip=request.headers.get('CF-Connecting-IP') || 'unknown';
    const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(ip+':'+Math.floor(now/86400)));
    const rate=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
    const minute=Math.floor(now/60);
    const budget=await env.BLOCKS_DB.prepare(WRITE_RATE_SQL).bind(rate,minute).first();
    if(!budget) return json({error:'Too many leaderboard requests. Please try again shortly.'},429,{'Retry-After':String(60-now%60)});
    // Bound actual streamed bytes, not just the untrusted Content-Length.
    const reader=request.body?.getReader(); if(!reader) return json({error:'Missing body.'},400);
    let length=0, chunks=[];
    while(true) { const {done,value}=await reader.read(); if(done) break; length+=value.length; if(length>1024) {await reader.cancel();return json({error:'Request too large.'},413);} chunks.push(value); }
    const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
    let body; try {body=JSON.parse(new TextDecoder().decode(bytes));} catch {return json({error:'Invalid JSON.'},400);}
    if(!body || typeof body !== 'object') return json({error:'Invalid request.'},400);
    if(body.action === 'start') {
      const id=crypto.randomUUID();
      // One atomic statement prevents parallel requests from racing the rate limit.
      const result=await env.BLOCKS_DB.prepare('INSERT INTO blocks_sessions(id,created,rate_key) SELECT ?,?,? WHERE (SELECT COUNT(*) FROM blocks_sessions WHERE rate_key=? AND created>?) < 30').bind(id,now,rate,rate,now-3600).run();
      if(!result.meta.changes) return json({error:'Leaderboard limit reached. Play locally and try sharing again later.'},429);
      // Indexed, bounded cleanup only after an admitted start; blocked requests never prune.
      await env.BLOCKS_DB.batch([
        env.BLOCKS_DB.prepare(SESSION_CLEANUP_SQL).bind(now-86400),
        env.BLOCKS_DB.prepare(RATE_CLEANUP_SQL).bind(minute-1440)
      ]);
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
    try {await cache?.delete(cacheKey);} catch { /* Other locations may remain stale for at most ten seconds. */ }
    return json({ok:true},201);
  } catch(error) {
    console.error('Blocks leaderboard unavailable', error?.message);
    return json({error:'Shared leaderboard is temporarily unavailable. Your personal best stays on this device.'},503);
  }
}
