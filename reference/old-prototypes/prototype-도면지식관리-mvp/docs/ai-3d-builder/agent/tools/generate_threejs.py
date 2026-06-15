"""generate_threejs — KB(sheets/*.yml + level-stack.yml) → Three.js 씬 HTML 생성.

p062 MVP 의 scene.js 패턴을 기반으로 결정론적 생성. 에이전트는 이 tool 을
modeling_order.queue 전체 KB 가 채워진 뒤 1~N회 호출하여 3D를 구성.
"""
import sys
from pathlib import Path

from .base import DOCS_DIR, KB_DIR, SHEETS_DIR, THREEJS_DIR, ROOT, rel

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pyyaml"])
    import yaml


SCHEMA = {
    "name": "generate_threejs",
    "description": (
        "sheets/*.yml KB 와 level-stack.yml 을 받아 Three.js 씬(HTML+JS)을 생성한다. "
        "출력은 threejs-scene/{scene_id}/index.html, scene.js, kb-loader.js. "
        "sheet_ids 지정 시 해당 시트들만 포함, 미지정 시 모든 sheets/*.yml. "
        "생성 후 render_preview 로 시각 확인 권장. "
        "BUG-A(이중 translate), BUG-B(Z 부호 분리), BUG-C(슬라브 투명) 방지 코드 내장."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "scene_id": {
                "type": "string",
                "description": "씬 식별자 (예: full-building). threejs-scene/{scene_id}/ 디렉토리 생성.",
            },
            "sheet_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "선택. 포함할 sheet_id 목록. 미지정 시 모든 sheets/*.yml.",
            },
            "preserve_existing": {
                "type": "boolean",
                "description": "true면 scene_id 디렉토리가 있을 때 에러. 기본 false(덮어쓰기).",
            },
        },
        "required": ["scene_id"],
    },
}


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="utf-8">
<title>{scene_id} — 3D 매싱</title>
<style>
  html, body {{ margin:0; padding:0; background:#1e2025; color:#ddd;
    font-family: system-ui, sans-serif; height:100%; overflow:hidden; }}
  #stage {{ position:absolute; inset:0; }}
  #status {{ position:fixed; top:8px; left:8px; padding:6px 10px;
    background:#000a; border-radius:4px; font-size:12px; z-index:10; }}
  .label {{ color:#eee; font-size:11px; background:#0008; padding:2px 4px;
    border-radius:2px; pointer-events:none; white-space:nowrap; }}
</style>
</head><body>
<div id="stage"></div>
<div id="status">loading…</div>
<script type="importmap">{{
  "imports": {{
    "three": "https://unpkg.com/three@0.161.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.161.0/examples/jsm/"
  }}
}}</script>
<script type="module" src="./kb-loader.js"></script>
<script type="module" src="./scene.js"></script>
</body></html>
"""


KB_LOADER_JS = """// kb-loader.js — import KB as ES module (file:// 호환, CORS 우회)
import KB from './kb-data.js';
export async function loadKB() {
  return KB;
}
"""


SCENE_JS_TEMPLATE = """// scene.js — Three.js 씬. BUG-A/B/C 방지 적용.
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
"""


def _load_level_stack():
    path = KB_DIR / "level-stack.yml"
    if not path.exists():
        return {"levels_mm": {}, "offsets_mm": {}, "ffh_mm": {}}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def execute(tool_input, context=None):
    scene_id = tool_input.get("scene_id")
    if not scene_id:
        return {"error": "scene_id 필수"}

    out_dir = THREEJS_DIR / scene_id
    if out_dir.exists() and tool_input.get("preserve_existing"):
        return {"error": f"{scene_id} 이미 존재 — preserve_existing=true 상태"}
    out_dir.mkdir(parents=True, exist_ok=True)

    sheet_ids = tool_input.get("sheet_ids")
    sheet_yamls = []
    if not SHEETS_DIR.exists():
        return {"error": "knowledge-base/sheets/ 없음"}

    yaml_files = sorted(SHEETS_DIR.glob("*.yml"))
    if sheet_ids:
        yaml_files = [p for p in yaml_files if p.stem in sheet_ids]

    if not yaml_files:
        return {"error": "포함할 sheets YAML 없음"}

    for y in yaml_files:
        sheet_yamls.append(yaml.safe_load(y.read_text(encoding="utf-8")))

    level_stack = _load_level_stack()
    kb_payload = {
        "sheets": sheet_yamls,
        "level_stack": level_stack,
    }

    import json as _json
    kb_json_str = _json.dumps(kb_payload, ensure_ascii=False, indent=2)
    # file:// 호환을 위해 kb.json + kb-data.js (ES module export) 둘 다 작성
    (out_dir / "kb.json").write_text(kb_json_str, encoding="utf-8")
    (out_dir / "kb-data.js").write_text(
        f"export default {kb_json_str};\n", encoding="utf-8"
    )
    (out_dir / "index.html").write_text(
        HTML_TEMPLATE.format(scene_id=scene_id), encoding="utf-8"
    )
    (out_dir / "kb-loader.js").write_text(KB_LOADER_JS, encoding="utf-8")
    (out_dir / "scene.js").write_text(SCENE_JS_TEMPLATE, encoding="utf-8")

    return {
        "scene_id": scene_id,
        "scene_dir": rel(out_dir),
        "html_path": rel(out_dir / "index.html"),
        "included_sheets": [p.stem for p in yaml_files],
        "level_stack_levels": list((level_stack.get("levels_mm") or {}).keys()),
        "next_action_hint": (
            f"render_preview(html_path='{rel(out_dir / 'index.html')}') "
            "로 스크린샷 확인 후 validate_coordinate_system 으로 버그 검사."
        ),
    }
