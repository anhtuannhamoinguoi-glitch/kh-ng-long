import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DINO RUN: Lost World",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    .stApp { background: #101820; color: #f6f0d8; }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1100px; padding-top: 1.2rem; padding-bottom: 1rem; }
    h1 { font-family: 'Press Start 2P', monospace !important; color: #f7d774 !important; font-size: clamp(1.2rem, 3vw, 2rem) !important; line-height: 1.6 !important; }
    .intro { color: #c8d5c4; margin-bottom: .6rem; }
    div[data-testid="stMarkdownContainer"] p { color: #d8e2d0; }
    .stAlert { background: #1a2b30; }
</style>
""", unsafe_allow_html=True)

st.title("DINO RUN")
st.markdown('<div class="intro">LOST WORLD • Chạy, nhảy và sống sót giữa vùng đất tiền sử.</div>', unsafe_allow_html=True)

game_html = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; background:#101820; color:#f6f0d8; font-family:monospace; }
  #wrap { width:100%; max-width:1000px; margin:0 auto; }
  #hud { display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; padding:10px 12px; background:#1a2b30; border:3px solid #344b45; border-bottom:0; font-weight:bold; letter-spacing:1px; }
  .stat { color:#f7d774; }
  canvas { display:block; width:100%; height:auto; image-rendering:pixelated; border:3px solid #344b45; background:#f5c56b; touch-action:manipulation; }
  #controls { display:flex; justify-content:center; gap:10px; padding:12px 0 2px; flex-wrap:wrap; }
  button { font-family:monospace; font-weight:bold; font-size:14px; color:#f6f0d8; background:#2c493f; border:3px solid #67835c; border-bottom-width:5px; padding:12px 18px; cursor:pointer; touch-action:manipulation; }
  button:active { transform:translateY(2px); border-bottom-width:3px; }
  #hint { text-align:center; color:#c8d5c4; font-size:12px; line-height:1.7; padding:8px 4px 12px; }
  @media (max-width:600px) { #hud { font-size:12px; } button { flex:1; padding:12px 8px; } }
</style>
</head>
<body>
<div id="wrap">
  <div id="hud">
    <span>ĐIỂM: <span id="score" class="stat">00000</span></span>
    <span>KỶ LỤC: <span id="best" class="stat">00000</span></span>
    <span>ĐỘ KHÓ: <span id="difficulty" class="stat">BÌNH THƯỜNG</span></span>
    <span>TỐC ĐỘ: <span id="speed" class="stat">1.0x</span></span>
    <span>HỆ SỐ ĐIỂM: <span id="multiplier" class="stat">1.0x</span></span>
  </div>
  <div id="difficultyBar" style="display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap;padding:10px;background:#142329;border:3px solid #344b45;border-bottom:0;">
    <label for="difficultySelect" style="font-weight:bold;color:#c8d5c4;">CHỌN ĐỘ KHÓ:</label>
    <select id="difficultySelect" style="font: bold 14px monospace;color:#f6f0d8;background:#2c493f;border:2px solid #67835c;padding:8px;">
      <option value="easy">DỄ — 0.75x</option>
      <option value="normal" selected>BÌNH THƯỜNG — 1.0x</option>
      <option value="hard">KHÓ — 1.5x</option>
      <option value="extreme">ÁC MỘNG — 2.0x</option>
    </select>
    <span style="font-size:12px;color:#c8d5c4;">Đổi độ khó trước khi bắt đầu hoặc khi chơi lại.</span>
  </div>
  <canvas id="game" width="960" height="400" aria-label="Trò chơi khủng long chạy vô tận"></canvas>
  <div id="controls">
    <button id="startBtn">▶ BẮT ĐẦU / CHƠI LẠI</button>
    <button id="jumpBtn">⬆ NHẢY</button>
    <button id="pauseBtn">Ⅱ TẠM DỪNG</button>
    <button id="soundBtn" aria-pressed="true">🔊 ÂM THANH: BẬT</button>
  </div>
  <div id="hint">Bật âm thanh bằng nút 🔊. Âm thanh sẽ hoạt động sau lần bấm đầu tiên vào game.<br>Bàn phím: SPACE / ↑ để nhảy · P để tạm dừng · Enter để bắt đầu lại<br>Trên điện thoại: chạm nút NHẢY hoặc chạm vào khu vực trò chơi.</div>
</div>
<script>
(() => {
  "use strict";
  const canvas = document.getElementById("game");
  const ctx = canvas.getContext("2d");
  const scoreEl = document.getElementById("score");
  const bestEl = document.getElementById("best");
  const speedEl = document.getElementById("speed");
  const difficultyEl = document.getElementById("difficulty");
  const multiplierEl = document.getElementById("multiplier");
  const difficultySelect = document.getElementById("difficultySelect");
  const startBtn = document.getElementById("startBtn");
  const jumpBtn = document.getElementById("jumpBtn");
  const pauseBtn = document.getElementById("pauseBtn");
  const soundBtn = document.getElementById("soundBtn");
  const W = canvas.width, H = canvas.height, groundY = 318;

  // Âm thanh được tạo trực tiếp bằng Web Audio API, không cần tải file MP3.
  let audioCtx = null;
  let soundEnabled = true;
  let lastMilestone = 0;
  function initAudio() {
    if (!soundEnabled) return false;
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) return false;
      if (!audioCtx) audioCtx = new AudioContextClass();
      if (audioCtx.state === "suspended") audioCtx.resume();
      return true;
    } catch (_) { return false; }
  }
  function tone(freq, duration, type="square", volume=0.045, endFreq=null, delay=0) {
    if (!initAudio()) return;
    const startAt = audioCtx.currentTime + delay;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(Math.max(1, freq), startAt);
    if (endFreq !== null) osc.frequency.exponentialRampToValueAtTime(Math.max(1, endFreq), startAt + duration);
    gain.gain.setValueAtTime(0.0001, startAt);
    gain.gain.exponentialRampToValueAtTime(Math.max(0.0002, volume), startAt + 0.012);
    gain.gain.exponentialRampToValueAtTime(0.0001, startAt + duration);
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.start(startAt); osc.stop(startAt + duration + 0.025);
  }
  function playSound(name) {
    if (!soundEnabled) return;
    if (name === "jump") {
      tone(360, 0.11, "square", 0.035, 620);
      tone(620, 0.09, "triangle", 0.022, 780, 0.045);
    } else if (name === "land") {
      tone(125, 0.055, "triangle", 0.018, 75);
    } else if (name === "hit") {
      tone(190, 0.20, "sawtooth", 0.055, 48);
      tone(95, 0.28, "square", 0.035, 38, 0.07);
    } else if (name === "start") {
      tone(440, 0.08, "square", 0.025, 550);
      tone(660, 0.12, "square", 0.03, 880, 0.09);
    } else if (name === "pause") {
      tone(500, 0.08, "triangle", 0.025, 300);
    } else if (name === "milestone") {
      tone(660, 0.07, "square", 0.025, 740);
      tone(880, 0.12, "square", 0.028, 1100, 0.075);
    }
  }
  soundBtn.addEventListener("click", () => {
    soundEnabled = !soundEnabled;
    soundBtn.textContent = soundEnabled ? "🔊 ÂM THANH: BẬT" : "🔇 ÂM THANH: TẮT";
    soundBtn.setAttribute("aria-pressed", String(soundEnabled));
    if (soundEnabled) { initAudio(); playSound("start"); }
  });
  let state = "ready"; // ready, running, paused, over
  let lastTime = 0, elapsed = 0, score = 0, speed = 6, spawnTimer = 0, cloudTimer = 0;
  let obstacles = [], particles = [], clouds = [], ambientDust = [];
  let screenShake = 0;
  const difficultySettings = {
    easy:    {label:"DỄ", base:0.75, growth:0.0009, max:1.8, scoreRate:10},
    normal:  {label:"BÌNH THƯỜNG", base:1.0, growth:0.0015, max:2.5, scoreRate:10},
    hard:    {label:"KHÓ", base:1.5, growth:0.0020, max:3.2, scoreRate:12},
    extreme: {label:"ÁC MỘNG", base:2.0, growth:0.0025, max:4.0, scoreRate:14}
  };
  let difficultyKey = difficultySelect.value;
  let difficulty = difficultySettings[difficultyKey];
  let best = 0;
  try { best = Number(localStorage.getItem("dinoRunBest") || 0) || 0; } catch (_) {}
  bestEl.textContent = String(best).padStart(5, "0");

  const dino = { x: 112, y: groundY - 52, w: 48, h: 52, vy: 0, onGround: true, duck: false, anim: 0, squash: 1, blink: 0, trail: 0 };
  const rand = (a,b) => a + Math.random() * (b-a);

  function reset() {
    difficultyKey = difficultySelect.value;
    difficulty = difficultySettings[difficultyKey];
    state = "running"; elapsed = 0; score = 0; speed = 6 * difficulty.base; spawnTimer = 0.85;
    lastMilestone = 0;
    obstacles = []; particles = []; clouds = [];
    initAudio(); playSound("start");
    difficultyEl.textContent = difficulty.label;
    multiplierEl.textContent = difficulty.base.toFixed(1) + "x";
    dino.y = groundY - dino.h; dino.vy = 0; dino.onGround = true; dino.duck = false; dino.anim = 0;
    for (let i=0;i<5;i++) clouds.push({x:rand(0,W), y:rand(35,135), s:rand(.7,1.5)});
    lastTime = performance.now();
  }
  function jump() {
    if (state === "ready" || state === "over") { reset(); return; }
    if (state !== "running") return;
    if (dino.onGround) { dino.vy = -14.5; dino.onGround = false; puff(dino.x+8, groundY-2, 7, "#e8a65b"); playSound("jump"); }
  }
  function togglePause() {
    if (state === "running") { state = "paused"; playSound("pause"); }
    else if (state === "paused") { state = "running"; lastTime = performance.now(); playSound("start"); }
  }
  function puff(x,y,n,color) {
    for(let i=0;i<n;i++) particles.push({x,y,vx:rand(-2,2),vy:rand(-3,0),life:rand(.2,.6),max:.6,color,size:rand(2,5)});
  }
  function rect(x,y,w,h,c) { ctx.fillStyle=c; ctx.fillRect(Math.round(x),Math.round(y),Math.round(w),Math.round(h)); }
  function drawCloud(c) {
    const x=c.x, y=c.y, s=c.s;
    rect(x,y+8*s,34*s,10*s,"#fff0c4"); rect(x+7*s,y,15*s,12*s,"#fff0c4");
    rect(x+19*s,y+3*s,14*s,12*s,"#fff0c4"); rect(x+4*s,y+13*s,32*s,5*s,"#f7dca0");
  }
  function drawBackground(dt) {
    const night = Math.min(1, Math.max(0, (score-450)/900));
    const top = [245,197,107], bottom = [255,230,165], darkTop=[30,48,70], darkBottom=[73,91,91];
    const mix=(a,b,t)=>a+(b-a)*t;
    const rgb=(a,b,t)=>`rgb(${mix(a[0],b[0],t)},${mix(a[1],b[1],t)},${mix(a[2],b[2],t)})`;
    const grad=ctx.createLinearGradient(0,0,0,H);
    grad.addColorStop(0,rgb(top,darkTop,night)); grad.addColorStop(1,rgb(bottom,darkBottom,night));
    ctx.fillStyle=grad; ctx.fillRect(0,0,W,H);
    // sun / moon
    if(night < .65) { rect(765,55,46,46,"#ffe59a"); rect(775,45,26,10,"#ffe59a"); }
    else { rect(765,55,38,38,"#e7f0dc"); rect(785,48,25,38,rgb(top,darkTop,night)); }
    // far parallax ridge
    ctx.fillStyle = night > .5 ? "#293f4b" : "#e8ac63";
    ctx.beginPath(); ctx.moveTo(0,230); ctx.lineTo(90,195); ctx.lineTo(160,222); ctx.lineTo(265,185); ctx.lineTo(360,230); ctx.lineTo(485,192); ctx.lineTo(600,230); ctx.lineTo(745,188); ctx.lineTo(850,225); ctx.lineTo(960,195); ctx.lineTo(960,groundY); ctx.lineTo(0,groundY); ctx.fill();
    // distant mountains
    ctx.fillStyle = night > .5 ? "#40545a" : "#d69b57";
    ctx.beginPath(); ctx.moveTo(0,250); ctx.lineTo(105,155); ctx.lineTo(185,235); ctx.lineTo(310,145); ctx.lineTo(435,250); ctx.lineTo(555,180); ctx.lineTo(680,250); ctx.lineTo(820,165); ctx.lineTo(960,250); ctx.lineTo(960,groundY); ctx.lineTo(0,groundY); ctx.fill();
    ctx.fillStyle = night > .5 ? "#344b50" : "#c9874c";
    ctx.beginPath(); ctx.moveTo(0,275); ctx.lineTo(180,220); ctx.lineTo(330,275); ctx.lineTo(500,215); ctx.lineTo(680,275); ctx.lineTo(830,220); ctx.lineTo(960,270); ctx.lineTo(960,groundY); ctx.lineTo(0,groundY); ctx.fill();
    clouds.forEach(c => drawCloud(c));
    // ground
    rect(0,groundY,W,H-groundY, night>.5 ? "#6c6650" : "#e6b66c");
    rect(0,groundY,W,5, night>.5 ? "#c1b17b" : "#805d3d");
    const offset = (elapsed*speed*1.7)%80;
    for(let x=-offset;x<W;x+=80) {
      rect(x,groundY+17,28,4,night>.5?"#514f42":"#c48a4d");
      rect(x+35,groundY+37,13,3,night>.5?"#514f42":"#c48a4d");
    }
    // tiny desert plants
    for(let i=0;i<8;i++) {
      const x=((i*137 - elapsed*speed*.38)% (W+80)+W+80)%(W+80);
      rect(x,groundY-9,3,9,night>.5?"#526b4c":"#638047");
      rect(x-4,groundY-6,4,3,night>.5?"#526b4c":"#638047");
    }
    // moving dust motes near the ground add a sense of speed
    ambientDust.forEach(p=>{
      p.x -= speed*0.42*p.s;
      if(p.x<0){p.x=W+rand(0,80);p.y=rand(groundY+4,H-5);}
      ctx.globalAlpha=p.a;
      rect(p.x,p.y,p.s,p.s,night>.5?"#e4d9a3":"#fff0c4");
    });
    ctx.globalAlpha=1;
  }
  function drawDino() {
    const run=Math.floor(dino.anim/6)%2;
    const airborne=!dino.onGround;
    const stretch=airborne?1.05:dino.squash;
    const bob=(!airborne && run===0)?1:0;
    const x=dino.x, y=dino.y + bob;
    ctx.save();
    // Soft pixel shadow changes size while jumping.
    ctx.globalAlpha=airborne?.18:.28;
    rect(x-1,groundY-3,48*(airborne?.72:1),4,"#29352d");
    ctx.globalAlpha=1;
    // squash/stretch around feet to make the jump feel less rigid
    ctx.translate(x+24, y+52);
    ctx.scale(1/stretch, stretch);
    ctx.translate(-(x+24), -(y+52));
    const green="#36784b", light="#70b85e", shade="#214c3c", cream="#e8d99d", highlight="#9bd16b";
    // tail with two-tone tip
    rect(x+2,y+27,13,9,shade); rect(x-5,y+24,10,7,green); rect(x-8,y+25,5,4,highlight);
    // torso and back
    rect(x+8,y+18,27,25,green); rect(x+12,y+20,19,18,light); rect(x+13,y+34,16,6,cream);
    // neck, head, muzzle
    rect(x+24,y+10,13,19,light); rect(x+26,y+2,21,19,green); rect(x+37,y+14,16,8,green);
    rect(x+39,y+19,13,5,shade); rect(x+43,y+17,7,3,highlight);
    // back spikes
    rect(x+8,y+13,7,7,light); rect(x+16,y+10,7,7,highlight); rect(x+24,y+8,7,6,light);
    // nostril and expressive eye
    rect(x+49,y+16,2,2,shade);
    if (dino.blink>0) rect(x+39,y+7,5,2,cream);
    else { rect(x+39,y+5,6,6,cream); rect(x+42,y+7,3,3,"#172321"); rect(x+42,y+7,1,1,"#ffffff"); }
    // tiny arm
    rect(x+34,y+25,7,3,shade); rect(x+39,y+26,4,3,light);
    // alternating legs with feet and toes
    if(airborne) {
      rect(x+12,y+40,7,10,shade); rect(x+27,y+40,7,8,shade);
      rect(x+7,y+49,14,4,green); rect(x+25,y+47,13,4,green);
    } else if(run===0) {
      rect(x+12,y+40,7,10,shade); rect(x+25,y+40,7,7,shade);
      rect(x+7,y+48,15,4,green); rect(x+23,y+45,14,4,green);
      rect(x+8,y+51,4,2,highlight);
    } else {
      rect(x+13,y+40,7,7,shade); rect(x+27,y+40,7,10,shade);
      rect(x+8,y+45,14,4,green); rect(x+25,y+48,15,4,green);
      rect(x+35,y+51,4,2,highlight);
    }
    ctx.restore();
    // speed streaks at high speed
    if(speed/6>1.45 && state==="running" && Math.floor(dino.anim)%3===0) {
      ctx.globalAlpha=.45; rect(x-15,y+20,10,2,"#fff0c4"); rect(x-21,y+29,7,2,"#fff0c4"); ctx.globalAlpha=1;
    }
  }
  function spawnObstacle() {
    const bird = score > 80 && Math.random() < Math.min(.55, .28 + score/1800);
    if (bird) {
      obstacles.push({type:"bird",x:W+20,y:rand(225,270),w:38,h:25,frame:0});
    } else {
      const tall = Math.random() < .3;
      obstacles.push({type:"cactus",x:W+20,y:groundY-(tall?56:38),w:tall?28:22,h:tall?56:38,tall});
    }
  }
  function drawObstacle(o) {
    if(o.type==="bird") {
      const wing=Math.floor(o.frame/8)%2;
      // Chim pixel-art có đuôi, lông cánh và hoạt ảnh vỗ cánh.
      rect(o.x+7,o.y+9,23,10,"#3b3838"); rect(o.x+25,o.y+5,10,10,"#3b3838");
      rect(o.x+33,o.y+8,9,4,"#e59a42"); rect(o.x+28,o.y+7,3,3,"#fff0bd");
      rect(o.x+29,o.y+8,1,1,"#1b2524");
      rect(o.x+3,o.y+10,7,5,"#66564b"); rect(o.x+1,o.y+8,4,4,"#8b715c");
      if (wing) {
        rect(o.x+11,o.y+1,7,8,"#66564b"); rect(o.x+16,o.y-4,8,8,"#66564b");
        rect(o.x+18,o.y-7,6,5,"#8b715c");
      } else {
        rect(o.x+11,o.y+17,8,7,"#66564b"); rect(o.x+17,o.y+20,8,4,"#66564b");
        rect(o.x+19,o.y+23,6,3,"#8b715c");
      }
      rect(o.x+8,o.y+12,6,4,"#786254");
    } else {
      rect(o.x+7,o.y,10,o.h,"#477744"); rect(o.x+2,o.y+12,8,5,"#477744");
      rect(o.x+2,o.y+7,5,12,"#477744"); rect(o.x+15,o.y+20,10,5,"#477744");
      rect(o.x+20,o.y+14,5,13,"#477744"); rect(o.x+4,o.y+o.h-5,o.w+3,5,"#2e5d3c");
      rect(o.x+9,o.y+4,3,Math.max(5,o.h-12),"#72a45b");
    }
  }
  function intersects(a,b) {
    const pad=7;
    return a.x+pad < b.x+b.w-pad && a.x+a.w-pad > b.x+pad &&
           a.y+pad < b.y+b.h-pad && a.y+a.h-pad > b.y+pad;
  }
  function update(dt) {
    if(state!=="running") return;
    elapsed += dt;
    // Tốc độ ảnh hưởng trực tiếp đến tốc độ cộng điểm.
    const speedMultiplier = speed / 6;
    score += dt * difficulty.scoreRate * speedMultiplier;
    speed = Math.min(6 * difficulty.max, 6 * difficulty.base + score * difficulty.growth);
    dino.anim += dt*22*(speed/6);
    dino.squash += ((dino.onGround ? 1 + Math.sin(dino.anim*0.45)*0.035 : 1.05) - dino.squash) * Math.min(1,dt*12);
    dino.blink = (Math.sin(elapsed*1.7)>0.995) ? 0.08 : Math.max(0,dino.blink-dt);
    dino.trail += dt;
    dino.vy += 36*dt;
    dino.y += dino.vy;
    if(dino.y >= groundY-dino.h) {
      if(!dino.onGround && dino.vy>4) { puff(dino.x+20,groundY-2,5,"#d9a25e"); dino.squash=.9; playSound("land"); }
      dino.y=groundY-dino.h; dino.vy=0; dino.onGround=true;
    }
    spawnTimer -= dt;
    if(spawnTimer<=0) { spawnObstacle(); spawnTimer=rand(.9,1.55)*Math.max(.62,7/speed); }
    obstacles.forEach(o=>{ o.x -= speed*60*dt; o.frame+=dt*25; });
    obstacles = obstacles.filter(o=>o.x+o.w>-10);
    const hitbox={x:dino.x+4,y:dino.y+4,w:dino.w-8,h:dino.h-6};
    for(const o of obstacles) {
      const box={x:o.x,y:o.y,w:o.w,h:o.h};
      if(intersects(hitbox,box)) {
        state="over";
        screenShake=0.22;
        playSound("hit");
        puff(dino.x+24,dino.y+28,24,"#d77b45");
        if(Math.floor(score)>best) {
          best=Math.floor(score);
          try { localStorage.setItem("dinoRunBest",String(best)); } catch (_) {}
        }
        bestEl.textContent=String(best).padStart(5,"0");
        break;
      }
    }
    cloudTimer += dt;
    clouds.forEach(c=>c.x-=speed*.12*c.s);
    clouds=clouds.filter(c=>c.x>-70);
    if(clouds.length<5 && cloudTimer>.8) { clouds.push({x:W+20,y:rand(35,135),s:rand(.7,1.5)}); cloudTimer=0; }
    particles.forEach(p=>{p.x+=p.vx*60*dt;p.y+=p.vy*60*dt;p.vy+=.12;p.life-=dt;});
    particles=particles.filter(p=>p.life>0);
    scoreEl.textContent=String(Math.floor(score)).padStart(5,"0");
    const milestone = Math.floor(score / 100) * 100;
    if (milestone >= 100 && milestone > lastMilestone) {
      lastMilestone = milestone;
      playSound("milestone");
    }
    speedEl.textContent=(speed/6).toFixed(1)+"x";
    multiplierEl.textContent=(speed/6).toFixed(1)+"x";
  }
  function overlay(title, lines) {
    ctx.fillStyle="rgba(16,24,32,.66)"; ctx.fillRect(0,0,W,H);
    ctx.textAlign="center";
    ctx.fillStyle="#f7d774"; ctx.font="bold 30px monospace"; ctx.fillText(title,W/2,155);
    ctx.fillStyle="#fff0c4"; ctx.font="bold 16px monospace";
    lines.forEach((line,i)=>ctx.fillText(line,W/2,198+i*29));
  }
  function render(dt) {
    if(screenShake>0) screenShake=Math.max(0,screenShake-dt);
    ctx.save();
    if(screenShake>0) ctx.translate(rand(-5,5),rand(-3,3));
    drawBackground(dt);
    // distant pixel stars at night
    if(score>450) {
      ctx.fillStyle="#f8edc1";
      for(let i=0;i<28;i++) { const x=(i*83+17)%W, y=(i*47+13)%145; ctx.fillRect(x,y,2,2); }
    }
    obstacles.forEach(drawObstacle);
    drawDino();
    particles.forEach(p=>{ctx.globalAlpha=Math.max(0,p.life/p.max);rect(p.x,p.y,p.size,p.size,p.color);});
    ctx.globalAlpha=1;
    if(state==="ready") overlay("DINO RUN",["NHẤN BẮT ĐẦU ĐỂ CHƠI","SPACE / ↑ ĐỂ NHẢY"]);
    else if(state==="paused") overlay("TẠM DỪNG",["Nhấn P hoặc nút tiếp tục"]);
    else if(state==="over") overlay("GAME OVER",["Điểm: "+Math.floor(score),"Nhấn BẮT ĐẦU ĐỂ THỬ LẠI"]);
    ctx.restore();
  }
  function frame(now) {
    const dt=Math.min(.035,Math.max(0,(now-lastTime)/1000 || 0));
    lastTime=now;
    update(dt);
    render(dt);
    requestAnimationFrame(frame);
  }
  difficultySelect.addEventListener("change", () => {
    const selected = difficultySettings[difficultySelect.value];
    if (state !== "running" && state !== "paused") {
      difficultyEl.textContent = selected.label;
      speedEl.textContent = selected.base.toFixed(1) + "x";
      multiplierEl.textContent = selected.base.toFixed(1) + "x";
    }
  });
  startBtn.addEventListener("click",reset);
  jumpBtn.addEventListener("click",jump);
  pauseBtn.addEventListener("click",togglePause);
  canvas.addEventListener("pointerdown",()=>{ if(state==="ready"||state==="over") reset(); else jump(); });
  window.addEventListener("keydown",e=>{
    if(["Space","ArrowUp","ArrowDown"].includes(e.code)) e.preventDefault();
    if(e.code==="Space"||e.code==="ArrowUp") { if(!e.repeat) jump(); }
    else if(e.code==="Enter") { if(state!=="running") reset(); }
    else if(e.code==="KeyP") togglePause();
  },{passive:false});
  // Prevent accidental scroll while using the jump button on touch devices.
  jumpBtn.addEventListener("touchstart",e=>e.preventDefault(),{passive:false});
  reset(); state="ready"; lastTime=performance.now(); render(0);
  requestAnimationFrame(frame);
})();
</script>
</body>
</html>
"""

components.html(game_html, height=540, scrolling=False)
st.caption("DINO RUN: LOST WORLD · Game chạy trong trình duyệt. Kỷ lục được lưu cục bộ trên trình duyệt hiện tại.")
