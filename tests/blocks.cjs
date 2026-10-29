const fs=require('node:fs');
const source=fs.readFileSync('Projects/blocks/game.js','utf8');
function harness(source) {
  const elements = {};
  const context = new Proxy({}, {get:(_,key) => key === 'fillStyle' ? '' : () => {}, set:()=>true});
  function element(id) {return elements[id] ||= {textContent:'',disabled:false,handlers:{},getContext:()=>context,focus(){},addEventListener(name,fn){this.handlers[name]=fn;}};}
  const document={hidden:false,getElementById:element,querySelectorAll:()=>[],addEventListener(){}};
  const window={events:[],addEventListener(){},dispatchEvent(e){this.events.push(e);}};
  const storage={getItem:()=>null,setItem(){}};
  let game;
  const instrumented = source.replace('  requestAnimationFrame(frame);\n})();', '  requestAnimationFrame(frame);\n  expose({reset,action,down,rotate,lock,take,fits,togglePause,frame,get:()=>({grid,piece,next,score,lines,running,paused,bag}),set:(s)=>{if(s.grid)grid=s.grid;if(s.piece)piece=s.piece;if(s.lines!==undefined)lines=s.lines;}});\n})();');
  new Function('document','window','localStorage','requestAnimationFrame','Event','CustomEvent','expose',instrumented)(document,window,storage,()=>{},class {constructor(type){this.type=type;}},class {constructor(type,init){this.type=type;this.detail=init.detail;}},value=>{game=value;});
  return {game,elements,window};
}

const {game,elements,window}=harness(source);
const assert=(condition,message)=>{if(!condition)throw new Error(message);};
game.reset();assert(game.get().running,'starts running');assert(game.get().grid.length===20,'20 rows');
game.action('pause');const x=game.get().piece.x;game.action('left');assert(game.get().piece.x===x,'paused input ignored');game.action('pause');
const bag=Array.from({length:7},()=>JSON.stringify(game.take())); // a fresh bag verified separately below
game.reset();const sequence=[JSON.stringify(game.get().piece.m),JSON.stringify(game.get().next),...Array.from({length:5},()=>JSON.stringify(game.take()))];
assert(new Set(sequence).size===7,'seven bag contains each piece exactly once');
const grid=Array.from({length:20},()=>Array(10).fill(0));grid[19]=Array(10).fill(1);grid[19][4]=0;
game.set({grid,piece:{m:[[1]],x:4,y:19}});game.lock();
assert(game.get().lines===1 && game.get().score===100,'single line clears and scores');
const four=Array.from({length:20},()=>Array(10).fill(0));for(let y=16;y<20;y++){four[y]=Array(10).fill(1);four[y][4]=0;}
game.set({grid:four,piece:{m:[[1],[1],[1],[1]],x:4,y:16},lines:9});game.lock();
assert(game.get().lines===13 && game.get().score===900,'four line clear at pre-clear level');assert(elements.level.textContent===2,'level advances after ten lines');
game.reset();game.action('drop');assert(game.get().score>0,'hard drop scores');assert(game.get().grid.some(row=>row.some(Boolean)),'hard drop locks');
game.set({piece:{m:[[1],[1],[1],[1]],x:9,y:0}});game.rotate(1);assert(game.fits(game.get().piece.m,game.get().piece.x,game.get().piece.y),'wall kick remains in bounds');
const full=Array.from({length:20},()=>Array(10).fill(1));game.set({grid:full,piece:{m:[[1]],x:0,y:-1}});game.lock();assert(!game.get().running,'top out ends round');assert(window.events.some(e=>e.type==='blocks:over'),'score event on top out');
game.reset();assert(game.get().score===0&&game.get().lines===0&&game.get().running,'restart resets score and board');

console.log('Gameplay checks passed');
(async () => {
  const {webcrypto}=require('node:crypto');
  const apiSource=fs.readFileSync('functions/api/blocks.js','utf8').replace('export async function','async function');
  const api=new Function('crypto',apiSource+';return onRequest;')(webcrypto);
  const assert=(v,m)=>{if(!v)throw new Error(m);};
  let used=false, inserted=0, rateLimited=false;
  const db={
    prepare(sql){return {args:[],bind(...args){this.args=args;return this;},
      async all(){return {results:[{name:'Kiwi',score:100,lines:1}]};},
      async first(){return {created:Math.floor(Date.now()/1000)-60,used:used?1:0};},
      async run(){return {meta:{changes:sql.startsWith('INSERT')?(rateLimited?0:1):0}};}
    };},
    async batch(statements){if(used)return [{meta:{changes:0}}];used=true;inserted++;return [{meta:{changes:1}}];}
  };
  const req=(body,origin='https://example.com')=>new Request('https://example.com/api/blocks',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:JSON.stringify(body)});
  const call=(request,env={BLOCKS_DB:db})=>api({request,env});
  assert((await call(new Request('https://example.com/api/blocks'),{})).status===503,'missing DB graceful');
  assert((await call(new Request('https://example.com/api/blocks'))).status===200,'read scoreboard');
  assert((await call(req({action:'start'},'https://evil.example'))).status===403,'reject cross origin');
  assert((await call(req({action:'start'}))).status===201,'issue session');
  rateLimited=true;assert((await call(req({action:'start'}))).status===429,'enforce start rate');rateLimited=false;
  assert((await call(req({name:'x'.repeat(2000)}))).status===413,'bound streamed body');
  const good={token:'12345678-1234-1234-1234-123456789abc',name:'Kiwi',score:100,lines:1};
  assert((await call(req({...good,name:'<script>'}))).status===400,'reject unsafe nickname');
  assert((await call(req({...good,score:-1}))).status===400,'reject negative score');
  assert((await call(req({...good,score:9000000}))).status===400,'reject implausible score');
  assert((await call(req(good))).status===201,'save valid score');
  assert((await call(req(good))).status===400 && inserted===1,'reject replay');
  console.log('Leaderboard API checks passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
