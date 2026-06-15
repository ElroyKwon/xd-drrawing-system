// scene.js — Three.js 씬. BUG-A/B/C 방지 적용.
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ CSS2DRenderer, CSS2DObject }} from 'three/addons/renderers/CSS2DRenderer.js';
import {{ loadKB }} from './kb-loader.js';

const COLOR = {{
  slab: 0x2e3540, wall: 0x6b7a88, room: 0x8fb4c9, stair: 0xffa057,
  parapet: 0x4a5560, grid: 0x445566, text: 0xffffff,
}};

const DEFAULT_WALL_THICKNESS_MM = 200;
const DEFAULT_SLAB_THICKNESS_MM = 250;
const DEFAULT_ROOM_HEIGHT_MM = 2700;

const stage = document.getElementById('stage');
const status = document.getElementById('status');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1e2025);

const camera = new THREE.PerspectiveCamera(45, stage.clientWidth / stage.clientHeight, 10, 1000000);
camera.position.set(35000, 20000, 35000);
camera.lookAt(10000, 5000, 10000);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(stage.clientWidth, stage.clientHeight);
stage.appendChild(renderer.domElement);

const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(stage.clientWidth, stage.clientHeight);
Object.assign(labelRenderer.domElement.style, {{
  position: 'absolute', top: 0, left: 0, pointerEvents: 'none'
}});
stage.appendChild(labelRenderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(10000, 5000, 10000);
scene.add(new THREE.AmbientLight(0xffffff, 0.55));
const dl = new THREE.DirectionalLight(0xffffff, 0.65); dl.position.set(30000, 50000, 20000); scene.add(dl);

const groups = {{
  rooms: new THREE.Group(), walls: new THREE.Group(), slabs: new THREE.Group(),
  stair: new THREE.Group(), grid: new THREE.Group(), labels: new THREE.Group(),
}};
for (const g of Object.values(groups)) scene.add(g);

// BUG-B 방지: shape 좌표를 -y로 (rotateX(-π/2) 적용 시 Z 부호 통일)
function makeExtrudedShape(pts, heightMm, color, opts = {{}}) {{
  if (!pts || pts.length < 3) return null;
  const shape = new THREE.Shape();
  shape.moveTo(pts[0][0], -pts[0][1]);
  for (let i = 1; i < pts.length; i++) shape.lineTo(pts[i][0], -pts[i][1]);
  shape.closePath();
  const geo = new THREE.ExtrudeGeometry(shape, {{ depth: heightMm, bevelEnabled: false }});
  geo.rotateX(-Math.PI / 2);
  // BUG-A 방지: 추가 translate 하지 않는다
  const mat = new THREE.MeshLambertMaterial({{
    color,
    transparent: opts.transparent ?? false,
    opacity: opts.opacity ?? 1.0,
    side: THREE.DoubleSide,
  }});
  return new THREE.Mesh(geo, mat);
}}

function addLabel(text, x, y, z, color = '#eee') {{
  const div = document.createElement('div');
  div.className = 'label';
  div.textContent = text;
  div.style.color = color;
  const lab = new CSS2DObject(div);
  lab.position.set(x, y, z);
  groups.labels.add(lab);
}}

function buildFromKB(kb) {{
  const levels = kb.level_stack?.levels_mm || {{}};
  const floorStack = [];
  // slab + labels per floor
  const floorOrder = ['PIT', 'GL', '1FL', '2FL', '3FL', '4FL', '5FL', 'RFL'];
  for (const name of floorOrder) {{
    if (levels[name] == null) continue;
    const y = levels[name] - (levels['1FL'] || 94200); // normalize 1FL to 0
    floorStack.push({{ name, y }});
    addLabel(name, -3000, y, -3000, '#ffdb70');
  }}

  for (const sheet of kb.sheets) {{
    for (const v of sheet.views || []) {{
      const floor = v.level?.floor || v.view_label || 'unknown';
      const flKey = floor.includes('2층') ? '2FL' : floor.includes('1층') ? '1FL'
                  : floor.includes('옥탑') ? 'RFL' : floor.includes('PIT') ? 'PIT' : '1FL';
      const baseY = (levels[flKey] ?? levels['1FL'] ?? 94200) - (levels['1FL'] || 94200);
      const ffh = (flKey === '2FL' ? 5500 : flKey === 'RFL' ? 4500 : 3500);

      // slab
      const slabPts = v.slab_polygon || deriveBoundingPoly(v.elements);
      if (slabPts) {{
        const slab = makeExtrudedShape(slabPts, DEFAULT_SLAB_THICKNESS_MM, COLOR.slab,
                                       {{ opacity: 1.0, transparent: false }});
        if (slab) {{ slab.position.y = baseY; groups.slabs.add(slab); }}
      }}

      // rooms: 바닥 패치(불투명) + 측벽·천장(반투명)
      for (const r of (v.elements || []).filter(e => e.type === 'room')) {{
        const pts = r.polygon_grid_mm || r.polygon_grid;
        if (!pts || pts.length < 3) continue;
        const floorPatch = makeExtrudedShape(pts, 20, COLOR.room,
                                             {{ transparent: false, opacity: 1.0 }});
        if (floorPatch) {{ floorPatch.position.y = baseY + DEFAULT_SLAB_THICKNESS_MM + 1; groups.rooms.add(floorPatch); }}
        const room = makeExtrudedShape(pts, ffh - DEFAULT_SLAB_THICKNESS_MM, COLOR.room,
                                       {{ transparent: true, opacity: 0.28 }});
        if (room) {{ room.position.y = baseY + DEFAULT_SLAB_THICKNESS_MM + 2; groups.rooms.add(room); }}
        if (r.name) {{
          const cx = pts.reduce((s,p)=>s+p[0],0) / pts.length;
          const cy = pts.reduce((s,p)=>s+p[1],0) / pts.length;
          addLabel(r.name, cx, baseY + ffh - 200, -cy);
        }}
      }}
    }}
  }}
  return floorStack;
}}

function deriveBoundingPoly(elements) {{
  const pts = [];
  for (const e of (elements||[])) {{
    if (e.polygon_grid_mm) for (const p of e.polygon_grid_mm) pts.push(p);
    else if (e.polygon_grid) for (const p of e.polygon_grid) pts.push(p);
  }}
  if (!pts.length) return null;
  const xs = pts.map(p=>p[0]); const ys = pts.map(p=>p[1]);
  const xmin=Math.min(...xs), xmax=Math.max(...xs), ymin=Math.min(...ys), ymax=Math.max(...ys);
  return [[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax]];
}}

function dumpBBox() {{
  const result = {{ views: {{}}, floor_stack: window.__floorStack || [] }};
  const globalAll = {{ min:[+Infinity,+Infinity,+Infinity], max:[-Infinity,-Infinity,-Infinity] }};
  for (const [name, g] of Object.entries(groups)) {{
    let mn=[+Infinity,+Infinity,+Infinity], mx=[-Infinity,-Infinity,-Infinity];
    g.traverse(o => {{
      if (!o.geometry) return;
      o.geometry.computeBoundingBox();
      const bb = o.geometry.boundingBox;
      if (!bb) return;
      const worldMin = bb.min.clone().applyMatrix4(o.matrixWorld);
      const worldMax = bb.max.clone().applyMatrix4(o.matrixWorld);
      mn = [Math.min(mn[0],worldMin.x,worldMax.x), Math.min(mn[1],worldMin.y,worldMax.y), Math.min(mn[2],worldMin.z,worldMax.z)];
      mx = [Math.max(mx[0],worldMin.x,worldMax.x), Math.max(mx[1],worldMin.y,worldMax.y), Math.max(mx[2],worldMin.z,worldMax.z)];
    }});
    if (mn[0] !== +Infinity) {{
      result.views.all = result.views.all || {{}};
      result.views.all[name] = {{ min: mn, max: mx }};
      for (let i=0;i<3;i++) {{
        globalAll.min[i] = Math.min(globalAll.min[i], mn[i]);
        globalAll.max[i] = Math.max(globalAll.max[i], mx[i]);
      }}
    }}
  }}
  result.global = globalAll;
  return result;
}}

window.__scene = {{
  scene, camera, renderer, controls, groups,
  dumpBBox,
  topView() {{ camera.up.set(0,0,-1); camera.position.set(10000, 60000, 10000); controls.target.set(10000, 5000, 10000); controls.update(); }},
  isoView() {{ camera.up.set(0,1,0); camera.position.set(35000, 20000, 35000); controls.target.set(10000, 5000, 10000); controls.update(); }},
  southeastView() {{ camera.up.set(0,1,0); camera.position.set(35000, 8000, -35000); controls.target.set(10000, 5000, 10000); controls.update(); }},
}};

(async () => {{
  try {{
    const kb = await loadKB();
    const fs = buildFromKB(kb);
    window.__floorStack = fs;
    status.textContent = `렌더 OK — 시트 ${{kb.sheets.length}} 장, 층 ${{fs.length}} 개`;
  }} catch (e) {{
    status.textContent = '로드 실패: ' + e.message;
    console.error(e);
  }}
}})();

function animate() {{
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}}
animate();

window.addEventListener('resize', () => {{
  camera.aspect = stage.clientWidth / stage.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(stage.clientWidth, stage.clientHeight);
  labelRenderer.setSize(stage.clientWidth, stage.clientHeight);
}});
