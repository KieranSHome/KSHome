'use strict';
(() => {
  const list=document.getElementById('leaderboard'), message=document.getElementById('leaderboard-status');
  async function request(body) {
    const response=await fetch('/api/blocks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const data=await response.json();if(!response.ok) throw new Error(data.error || 'Unable to share this score.');return data;
  }
  async function refresh() {
    try {
      const response=await fetch('/api/blocks',{cache:'no-store'});const data=await response.json();
      if(!response.ok || !Array.isArray(data.scores)) throw new Error();
      list.replaceChildren();
      for(const row of data.scores) {const item=document.createElement('li');item.textContent=row.name+' — '+Number(row.score).toLocaleString()+' points · '+row.lines+' lines';list.append(item);}
      if(!data.scores.length) {const item=document.createElement('li');item.textContent='No shared scores yet. Yours could be the first!';list.append(item);}
      message.textContent='Shared scores · refresh to see the latest round.';
    } catch {message.textContent='Shared leaderboard is currently unavailable. You can still play and save your personal best on this device.';list.replaceChildren();}
  }
  document.getElementById('refresh-scores')?.addEventListener('click',refresh); refresh();
  const form=document.getElementById('share-score');if(!form) return;
  let generation=0,tokenPromise=null,result=null,sharing=false;
  const shareStatus=document.getElementById('share-status');
  window.addEventListener('blocks:start',() => {
    generation++;form.hidden=true;result=null;shareStatus.textContent='';
    tokenPromise=request({action:'start'}).then(data=>({token:data.token})).catch(error=>({error:error.message}));
  });
  window.addEventListener('blocks:over',event => {
    result=event.detail;if(result.score>0) {form.hidden=false;form.querySelector('button').disabled=false;}
  });
  form.addEventListener('submit',async event => {
    event.preventDefault();if(sharing || !result) return;
    const current=generation, finalScore={...result}, nickname=document.getElementById('player-name').value.trim();
    sharing=true;const button=form.querySelector('button');button.disabled=true;shareStatus.textContent='Sharing…';
    try {
      const session=await tokenPromise;if(!session?.token) throw new Error(session?.error || 'This round cannot be shared.');
      await request({token:session.token,name:nickname,...finalScore});
      if(current===generation) {shareStatus.textContent='Score shared. Thanks for playing!';result=null;}
      await refresh();
    } catch(error) {if(current===generation){shareStatus.textContent=error.message;button.disabled=false;}}
    finally {sharing=false;}
  });
})();