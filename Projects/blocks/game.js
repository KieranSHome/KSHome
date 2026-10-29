'use strict';
(() => {
  const board = document.getElementById('board'), ctx = board.getContext('2d');
  const preview = document.getElementById('next'), pc = preview.getContext('2d');
  const status = document.getElementById('status'), start = document.getElementById('start'), pause = document.getElementById('pause');
  const shapes = [[[1,1,1,1]],[[2,2],[2,2]],[[0,3,0],[3,3,3]],[[0,4,4],[4,4,0]],[[5,5,0],[0,5,5]],[[6,0,0],[6,6,6]],[[0,0,7],[7,7,7]]];
  const colors = ['', '#77d9c0','#e6c85a','#bfa8ed','#9bd36a','#e8a58d','#81b7ee','#f0af68'];
  let grid, piece, next, bag = [], score = 0, lines = 0, best = 0, running = false, paused = false, elapsed = 0, last = 0;
  try { best = Math.max(0, Number(localStorage.getItem('kiwiii-blocks-best')) || 0); } catch {}
  const level = () => 1 + Math.floor(lines / 10);
  function take() {
    if (!bag.length) {
      bag = shapes.map((_, i) => i);
      for (let i = bag.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [bag[i], bag[j]] = [bag[j], bag[i]]; }
    }
    return shapes[bag.pop()].map(row => row.slice());
  }
  function fits(m, x, y) {
    return m.every((row, dy) => row.every((v, dx) => !v || (x+dx >= 0 && x+dx < 10 && y+dy < 20 && (y+dy < 0 || !grid[y+dy][x+dx]))));
  }
  function spawn() {
    piece = {m: next, x: 0, y: 0}; piece.x = Math.floor((10-piece.m[0].length)/2);
    next = take();
    if (!fits(piece.m, piece.x, piece.y)) {
      running = false; window.dispatchEvent(new CustomEvent('blocks:over',{detail:{score,lines}})); pause.disabled = true; status.textContent = 'Game over · score ' + score + '. Start a new game to try again.';
    }
  }
  function update() {
    if (score > best) { best = score; try { localStorage.setItem('kiwiii-blocks-best', String(best)); } catch {} }
    for (const [id, value] of Object.entries({score, lines, level:level(), best})) document.getElementById(id).textContent = value;
  }
  function reset() {
    grid = Array.from({length:20}, () => Array(10).fill(0)); bag = []; score = lines = elapsed = 0;
    next = take(); running = true; paused = false; pause.disabled = false; pause.textContent = 'Pause';
    start.textContent = 'Restart'; status.textContent = 'Playing · clear full rows to grow your score.';
    window.dispatchEvent(new Event('blocks:start')); spawn(); update(); draw(); board.focus();
  }
  function lock() {
    let above = false;
    piece.m.forEach((row,dy) => row.forEach((v,dx) => { if(v) { if(piece.y+dy < 0) above = true; else grid[piece.y+dy][piece.x+dx] = v; } }));
    if (above) { running = false; window.dispatchEvent(new CustomEvent('blocks:over',{detail:{score,lines}})); pause.disabled = true; status.textContent = 'Game over · start a new game to try again.'; return; }
    const kept = grid.filter(row => row.some(v => !v)), count = 20-kept.length;
    score += [0,100,300,500,800][count]*level(); lines += count;
    grid = [...Array.from({length:count}, () => Array(10).fill(0)), ...kept];
    elapsed = 0; spawn(); update();
  }
  function down(manual = false) {
    if(fits(piece.m,piece.x,piece.y+1)) { piece.y++; if(manual) {score++; update();} } else lock();
  }
  function rotate(direction) {
    const m = direction > 0 ? piece.m[0].map((_,i) => piece.m.map(row => row[i]).reverse()) : piece.m[0].map((_,i) => piece.m.map(row => row[row.length-1-i]));
    for(const dx of [0,-1,1,-2,2]) if(fits(m,piece.x+dx,piece.y)) { piece.m=m; piece.x+=dx; break; }
  }
  function togglePause() {
    if(!running) return;
    paused = !paused; elapsed = 0; pause.textContent = paused ? 'Resume' : 'Pause';
    status.textContent = paused ? 'Paused · resume when you are ready.' : 'Playing · clear full rows to grow your score.'; draw();
  }
  function action(name) {
    if(name === 'pause') { togglePause(); return; }
    if(!running || paused) return;
    if(name === 'left' && fits(piece.m,piece.x-1,piece.y)) piece.x--;
    if(name === 'right' && fits(piece.m,piece.x+1,piece.y)) piece.x++;
    if(name === 'down') down(true);
    if(name === 'rotate') rotate(1);
    if(name === 'counter') rotate(-1);
    if(name === 'drop') { while(fits(piece.m,piece.x,piece.y+1)) {piece.y++; score+=2;} lock(); }
    draw();
  }
  function cell(context,x,y,v,size,ghost=false) {
    context.fillStyle = ghost ? '#355148' : colors[v];
    context.fillRect(x*size+1,y*size+1,size-2,size-2);
    context.strokeStyle = ghost ? '#9bd36a' : '#ffffff50';
    context.strokeRect(x*size+3,y*size+3,size-6,size-6);
  }
  function draw() {
    ctx.fillStyle='#0c1716'; ctx.fillRect(0,0,300,600);
    ctx.strokeStyle='#1d302b';
    for(let x=0;x<=300;x+=30) {ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,600);ctx.stroke();}
    for(let y=0;y<=600;y+=30) {ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(300,y);ctx.stroke();}
    grid.forEach((row,y) => row.forEach((v,x) => {if(v) cell(ctx,x,y,v,30);}));
    if(piece && running && !paused) {
      let gy = piece.y; while(fits(piece.m,piece.x,gy+1)) gy++;
      piece.m.forEach((row,y) => row.forEach((v,x) => {if(v) cell(ctx,x+piece.x,y+gy,v,30,true);}));
      piece.m.forEach((row,y) => row.forEach((v,x) => {if(v) cell(ctx,x+piece.x,y+piece.y,v,30);}));
    }
    if(!running || paused) {
      ctx.fillStyle='#0c1716cc';ctx.fillRect(0,0,300,600);
      ctx.fillStyle='#edf5df';ctx.textAlign='center';ctx.font='bold 22px system-ui';
      ctx.fillText(paused ? 'PAUSED' : piece ? 'GAME OVER' : 'READY TO GROW?',150,285);
      ctx.font='14px system-ui';ctx.fillText(paused ? 'Press P or Resume' : 'Press Start to play',150,315);
    }
    pc.clearRect(0,0,120,100);
    if(next) next.forEach((row,y) => row.forEach((v,x) => {if(v) cell(pc,x+(4-row.length)/2,y+0.5,v,25);}));
  }
  start.addEventListener('click', reset); pause.addEventListener('click', togglePause);
  board.addEventListener('keydown', e => {
    const keys = {ArrowLeft:'left',ArrowRight:'right',ArrowDown:'down',ArrowUp:'rotate',x:'rotate',z:'counter',' ':'drop',p:'pause',Escape:'pause'};
    const name=keys[e.key] || keys[e.key.toLowerCase()]; if(!name) return;
    e.preventDefault(); if(e.repeat && ['drop','rotate','counter','pause'].includes(name)) return; action(name);
  });
  document.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', () => action(button.dataset.action)));
  window.addEventListener('blur', () => {if(running && !paused) togglePause();});
  document.addEventListener('visibilitychange', () => {if(document.hidden && running && !paused) togglePause();});
  grid=Array.from({length:20}, () => Array(10).fill(0)); update(); draw();
  function frame(time) {
    const delta = last ? Math.min(time-last,100) : 0; last=time;
    if(running && !paused) { elapsed += delta; if(elapsed >= Math.max(90,850*Math.pow(.8,level()-1))) {elapsed=0;down();draw();} }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
