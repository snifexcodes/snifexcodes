// Interactive 3D portfolio — built into ../docs/index.html by build.mjs
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

// ───────────── content (edit me) ─────────────
const GH = 'https://github.com/snifexcodes';
const PROJECTS = [
  { kicker: 'Featured · Python · Computer vision', title: 'Mudra', color: '#34d399', radius: 6.8, size: 1.15, speed: 0.3, ring: true,
    desc: 'Real-time sign language to text. Watches your hand through a webcam, turns signs into live captions, and trains and compares four ML models on your recordings.',
    tags: ['Python', 'Flask', 'MediaPipe', 'scikit-learn'], url: 'https://github.com/snifexcodes/Mudra' },
  { kicker: 'Python · Scraper', title: 'Paper Analyzer', color: '#22d3ee', radius: 9, size: 1.25, speed: 0.22,
    desc: "Scrapes TMV's DSpace repository and finds exam questions that repeat across years, then builds a PDF report.",
    tags: ['Python', 'Scraping', 'PDF'], url: `${GH}?tab=repositories` },
  { kicker: 'Web App', title: 'AI Chat UI', color: '#a78bfa', radius: 12.5, size: 1.05, speed: 0.16, ring: true,
    desc: 'Single-page chat interface with built-in diagram rendering and support for multiple AI providers.',
    tags: ['HTML', 'JS', 'LLM APIs'], url: `${GH}?tab=repositories` },
  { kicker: 'Python · MCP', title: 'Binance MCP', color: '#f472b6', radius: 16, size: 1.4, speed: 0.11,
    desc: 'MCP server and trading-bot tooling for crypto futures on Binance.',
    tags: ['Python', 'MCP', 'Binance API'], url: `${GH}?tab=repositories` },
  { kicker: 'Java · Minecraft', title: 'Flashback Bridge', color: '#fbbf24', radius: 19.5, size: 0.95, speed: 0.08, ring: true,
    desc: 'Mod patch that bridges CreamyKeys audio into Flashback replays and exports.',
    tags: ['Java', 'Modding'], url: `${GH}?tab=repositories` },
];
const SKILLS = [
  ['HTML', '#e34c26'], ['CSS', '#2965f1'], ['JavaScript', '#f7df1e'], ['PHP', '#777bb4'], ['Python', '#3776ab'],
  ['Java', '#f89820'], ['MySQL', '#00a3c4'], ['Linux', '#fcc624'], ['Bash', '#4eaa25'], ['Git', '#f05032'],
];
// ─────────────────────────────────────────────

const $ = (s) => document.querySelector(s);
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const mobile = matchMedia('(max-width: 760px)').matches;

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
} catch (e) {
  $('#loader').innerHTML = `<p>Your browser can't run WebGL.<br><a href="${GH}">Visit my GitHub instead →</a></p>`;
  throw e;
}
renderer.setPixelRatio(Math.min(devicePixelRatio, mobile ? 1.5 : 2));
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
$('#stage').appendChild(renderer.domElement);

const labels = new CSS2DRenderer();
labels.setSize(innerWidth, innerHeight);
labels.domElement.className = 'labels';
$('#stage').appendChild(labels.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#04050d');
scene.fog = new THREE.FogExp2('#04050d', 0.006);
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.35;

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 600);
const HOME = new THREE.Vector3(0, 9, mobile ? 46 : 32);
camera.position.set(0, 40, 120);

const controls = new OrbitControls(camera, labels.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 8;
controls.maxDistance = 90;
controls.enablePan = false;
controls.autoRotate = !reduced;
controls.autoRotateSpeed = 0.35;
controls.maxPolarAngle = Math.PI * 0.85;

// ── lights ──
scene.add(new THREE.AmbientLight('#6b5bd6', 0.35));
const coreLight = new THREE.PointLight('#c084fc', 55, 90, 1.6);
scene.add(coreLight);
const rim = new THREE.DirectionalLight('#22d3ee', 1.2);
rim.position.set(-20, 12, -10);
scene.add(rim);

// ── helpers ──
function glowTexture(inner, outer = 'rgba(0,0,0,0)', soft = false) {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  const grd = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  grd.addColorStop(0, inner);
  if (soft) grd.addColorStop(0.35, inner.replace(/[\d.]+\)$/, (a) => `${parseFloat(a) * 0.35})`));
  grd.addColorStop(1, outer);
  g.fillStyle = grd;
  g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function planetTexture(hex) {
  const c = document.createElement('canvas');
  c.width = 512; c.height = 256;
  const g = c.getContext('2d');
  const base = new THREE.Color(hex), col = new THREE.Color();
  const seed = Math.random() * 10;
  for (let y = 0; y < 256; y++) {
    const n = Math.sin(y * 0.06 + seed + Math.sin(y * 0.023 + seed) * 3) * 0.5 + 0.5;
    col.copy(base).offsetHSL(0, 0, (n - 0.5) * 0.3);
    g.fillStyle = `#${col.getHexString()}`;
    g.fillRect(0, y, 512, 1);
  }
  for (let i = 0; i < 160; i++) {
    col.copy(base).offsetHSL(0, 0, (Math.random() - 0.5) * 0.35);
    g.fillStyle = `#${col.getHexString()}`;
    g.globalAlpha = 0.22;
    g.beginPath();
    g.ellipse(Math.random() * 512, Math.random() * 256, 4 + Math.random() * 34, 2 + Math.random() * 6, 0, 0, Math.PI * 2);
    g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}

const fresnel = (color, power = 2.6, strength = 1.4) => new THREE.ShaderMaterial({
  uniforms: { c: { value: new THREE.Color(color) }, p: { value: power }, s: { value: strength } },
  vertexShader: `varying vec3 vN; varying vec3 vV;
    void main(){ vec4 mv = modelViewMatrix * vec4(position,1.); vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform vec3 c; uniform float p; uniform float s; varying vec3 vN; varying vec3 vV;
    void main(){ float f = pow(1. - abs(dot(vN, vV)), p) * s; gl_FragColor = vec4(c * f, f); }`,
  transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
});

// ── starfield ──
{
  const n = mobile ? 2500 : 5000;
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
  const tint = [new THREE.Color('#ffffff'), new THREE.Color('#a5f3fc'), new THREE.Color('#ddd6fe'), new THREE.Color('#fbcfe8')];
  for (let i = 0; i < n; i++) {
    const r = 90 + Math.random() * 220, th = Math.random() * Math.PI * 2, ph = Math.acos(2 * Math.random() - 1);
    pos.set([r * Math.sin(ph) * Math.cos(th), r * Math.cos(ph), r * Math.sin(ph) * Math.sin(th)], i * 3);
    const c = tint[(Math.random() * tint.length) | 0];
    col.set([c.r, c.g, c.b], i * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const stars = new THREE.Points(g, new THREE.PointsMaterial({
    size: 1.1, vertexColors: true, map: glowTexture('rgba(255,255,255,1)'), transparent: true, depthWrite: false,
    blending: THREE.AdditiveBlending, fog: false,
  }));
  stars.name = 'stars';
  scene.add(stars);
}

// ── nebula sprites ──
[['rgba(139,92,246,.55)', -60, 10, -120, 140], ['rgba(34,211,238,.35)', 80, -20, -90, 110],
 ['rgba(236,72,153,.35)', 30, 40, -150, 160]].forEach(([c, x, y, z, s]) => {
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTexture(c, undefined, true), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
  sp.position.set(x, y, z);
  sp.scale.setScalar(s);
  scene.add(sp);
});

// ── core ──
const core = new THREE.Group();
scene.add(core);
const crystal = new THREE.Mesh(
  new THREE.IcosahedronGeometry(2.6, 0),
  new THREE.MeshPhysicalMaterial({
    color: '#7c3aed', metalness: 0.25, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.1,
    iridescence: 1, iridescenceIOR: 1.6, emissive: '#4c1d95', emissiveIntensity: 0.55, flatShading: true,
  }));
core.add(crystal);
const heart = new THREE.Mesh(new THREE.SphereGeometry(0.85, 32, 32), new THREE.MeshBasicMaterial({ color: '#f0abfc' }));
core.add(heart);
const cage = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(3.9, 1)),
  new THREE.LineBasicMaterial({ color: '#22d3ee', transparent: true, opacity: 0.7 }));
core.add(cage);
const aura = new THREE.Mesh(new THREE.SphereGeometry(4.6, 48, 48), fresnel('#8b5cf6', 2.4, 0.7));
core.add(aura);
const coreGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTexture('rgba(192,132,252,.45)'), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
coreGlow.scale.setScalar(11);
core.add(coreGlow);

// name label on the core
const nameEl = document.createElement('div');
nameEl.className = 'core-label';
nameEl.innerHTML = '<b>RAJ</b><span>click a planet</span>';
const nameObj = new CSS2DObject(nameEl);
nameObj.position.set(0, -5.6, 0);
core.add(nameObj);

// ── orbits + planets ──
const system = new THREE.Group();
system.rotation.x = 0.18;
scene.add(system);
const planets = [];

PROJECTS.forEach((p, i) => {
  const orbit = new THREE.Mesh(
    new THREE.TorusGeometry(p.radius, 0.025, 8, 256),
    new THREE.MeshBasicMaterial({ color: p.color, transparent: true, opacity: 0.28 }));
  orbit.rotation.x = Math.PI / 2;
  system.add(orbit);

  const pivot = new THREE.Group();
  system.add(pivot);
  const body = new THREE.Group();
  pivot.add(body);

  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(p.size, 64, 64),
    (() => { const tex = planetTexture(p.color);
      return new THREE.MeshStandardMaterial({ map: tex, emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: 0.14, roughness: 0.6, metalness: 0.05 }); })());
  mesh.userData.index = i;
  body.add(mesh);
  body.add(new THREE.Mesh(new THREE.SphereGeometry(p.size * 1.32, 48, 48), fresnel(p.color, 2.6, 0.85)));
  if (p.ring) {
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(p.size * 1.5, p.size * 2.15, 96),
      new THREE.MeshBasicMaterial({ color: p.color, transparent: true, opacity: 0.45, side: THREE.DoubleSide }));
    ring.rotation.x = Math.PI / 2.4;
    body.add(ring);
  }
  // tiny moon
  const moonPivot = new THREE.Group();
  body.add(moonPivot);
  const moon = new THREE.Mesh(new THREE.SphereGeometry(p.size * 0.22, 16, 16), new THREE.MeshBasicMaterial({ color: '#ffffff' }));
  moon.position.x = p.size * 2.6;
  moonPivot.add(moon);
  moonPivot.rotation.z = 0.5;

  const el = document.createElement('button');
  el.className = 'planet-label';
  el.style.setProperty('--c', p.color);
  el.innerHTML = `<i></i>${p.title}`;
  el.addEventListener('click', (e) => { e.stopPropagation(); focus(i); });
  ['pointerdown', 'pointerup'].forEach((ev) => el.addEventListener(ev, (e) => e.stopPropagation()));
  el.addEventListener('pointerenter', () => (hovered = i));
  el.addEventListener('pointerleave', () => (hovered = -1));
  const label = new CSS2DObject(el);
  label.position.set(0, p.size + 1.1, 0);
  body.add(label);

  planets.push({ ...p, pivot, body, mesh, moonPivot, el, angle: i * 1.7 + 0.4, scale: 1 });
});

// ── skill belt ──
const belt = new THREE.Group();
belt.rotation.x = 0.18;
scene.add(belt);
const skillCubes = SKILLS.map(([name, color], i) => {
  const m = new THREE.Mesh(
    new THREE.BoxGeometry(0.9, 0.9, 0.9),
    new THREE.MeshPhysicalMaterial({ color, emissive: color, emissiveIntensity: 0.25, roughness: 0.2, metalness: 0.1, clearcoat: 1 }));
  const a = (i / SKILLS.length) * Math.PI * 2;
  m.position.set(Math.cos(a) * 23.5, Math.sin(i * 2.1) * 0.9, Math.sin(a) * 23.5);
  m.rotation.set(Math.random() * 3, Math.random() * 3, 0);
  m.userData = { skill: name, spin: 0.4 + Math.random() * 0.6 };
  belt.add(m);
  return m;
});
{
  const n = mobile ? 220 : 420;
  const debris = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1),
    new THREE.MeshStandardMaterial({ color: '#8b5cf6', emissive: '#4c1d95', emissiveIntensity: 0.5, roughness: 0.4 }), n);
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), s = new THREE.Vector3(), v = new THREE.Vector3();
  const pal = ['#8b5cf6', '#22d3ee', '#ec4899', '#6366f1'].map((c) => new THREE.Color(c));
  for (let i = 0; i < n; i++) {
    const a = Math.random() * Math.PI * 2, r = 22 + Math.random() * 3.5;
    v.set(Math.cos(a) * r, (Math.random() - 0.5) * 1.6, Math.sin(a) * r);
    q.setFromEuler(e.set(Math.random() * 6, Math.random() * 6, 0));
    s.setScalar(0.06 + Math.random() * 0.2);
    debris.setMatrixAt(i, m4.compose(v, q, s));
    debris.setColorAt(i, pal[i % pal.length]);
  }
  belt.add(debris);
}

// ── post-processing ──
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), mobile ? 0.45 : 0.6, 0.5, 0.32);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// ── interaction ──
const ray = new THREE.Raycaster();
const pointer = new THREE.Vector2(9, 9);
let hovered = -1, focused = -1, timeScale = 1;
const tip = $('#tip');
const pickables = [...planets.map((p) => p.mesh), ...skillCubes];

labels.domElement.addEventListener('pointermove', (e) => {
  pointer.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  tip.style.transform = `translate(${e.clientX + 14}px, ${e.clientY + 14}px)`;
});
labels.domElement.addEventListener('pointerleave', () => pointer.set(9, 9));

let downAt = 0, downPos = [0, 0];
labels.domElement.addEventListener('pointerdown', (e) => { downAt = performance.now(); downPos = [e.clientX, e.clientY]; });
labels.domElement.addEventListener('pointerup', (e) => {
  const moved = Math.hypot(e.clientX - downPos[0], e.clientY - downPos[1]);
  if (performance.now() - downAt > 350 || moved > 6) return;           // that was a drag
  pointer.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  ray.setFromCamera(pointer, camera);
  const hit = ray.intersectObjects(planets.map((p) => p.mesh))[0];
  if (hit) focus(hit.object.userData.index);
  else if (focused >= 0) unfocus();
});

// camera tween
let tween = null;
function flyTo(pos, target, dur = 1.4) {
  tween = { t: 0, dur, p0: camera.position.clone(), t0: controls.target.clone(), p1: pos.clone(), t1: target.clone() };
}
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

const panel = $('#panel');
function focus(i) {
  focused = i;
  const p = planets[i];
  controls.autoRotate = false;
  const world = p.mesh.getWorldPosition(new THREE.Vector3());
  const dir = world.clone().sub(camera.position).normalize();
  const dist = p.size * (mobile ? 9 : 6.5);
  flyTo(world.clone().sub(dir.multiplyScalar(dist)).add(new THREE.Vector3(0, p.size * 1.2, 0)), world);
  $('#p-kicker').textContent = p.kicker;
  $('#p-kicker').style.color = p.color;
  $('#p-title').textContent = p.title;
  $('#p-desc').textContent = p.desc;
  $('#p-tags').innerHTML = p.tags.map((t) => `<span style="--c:${p.color}">${t}</span>`).join('');
  $('#p-link').href = p.url;
  $('#p-link').style.setProperty('--c', p.color);
  panel.classList.add('open');
  document.querySelectorAll('#dock button').forEach((b, k) => b.classList.toggle('on', k === i));
}
function unfocus() {
  focused = -1;
  panel.classList.remove('open');
  flyTo(HOME, new THREE.Vector3(0, 0, 0));
  controls.autoRotate = !reduced;
  document.querySelectorAll('#dock button').forEach((b) => b.classList.remove('on'));
}
$('#p-close').addEventListener('click', unfocus);
addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && focused >= 0) unfocus();
  if (e.key === 'ArrowRight') focus((focused + 1) % planets.length);
  if (e.key === 'ArrowLeft') focus((focused - 1 + planets.length) % planets.length);
});

// project dock
const dock = $('#dock');
planets.forEach((p, i) => {
  const b = document.createElement('button');
  b.style.setProperty('--c', p.color);
  b.innerHTML = `<i></i>${p.title}`;
  b.addEventListener('click', () => (focused === i ? unfocus() : focus(i)));
  dock.appendChild(b);
});
$('#skills').innerHTML = SKILLS.map(([n, c]) => `<span style="--c:${c}">${n}</span>`).join('');

// ── loop ──
const timer = new THREE.Timer();
timer.connect(document);
const tmp = new THREE.Vector3();
function frame() {
  timer.update();
  const raw = timer.getDelta();
  const dt = Math.min(raw, 0.05);
  const t = timer.getElapsed();
  timeScale += ((focused >= 0 ? 0.04 : 1) - timeScale) * 0.06;
  bloom.strength += ((focused >= 0 ? 0.3 : mobile ? 0.45 : 0.6) - bloom.strength) * 0.05;
  const k = reduced ? 0.3 : 1;

  crystal.rotation.y += dt * 0.35 * k;
  crystal.rotation.x += dt * 0.15 * k;
  cage.rotation.y -= dt * 0.12 * k;
  cage.rotation.z += dt * 0.05 * k;
  const pulse = 1 + Math.sin(t * 2) * 0.06;
  heart.scale.setScalar(pulse);
  coreGlow.scale.setScalar(10.5 + Math.sin(t * 2) * 0.8);
  belt.rotation.y += dt * 0.03 * timeScale * k;
  skillCubes.forEach((c) => { c.rotation.x += dt * c.userData.spin * k; c.rotation.y += dt * c.userData.spin * 0.7 * k; });
  scene.getObjectByName('stars').rotation.y += dt * 0.004;

  planets.forEach((p, i) => {
    p.angle += dt * p.speed * timeScale * k;
    p.pivot.rotation.y = -p.angle;
    p.body.position.set(p.radius, Math.sin(t * 0.8 + i) * 0.25, 0);
    p.body.rotation.y += dt * 0.4;
    p.moonPivot.rotation.y += dt * 1.6 * k;
    const target = hovered === i || focused === i ? 1.25 : 1;
    p.scale += (target - p.scale) * 0.12;
    p.body.scale.setScalar(p.scale);
    p.el.classList.toggle('hot', hovered === i || focused === i);
  });

  // hover picking
  if (!tween) {
    ray.setFromCamera(pointer, camera);
    const hit = ray.intersectObjects(pickables)[0];
    const prev = hovered;
    if (hit && hit.object.userData.index !== undefined) hovered = hit.object.userData.index;
    else if (prev >= 0 && !planets[prev].el.matches(':hover')) hovered = -1;
    const skill = hit?.object.userData.skill;
    const showPlanet = hovered >= 0 && hovered !== focused;
    tip.textContent = skill || (showPlanet ? `${planets[hovered].title} — click to open` : '');
    tip.classList.toggle('show', !!(skill || showPlanet));
    document.body.style.cursor = hit ? 'pointer' : '';
  }

  // keep camera locked on a focused (slow-moving) planet
  if (tween) {
    tween.t += Math.min(raw, 0.25) / tween.dur;
    const e = ease(Math.min(tween.t, 1));
    if (focused >= 0) {
      planets[focused].mesh.getWorldPosition(tmp);
      tween.t1.copy(tmp);
    }
    camera.position.lerpVectors(tween.p0, tween.p1, e);
    controls.target.lerpVectors(tween.t0, tween.t1, e);
    if (tween.t >= 1) tween = null;
  } else if (focused >= 0) {
    planets[focused].mesh.getWorldPosition(tmp);
    const delta = tmp.clone().sub(controls.target);
    controls.target.add(delta);
    camera.position.add(delta);
  }

  controls.update();
  composer.render();
  labels.render(scene, camera);
  requestAnimationFrame(frame);
}

// intro fly-in
flyTo(HOME, new THREE.Vector3(0, 0, 0), reduced ? 0.01 : 3.2);
requestAnimationFrame(() => {
  $('#loader').classList.add('done');
  document.body.classList.add('ready');
});
frame();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  composer.setSize(innerWidth, innerHeight);
  labels.setSize(innerWidth, innerHeight);
});
