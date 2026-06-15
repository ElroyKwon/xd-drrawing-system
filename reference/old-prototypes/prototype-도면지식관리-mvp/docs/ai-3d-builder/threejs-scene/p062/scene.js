import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { loadKB } from './kb-loader.js';

window.THREE = THREE;

const COLOR = {
  slab: 0x5a6f88,
  slabTop: 0x7a8fa8,
  room: 0xe0c080,
  wall: 0x6a6a7a,
  stair: 0xe08040,
  shaft: 0x40c0b0,
  void: 0x555555,
  pad: 0xa06040,
  parapet: 0xaaaaaa,
  gridLine: 0x444a55,
  bg: 0x1e2025,
};

const DEFAULT_CEILING_MM = 3000;
const SLAB_THICKNESS_MM = 200;
const WALL_DEFAULT_THICKNESS_MM = 200;
const WALL_DEFAULT_HEIGHT_MM = 3000;

const setStatus = (t) => { const el = document.getElementById('status'); if (el) el.textContent = t; };

// --- Grid coord utils ---

function buildGridCoords(labels, spacings) {
  const n = labels?.length || 0;
  const spc = (spacings || []).slice(0, Math.max(0, n - 1));
  const coords = [0];
  let cum = 0;
  for (let i = 0; i < n - 1; i++) {
    const s = Number.isFinite(spc[i]) && spc[i] > 0 ? spc[i] : 0;
    cum += s;
    coords.push(cum);
  }
  const map = Object.fromEntries(labels.map((l, i) => [String(l), coords[i]]));
  return { coordMap: map, total: cum, coords };
}

function pairToXZ(pair, xMap, zMap) {
  if (!Array.isArray(pair) || pair.length < 2) return null;
  const xk = String(pair[0]);
  const zk = String(pair[1]);
  if (!(xk in xMap) || !(zk in zMap)) return null;
  return [xMap[xk], zMap[zk]];
}

function polygonToXZ(poly, xMap, zMap) {
  if (!Array.isArray(poly)) return [];
  const pts = poly.map(p => pairToXZ(p, xMap, zMap)).filter(Boolean);
  return pts;
}

function polygonBBox(pts) {
  if (!pts.length) return null;
  let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
  for (const [x, z] of pts) {
    if (x < minX) minX = x;
    if (x > maxX) maxX = x;
    if (z < minZ) minZ = z;
    if (z > maxZ) maxZ = z;
  }
  return { minX, maxX, minZ, maxZ, cx: (minX + maxX) / 2, cz: (minZ + maxZ) / 2 };
}

function expandToQuadIfDegenerate(pts, fallbackCellX = 4000, fallbackCellZ = 4000) {
  // polygon 이 1점 또는 2점이면 근사 사각형으로 확장 (MVP 허용)
  if (pts.length >= 3) return pts;
  if (pts.length === 2) {
    const [[x1, z1], [x2, z2]] = pts;
    return [[x1, z1], [x2, z1], [x2, z2], [x1, z2]];
  }
  if (pts.length === 1) {
    const [x, z] = pts[0];
    const hx = fallbackCellX / 2, hz = fallbackCellZ / 2;
    return [[x - hx, z - hz], [x + hx, z - hz], [x + hx, z + hz], [x - hx, z + hz]];
  }
  return pts;
}

// --- Mesh builders ---

function makeExtrudedShape(pts, heightMm, color, opts = {}) {
  if (pts.length < 3) return null;
  // pts 는 [X, Z] 쌍 (그리드 좌표계). Three.js Shape 은 XY 평면이라 y 에 Z 를 넣되,
  // rotateX(-π/2) 가 shape.y → scene.-z 로 매핑되므로 부호를 뒤집어야 결과 scene.z 가 원래 Z 가 된다.
  const shape = new THREE.Shape();
  shape.moveTo(pts[0][0], -pts[0][1]);
  for (let i = 1; i < pts.length; i++) shape.lineTo(pts[i][0], -pts[i][1]);
  shape.closePath();
  const geom = new THREE.ExtrudeGeometry(shape, { depth: Math.max(heightMm, 1), bevelEnabled: false });
  // rotateX(-π/2): (x, y, z) → (x, z, -y). 그러므로 extrude +z 방향이 +y 가 됨 → bottom y=0, top y=+depth.
  geom.rotateX(-Math.PI / 2);
  const mat = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.75,
    metalness: 0.05,
    transparent: opts.transparent || false,
    opacity: opts.opacity ?? 1.0,
    side: THREE.DoubleSide,
  });
  return new THREE.Mesh(geom, mat);
}

function makeBox(w, h, d, color, opts = {}) {
  const geom = new THREE.BoxGeometry(Math.max(w, 1), Math.max(h, 1), Math.max(d, 1));
  const mat = new THREE.MeshStandardMaterial({
    color, roughness: 0.75, metalness: 0.05,
    transparent: opts.transparent || false, opacity: opts.opacity ?? 1.0,
  });
  return new THREE.Mesh(geom, mat);
}

function makeCSS2DLabel(text, className = 'label-room') {
  const el = document.createElement('div');
  el.className = className;
  el.textContent = text;
  return new CSS2DObject(el);
}

// --- Wall segment → box ---

function buildWallSegment(pathPts, thicknessMm, heightMm, color) {
  if (pathPts.length < 2) return null;
  const group = new THREE.Group();
  for (let i = 0; i < pathPts.length - 1; i++) {
    const [x1, z1] = pathPts[i];
    const [x2, z2] = pathPts[i + 1];
    const dx = x2 - x1, dz = z2 - z1;
    const len = Math.hypot(dx, dz);
    if (len < 1) continue;
    const box = makeBox(len, heightMm, thicknessMm, color);
    box.position.set((x1 + x2) / 2, heightMm / 2, (z1 + z2) / 2);
    box.rotation.y = -Math.atan2(dz, dx);
    group.add(box);
  }
  return group;
}

// --- Grid helper on a plane ---

function buildGridLines(xCoords, zCoords, y, xLabels, zLabels) {
  const group = new THREE.Group();
  const xMin = xCoords[0], xMax = xCoords[xCoords.length - 1];
  const zMin = zCoords[0], zMax = zCoords[zCoords.length - 1];
  const lineMat = new THREE.LineBasicMaterial({ color: COLOR.gridLine, transparent: true, opacity: 0.4 });

  // X 축 라인 (수직선 — 각 X 라벨마다 Z 방향으로 뻗은 선)
  for (let i = 0; i < xCoords.length; i++) {
    const x = xCoords[i];
    const g = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(x, y, zMin),
      new THREE.Vector3(x, y, zMax),
    ]);
    group.add(new THREE.Line(g, lineMat));
    // 라벨 (시작 쪽)
    const lbl = makeCSS2DLabel(xLabels[i], 'label-grid');
    lbl.position.set(x, y, zMin - 800);
    group.add(lbl);
  }
  for (let i = 0; i < zCoords.length; i++) {
    const z = zCoords[i];
    const g = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(xMin, y, z),
      new THREE.Vector3(xMax, y, z),
    ]);
    group.add(new THREE.Line(g, lineMat));
    const lbl = makeCSS2DLabel(zLabels[i], 'label-grid');
    lbl.position.set(xMin - 800, y, z);
    group.add(lbl);
  }
  return group;
}

// --- View builder (한 view 의 elements 를 그룹으로) ---

function buildViewGroup(view, baseY, flatHeightFallback) {
  const { grid } = view;
  const gx = buildGridCoords(grid.x_labels, grid.x_spacings_mm);
  const gz = buildGridCoords(grid.y_labels, grid.y_spacings_mm);
  const xMap = gx.coordMap, zMap = gz.coordMap;

  const viewGroup = new THREE.Group();
  viewGroup.name = `view:${view.view_id}`;

  const groups = {
    slabs: new THREE.Group(), rooms: new THREE.Group(),
    walls: new THREE.Group(), cores: new THREE.Group(),
    voids: new THREE.Group(), grid: new THREE.Group(),
    labels: new THREE.Group(),
  };
  Object.entries(groups).forEach(([k, g]) => { g.name = `${view.view_id}:${k}`; viewGroup.add(g); });

  // --- Slab (층 외곽) ---
  const outerRect = [
    [gx.coords[0], gz.coords[0]],
    [gx.coords[gx.coords.length - 1], gz.coords[0]],
    [gx.coords[gx.coords.length - 1], gz.coords[gz.coords.length - 1]],
    [gx.coords[0], gz.coords[gz.coords.length - 1]],
  ];
  const slabMesh = makeExtrudedShape(outerRect, SLAB_THICKNESS_MM, COLOR.slab, { opacity: 1.0, transparent: false });
  if (slabMesh) {
    slabMesh.position.y = baseY - SLAB_THICKNESS_MM;
    slabMesh.name = `${view.view_id}:slab`;
    groups.slabs.add(slabMesh);
  }

  // --- 그리드 라인 (슬래브 위) ---
  const gridLines = buildGridLines(gx.coords, gz.coords, baseY + 2, view.grid.x_labels, view.grid.y_labels);
  groups.grid.add(gridLines);

  // --- Elements ---
  const elements = view.elements || [];
  let droppedShapeCount = 0;

  for (const el of elements) {
    const type = el.type;
    if (type === 'room') {
      const raw = polygonToXZ(el.polygon_grid || [], xMap, zMap);
      const pts = expandToQuadIfDegenerate(raw);
      const h = el.ceiling_height_mm || DEFAULT_CEILING_MM;
      if (pts.length < 3) { droppedShapeCount++; continue; }
      // 1) 바닥 패치 (불투명) — 위에서 내려다봤을 때 실 색상이 보이도록.
      const floorPatch = makeExtrudedShape(pts, 20, COLOR.room, { transparent: false, opacity: 1.0 });
      if (floorPatch) {
        floorPatch.position.y = baseY + 1;
        floorPatch.userData = { id: el.id, type: 'room_floor', name: el.name };
        groups.rooms.add(floorPatch);
      }
      // 2) 측벽+천장 (반투명) — 내부 구조 보임.
      const mesh = makeExtrudedShape(pts, h, COLOR.room, { transparent: true, opacity: 0.28 });
      if (mesh) {
        mesh.position.y = baseY;
        mesh.userData = { id: el.id, type, name: el.name, room_number: el.room_number };
        groups.rooms.add(mesh);
        const bb = polygonBBox(pts);
        if (el.name && bb) {
          const lbl = makeCSS2DLabel(
            el.room_number ? `${el.name} (${el.room_number})` : el.name,
            'label-room',
          );
          lbl.position.set(bb.cx, baseY + Math.min(h, DEFAULT_CEILING_MM) * 0.6, bb.cz);
          groups.labels.add(lbl);
        }
      }
    } else if (type === 'wall') {
      const path = polygonToXZ(el.path_grid || [], xMap, zMap);
      if (path.length < 2) { droppedShapeCount++; continue; }
      const wall = buildWallSegment(path, el.thickness_mm || WALL_DEFAULT_THICKNESS_MM,
                                    flatHeightFallback || WALL_DEFAULT_HEIGHT_MM, COLOR.wall);
      if (wall) { wall.position.y = baseY; groups.walls.add(wall); }
    } else if (type === 'stair') {
      const pts = polygonToXZ(el.polygon_grid || [], xMap, zMap);
      const expanded = expandToQuadIfDegenerate(pts, 3000, 3000);
      if (expanded.length >= 3) {
        const mesh = makeExtrudedShape(expanded, DEFAULT_CEILING_MM, COLOR.stair, { opacity: 0.8, transparent: true });
        if (mesh) {
          mesh.position.y = baseY;
          mesh.userData = { id: el.id, type, label: el.label };
          groups.cores.add(mesh);
          const bb = polygonBBox(expanded);
          if (bb) {
            const lbl = makeCSS2DLabel(el.label || '계단', 'label-room');
            lbl.position.set(bb.cx, baseY + DEFAULT_CEILING_MM * 0.9, bb.cz);
            groups.labels.add(lbl);
          }
        }
      }
    } else if (type === 'shaft' || type === 'elevator') {
      // at_grid 우선, polygon 이면 extrude
      if (el.polygon_grid && el.polygon_grid.length >= 1) {
        const pts = polygonToXZ(el.polygon_grid, xMap, zMap);
        const expanded = expandToQuadIfDegenerate(pts, 2000, 2000);
        if (expanded.length >= 3) {
          const mesh = makeExtrudedShape(expanded, DEFAULT_CEILING_MM, COLOR.shaft, { opacity: 0.9, transparent: true });
          if (mesh) { mesh.position.y = baseY; groups.cores.add(mesh); }
        }
      } else if (el.at_grid) {
        const xz = pairToXZ(el.at_grid, xMap, zMap);
        if (xz) {
          const w = (el.size_mm && el.size_mm.w) || 2000;
          const d = (el.size_mm && el.size_mm.d) || 2000;
          const h = DEFAULT_CEILING_MM;
          const box = makeBox(w, h, d, COLOR.shaft, { opacity: 0.9, transparent: true });
          box.position.set(xz[0], baseY + h / 2, xz[1]);
          groups.cores.add(box);
          if (el.label) {
            const lbl = makeCSS2DLabel(el.label, 'label-room');
            lbl.position.set(xz[0], baseY + h * 0.9, xz[1]);
            groups.labels.add(lbl);
          }
        }
      }
    } else if (type === 'void') {
      const pts = polygonToXZ(el.polygon_grid || [], xMap, zMap);
      const expanded = expandToQuadIfDegenerate(pts);
      if (expanded.length >= 3) {
        const mesh = makeExtrudedShape(expanded, 100, COLOR.void, { opacity: 0.3, transparent: true });
        if (mesh) { mesh.position.y = baseY - 50; groups.voids.add(mesh); }
      }
    } else if (type === 'column') {
      if (el.at_grid) {
        const xz = pairToXZ(el.at_grid, xMap, zMap);
        if (xz) {
          const w = (el.size_mm && el.size_mm.w) || 500;
          const d = (el.size_mm && el.size_mm.d) || 500;
          const h = flatHeightFallback || WALL_DEFAULT_HEIGHT_MM;
          const box = makeBox(w, h, d, COLOR.wall);
          box.position.set(xz[0], baseY + h / 2, xz[1]);
          groups.walls.add(box);
        }
      }
    }
  }

  if (droppedShapeCount > 0) {
    console.warn(`[view ${view.view_id}] 그리드 매칭 실패로 누락된 요소: ${droppedShapeCount}`);
  }

  return { viewGroup, groups, gx, gz };
}

// --- Parapet on RFL outer ---

function buildParapet(gx, gz, baseY, topY) {
  const outer = [
    [gx.coords[0], gz.coords[0]],
    [gx.coords[gx.coords.length - 1], gz.coords[0]],
    [gx.coords[gx.coords.length - 1], gz.coords[gz.coords.length - 1]],
    [gx.coords[0], gz.coords[gz.coords.length - 1]],
    [gx.coords[0], gz.coords[0]],
  ];
  const group = new THREE.Group();
  const height = topY - baseY;
  for (let i = 0; i < outer.length - 1; i++) {
    const [x1, z1] = outer[i], [x2, z2] = outer[i + 1];
    const dx = x2 - x1, dz = z2 - z1;
    const len = Math.hypot(dx, dz);
    if (len < 1) continue;
    const box = makeBox(len, height, 150, COLOR.parapet, { opacity: 0.6, transparent: true });
    box.position.set((x1 + x2) / 2, baseY + height / 2, (z1 + z2) / 2);
    box.rotation.y = -Math.atan2(dz, dx);
    group.add(box);
  }
  return group;
}

// --- Ground (GL) 박스 ---

function buildGround(view, glY) {
  const gx = buildGridCoords(view.grid.x_labels, view.grid.x_spacings_mm);
  const gz = buildGridCoords(view.grid.y_labels, view.grid.y_spacings_mm);
  const margin = 5000;
  const w = gx.total + margin * 2;
  const d = gz.total + margin * 2;
  const g = new THREE.BoxGeometry(w, 200, d);
  const m = new THREE.MeshStandardMaterial({ color: 0x4a5060, roughness: 0.95, metalness: 0 });
  const mesh = new THREE.Mesh(g, m);
  mesh.position.set(gx.total / 2, glY - 100, gz.total / 2);
  return mesh;
}

// --- Floor label ---

function buildFloorLabel(text, y, x, z) {
  const lbl = makeCSS2DLabel(text, 'label-floor');
  lbl.position.set(x, y, z);
  return lbl;
}

// --- Main ---

async function main() {
  setStatus('KB 로딩 중…');
  const { sheet, levelStack } = await loadKB({ sheetId: 'arch_p062' });

  document.getElementById('hud-sheet').textContent =
    `${sheet.sheet_id} (${sheet.sheet_number || '-'})`;
  document.getElementById('hud-conf').textContent =
    (sheet.global_confidence ?? '-') + '';
  const levels = levelStack.levels_mm || {};
  document.getElementById('hud-levels').textContent =
    ['GL', '1FL', '2FL', 'RFL'].map(k => `${k}=${(levels[k]||'-')}mm`).join(' / ');

  const views = sheet.views || [];
  const v1 = views.find(v => v.view_id === 'v1') || views[0];
  const v2 = views.find(v => v.view_id === 'v2');

  const GL = levels.GL ?? 94000;
  const L1 = levels['1FL'] ?? 94200;
  const L2 = levels['2FL'] ?? 99700;
  const LR = levels.RFL ?? 104200;
  const PARAPET_TOP = (levelStack.offsets_mm?.['RSFL+1800']) ?? (LR + 1800);

  // --- scene setup ---
  const container = document.getElementById('scene-root');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(COLOR.bg);
  scene.fog = new THREE.Fog(COLOR.bg, 50000, 200000);

  const camera = new THREE.PerspectiveCamera(
    45, container.clientWidth / container.clientHeight, 100, 500000,
  );

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  const labelRenderer = new CSS2DRenderer();
  labelRenderer.setSize(container.clientWidth, container.clientHeight);
  labelRenderer.domElement.style.position = 'absolute';
  labelRenderer.domElement.style.top = '0';
  labelRenderer.domElement.style.left = '0';
  labelRenderer.domElement.style.pointerEvents = 'none';
  container.appendChild(labelRenderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;

  // --- lighting ---
  scene.add(new THREE.HemisphereLight(0xffffff, 0x444466, 0.6));
  const dir = new THREE.DirectionalLight(0xffffff, 0.7);
  dir.position.set(20000, 60000, 30000);
  dir.castShadow = true;
  scene.add(dir);
  const dir2 = new THREE.DirectionalLight(0xaabbee, 0.25);
  dir2.position.set(-20000, 30000, -10000);
  scene.add(dir2);

  // --- 지반 (GL) ---
  const groundMesh = buildGround(v1, GL);
  scene.add(groundMesh);

  // --- 1FL slab (외곽 추정: v1 과 동일 footprint) ---
  const gxRef = buildGridCoords(v1.grid.x_labels, v1.grid.x_spacings_mm);
  const gzRef = buildGridCoords(v1.grid.y_labels, v1.grid.y_spacings_mm);
  const outer1FL = [
    [gxRef.coords[0], gzRef.coords[0]],
    [gxRef.coords[gxRef.coords.length - 1], gzRef.coords[0]],
    [gxRef.coords[gxRef.coords.length - 1], gzRef.coords[gzRef.coords.length - 1]],
    [gxRef.coords[0], gzRef.coords[gzRef.coords.length - 1]],
  ];
  const slab1FL = makeExtrudedShape(outer1FL, SLAB_THICKNESS_MM, COLOR.slab, { opacity: 1.0, transparent: false });
  slab1FL.position.y = L1 - SLAB_THICKNESS_MM;
  slab1FL.name = '1FL:slab';
  scene.add(slab1FL);

  // --- 2FL (v1) ---
  const v1Build = buildViewGroup(v1, L2, DEFAULT_CEILING_MM);
  v1Build.viewGroup.name = '2FL';
  scene.add(v1Build.viewGroup);
  scene.add(buildFloorLabel('2FL (99.70m)', L2 + 500,
    v1Build.gx.total + 2000, -2000));

  // --- RFL (v2) ---
  let v2Build = null;
  if (v2) {
    v2Build = buildViewGroup(v2, LR, 1000);
    v2Build.viewGroup.name = 'RFL';
    scene.add(v2Build.viewGroup);
    scene.add(buildFloorLabel('RFL (104.20m)', LR + 500,
      v2Build.gx.total + 2000, -2000));

    // 파라펫 (RSFL+1800)
    const parapet = buildParapet(v2Build.gx, v2Build.gz, LR, PARAPET_TOP);
    parapet.name = 'parapet';
    scene.add(parapet);
  }

  scene.add(buildFloorLabel('GL (94.00m)', GL + 100,
    gxRef.total + 2000, -2000));
  scene.add(buildFloorLabel('1FL (94.20m)', L1 + 200,
    gxRef.total + 2000, -2000));

  // --- 카메라 fit-to-bounds ---
  // XZ footprint 를 기준으로 distance 계산 (Y 스택은 건물 footprint 에 비해 작음).
  function sceneBounds() {
    const box = new THREE.Box3().setFromObject(scene);
    return { box, size: box.getSize(new THREE.Vector3()), center: box.getCenter(new THREE.Vector3()) };
  }
  function fitCamera() {
    const { center, size } = sceneBounds();
    const maxXZ = Math.max(size.x, size.z);
    const dist = maxXZ * 1.2;
    camera.position.set(center.x + dist * 0.9, center.y + dist * 0.55, center.z + dist * 0.9);
    camera.lookAt(center);
    controls.target.copy(center);
    controls.update();
  }
  fitCamera();

  function topView() {
    const { center, size } = sceneBounds();
    const maxXZ = Math.max(size.x, size.z);
    camera.position.set(center.x, center.y + maxXZ * 1.8, center.z);
    camera.up.set(0, 0, -1);  // top-down 에서는 Z(남북) 이 위쪽
    camera.lookAt(center);
    controls.target.copy(center);
    controls.update();
  }
  function isoView() {
    camera.up.set(0, 1, 0);
    fitCamera();
  }
  function focusFloor(y, vSize) {
    const { center, size } = sceneBounds();
    const maxXZ = Math.max(size.x, size.z);
    const dist = maxXZ * 1.0;
    camera.up.set(0, 1, 0);
    camera.position.set(center.x + dist * 0.8, y + vSize * 1.2, center.z + dist * 0.8);
    const tgt = new THREE.Vector3(center.x, y + vSize / 2, center.z);
    camera.lookAt(tgt);
    controls.target.copy(tgt);
    controls.update();
  }

  document.getElementById('cam-top').addEventListener('click', topView);
  document.getElementById('cam-iso').addEventListener('click', isoView);
  document.getElementById('cam-fit').addEventListener('click', fitCamera);

  // 디버그/외부 호출용 전역 훅
  window.__scene = {
    scene, camera, controls, renderer, labelRenderer,
    topView, isoView, fitCamera, focusFloor,
    L1, L2, LR, GL, PARAPET_TOP,
    v1Build, v2Build,
  };

  // --- 옵션 토글 ---
  function gatherByKey(builds, key) {
    const list = [];
    for (const b of builds) if (b && b.groups?.[key]) list.push(b.groups[key]);
    return list;
  }
  const allBuilds = [v1Build, v2Build].filter(Boolean);

  const toggles = {
    'opt-slabs': () => [slab1FL, groundMesh, ...gatherByKey(allBuilds, 'slabs')],
    'opt-rooms': () => gatherByKey(allBuilds, 'rooms'),
    'opt-walls': () => gatherByKey(allBuilds, 'walls'),
    'opt-cores': () => gatherByKey(allBuilds, 'cores'),
    'opt-voids': () => gatherByKey(allBuilds, 'voids'),
    'opt-grid':  () => gatherByKey(allBuilds, 'grid'),
    'opt-labels':() => gatherByKey(allBuilds, 'labels'),
    'opt-parapet': () => scene.children.filter(c => c.name === 'parapet'),
  };
  for (const [id, getter] of Object.entries(toggles)) {
    const el = document.getElementById(id);
    if (!el) continue;
    el.addEventListener('change', () => {
      const objs = getter();
      for (const o of objs) o.visible = el.checked;
    });
  }

  // --- resize ---
  function onResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
    labelRenderer.setSize(container.clientWidth, container.clientHeight);
  }
  window.addEventListener('resize', onResize);

  // --- animate ---
  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
  }
  animate();

  setStatus(`렌더 OK · elements: v1=${(v1.elements||[]).length} v2=${(v2?.elements||[]).length}`);
  console.log('[scene] ready', { sheet, levelStack });
}

main().catch(err => {
  console.error(err);
  setStatus('에러: ' + err.message);
});
