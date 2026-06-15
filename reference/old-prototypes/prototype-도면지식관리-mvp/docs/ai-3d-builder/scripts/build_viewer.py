"""
build_viewer.py — Stage 10 추출 JSON + 원본 PNG → 단일 HTML 검증 뷰어 (Canvas 2D).

좌측: 원본 PNG.  우측: 추출 데이터 Canvas 재구성.
사용:
  python build_viewer.py <stage-10-parsed.json> <original.png> [out.html]
"""
import argparse
import base64
import json
from pathlib import Path


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>__TITLE__</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; background:#1a1a1a; color:#ddd; }
  header { padding:8px 16px; background:#0a0a0a; border-bottom:1px solid #333; display:flex; gap:24px; align-items:center; }
  header strong { font-size:15px; color:#fff; }
  header .meta { color:#888; font-size:12px; }
  .container { display:grid; grid-template-columns:1fr 1fr; gap:6px; padding:6px; height:calc(100vh - 50px); }
  .pane { background:#000; border:1px solid #333; overflow:auto; position:relative; }
  .pane h3 { margin:0; padding:6px 12px; background:#1a1a1a; font-size:12px; font-weight:normal; color:#aaa; border-bottom:1px solid #333; position:sticky; top:0; z-index:5; }
  .pane.original { display:flex; flex-direction:column; }
  .pane.original > div { flex:1; overflow:auto; }
  img.original { width:100%; display:block; }
  .canvas-wrap { background:#fff; }
  canvas { display:block; }
  .views { display:flex; flex-direction:column; }
  .view-block { border-bottom:2px solid #444; padding:8px; }
  .view-block h4 { margin:0 0 6px 0; font-size:12px; color:#ccc; }
  .legend { position:absolute; bottom:8px; right:8px; background:rgba(0,0,0,0.85); padding:8px; font-size:11px; line-height:1.6; border:1px solid #444; }
  .legend .sw { display:inline-block; width:14px; height:8px; vertical-align:middle; margin-right:4px; }
  .info { padding:6px 12px; background:#111; font-size:11px; color:#999; }
</style>
</head>
<body>
<header>
  <strong>__SHEET__</strong>
  <span class="meta">Stage 10 추출 검증 — 좌: 원본 / 우: Canvas 재구성</span>
</header>
<div class="container">
  <div class="pane original">
    <h3>원본 PNG (DPI 400)</h3>
    <div><img class="original" src="data:image/__EXT__;base64,__IMG__" /></div>
  </div>
  <div class="pane">
    <h3>추출 데이터 Canvas</h3>
    <div class="views" id="views"></div>
    <div class="info" id="info"></div>
  </div>
</div>
<div class="legend">
  <span class="sw" style="background:#222"></span> 벽<br>
  <span class="sw" style="background:rgba(100,150,200,0.25);border:1px solid #468"></span> 실<br>
  <span class="sw" style="background:rgba(255,80,80,0.6)"></span> 문<br>
  <span class="sw" style="background:rgba(160,80,200,0.4)"></span> 샤프트/트렌치<br>
  <span class="sw" style="background:rgba(0,160,80,0.4)"></span> EV<br>
  <span class="sw" style="background:#bbf;border:1px dashed #66a"></span> 그리드<br>
  <span class="sw" style="background:#080"></span> 치수
</div>
<script>
const DATA = __DATA__;

// ------ Renderer ------
function cumsum(arr, fallback) {
  const out = [0];
  let s = 0;
  for (const v of arr) {
    s += (v == null ? fallback : v);
    out.push(s);
  }
  return out;
}
function buildAxis(labels, spacings, fallbackSpacing) {
  // n labels, n-1 spacings ideal. if mismatch, truncate.
  const n = labels.length;
  const sp = (spacings || []).slice(0, Math.max(0, n - 1));
  while (sp.length < n - 1) sp.push(null);
  const positions = cumsum(sp, fallbackSpacing);
  const map = {};
  labels.forEach((lab, i) => { map[lab] = positions[i]; });
  return { labels, positions, map, missing: sp.map(v => v == null) };
}

function renderView(container, view) {
  const xAxis = buildAxis(view.grid.x_labels, view.grid.x_spacings_mm, 3000);
  const yAxis = buildAxis(view.grid.y_labels, view.grid.y_spacings_mm, 3000);

  const wrap = document.createElement('div');
  wrap.className = 'view-block';
  const title = document.createElement('h4');
  title.textContent = `${view.view_id || ''}  ${view.view_label || ''}  (${view.view_scale || ''})`;
  wrap.appendChild(title);

  // world bounds (mm), padding
  const pad = 4000;
  const wMin = -pad, wMax = xAxis.positions[xAxis.positions.length - 1] + pad;
  const hMin = -pad, hMax = yAxis.positions[yAxis.positions.length - 1] + pad;
  const worldW = wMax - wMin;
  const worldH = hMax - hMin;

  // canvas size: fit width 700px
  const targetW = 720;
  const scale = targetW / worldW;
  const canvas = document.createElement('canvas');
  canvas.width = targetW;
  canvas.height = Math.round(worldH * scale);
  canvas.style.background = '#fff';
  wrap.appendChild(canvas);
  container.appendChild(wrap);

  const ctx = canvas.getContext('2d');
  // World→Canvas. Y-down: flip so 'A' (top of drawing) is top of canvas.
  function W2C(wx, wy) {
    const cx = (wx - wMin) * scale;
    const cy = (wy - hMin) * scale;
    return [cx, cy];
  }

  // --- Grid ---
  ctx.strokeStyle = '#bbf';
  ctx.fillStyle = '#669';
  ctx.lineWidth = 0.5;
  ctx.font = '11px sans-serif';
  ctx.setLineDash([4, 4]);
  // X grid lines (vertical)
  xAxis.positions.forEach((x, i) => {
    const [cx, cy0] = W2C(x, hMin);
    const [, cy1] = W2C(x, hMax);
    ctx.beginPath(); ctx.moveTo(cx, cy0); ctx.lineTo(cx, cy1); ctx.stroke();
    ctx.fillText(xAxis.labels[i] || '?', cx + 2, 12);
  });
  // Y grid lines (horizontal)
  yAxis.positions.forEach((y, i) => {
    const [cx0, cy] = W2C(wMin, y);
    const [cx1] = W2C(wMax, y);
    ctx.beginPath(); ctx.moveTo(cx0, cy); ctx.lineTo(cx1, cy); ctx.stroke();
    ctx.fillText(yAxis.labels[i] || '?', 2, cy - 2);
  });
  ctx.setLineDash([]);

  function gridPt(g) {
    if (!g || g.length < 2) return null;
    const [xl, yl] = g;
    const wx = xAxis.map[xl];
    const wy = yAxis.map[yl];
    if (wx == null || wy == null) return null;
    return W2C(wx, wy);
  }

  // --- Rooms (polygons) ---
  (view.elements || []).filter(e => e.type === 'room' && e.polygon_grid).forEach(rm => {
    const pts = rm.polygon_grid.map(gridPt).filter(Boolean);
    if (pts.length < 3) return;
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.closePath();
    ctx.fillStyle = 'rgba(100,150,200,0.22)';
    ctx.strokeStyle = 'rgba(60,100,160,0.9)';
    ctx.lineWidth = 1;
    ctx.fill();
    ctx.stroke();
    // label
    const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length;
    const cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    ctx.fillStyle = '#234';
    ctx.font = 'bold 11px Malgun Gothic, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(rm.name || rm.id, cx, cy);
    ctx.textAlign = 'left';
  });

  // --- Shafts ---
  (view.elements || []).filter(e => e.type === 'shaft' && e.polygon_grid).forEach(sh => {
    const pts = sh.polygon_grid.map(gridPt).filter(Boolean);
    if (pts.length < 3) return;
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.closePath();
    ctx.fillStyle = 'rgba(160,80,200,0.4)';
    ctx.strokeStyle = '#624';
    ctx.fill(); ctx.stroke();
    const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length;
    const cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    ctx.fillStyle = '#312';
    ctx.fillText(sh.name || 'shaft', cx + 4, cy);
  });

  // --- Elevator (point) ---
  (view.elements || []).filter(e => e.type === 'elevator').forEach(ev => {
    const p = ev.at_grid ? gridPt(ev.at_grid) : null;
    if (!p) return;
    const sz = (ev.size_mm && ev.size_mm.w ? ev.size_mm.w : 2500) * scale;
    ctx.fillStyle = 'rgba(0,160,80,0.4)';
    ctx.strokeStyle = '#040';
    ctx.lineWidth = 1;
    ctx.fillRect(p[0] - sz/2, p[1] - sz/2, sz, sz);
    ctx.strokeRect(p[0] - sz/2, p[1] - sz/2, sz, sz);
    ctx.fillStyle = '#020';
    ctx.fillText(ev.label || 'EV', p[0] - 8, p[1] + 4);
  });

  // --- Walls ---
  ctx.strokeStyle = '#222';
  (view.elements || []).filter(e => e.type === 'wall' && e.path_grid).forEach(w => {
    const pts = w.path_grid.map(gridPt).filter(Boolean);
    if (pts.length < 2) return;
    const thk = Math.max(2, (w.thickness_mm || 200) * scale);
    ctx.lineWidth = thk;
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.stroke();
  });
  ctx.lineWidth = 1;

  // --- Doors ---
  (view.elements || []).filter(e => e.type === 'door').forEach(d => {
    const a = gridPt(d.on_wall_from);
    const b = gridPt(d.on_wall_to);
    if (!a || !b) return;
    // mark midpoint with red rectangle
    const mx = (a[0] + b[0]) / 2;
    const my = (a[1] + b[1]) / 2;
    const wpx = Math.max(6, (d.width_mm || 900) * scale);
    ctx.fillStyle = 'rgba(255,80,80,0.7)';
    ctx.strokeStyle = '#a00';
    ctx.fillRect(mx - wpx/2, my - 4, wpx, 8);
    ctx.strokeRect(mx - wpx/2, my - 4, wpx, 8);
  });

  // --- Dimensions overlay (as small green text on segments) ---
  ctx.fillStyle = '#080';
  ctx.font = '10px sans-serif';
  (view.dimensions_raw || []).forEach(dim => {
    const a = gridPt(dim.from_grid);
    const b = gridPt(dim.to_grid);
    if (!a || !b) return;
    const mx = (a[0] + b[0]) / 2;
    const my = (a[1] + b[1]) / 2;
    ctx.fillText(dim.text, mx, my - 3);
  });

  return { canvas, xAxis, yAxis };
}

const viewsBox = document.getElementById('views');
(DATA.views || []).forEach(v => renderView(viewsBox, v));

// info bar
const info = document.getElementById('info');
const totalRooms = (DATA.views||[]).reduce((s,v)=>s + (v.elements||[]).filter(e=>e.type==='room').length, 0);
const totalWalls = (DATA.views||[]).reduce((s,v)=>s + (v.elements||[]).filter(e=>e.type==='wall').length, 0);
const totalDoors = (DATA.views||[]).reduce((s,v)=>s + (v.elements||[]).filter(e=>e.type==='door').length, 0);
info.textContent = `Views: ${(DATA.views||[]).length} | Rooms: ${totalRooms} | Walls: ${totalWalls} | Doors: ${totalDoors} | global_confidence: ${DATA.global_confidence ?? 'n/a'}`;
</script>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("image_path")
    ap.add_argument("out_path", nargs="?", default=None)
    args = ap.parse_args()

    json_path = Path(args.json_path)
    img_path = Path(args.image_path)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    img_b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
    ext = img_path.suffix[1:].lower() or "png"

    sheet = data.get("sheet_number") or json_path.stem
    title = f"검증 뷰어 — {sheet}"

    html = (HTML_TEMPLATE
            .replace("__TITLE__", title)
            .replace("__SHEET__", sheet)
            .replace("__EXT__", ext)
            .replace("__IMG__", img_b64)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))

    out = Path(args.out_path) if args.out_path else json_path.parent / "viewer.html"
    out.write_text(html, encoding="utf-8")
    print(f"viewer saved: {out}")
    print(f"  open in browser: file:///{out.as_posix()}")


if __name__ == "__main__":
    main()
