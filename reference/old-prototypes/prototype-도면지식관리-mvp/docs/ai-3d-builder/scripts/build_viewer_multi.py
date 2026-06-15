"""
build_viewer_multi.py — 여러 시트의 stage-10 결과를 한 화면에 행 단위로 표시.

사용:
  python build_viewer_multi.py out.html \
    --pair json1.json img1.png \
    --pair json2.json img2.png \
    [--label "p060 (Opus 4.7)"] [--label "p062 (Opus 4.7)"]
"""
import argparse
import base64
import json
from pathlib import Path


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>다중 시트 누적 비교</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Malgun Gothic','맑은 고딕',sans-serif; background:#1a1a1a; color:#ddd; }
  header { padding:8px 16px; background:#0a0a0a; border-bottom:1px solid #333; display:flex; gap:24px; align-items:center; }
  header strong { font-size:15px; color:#fff; }
  header .meta { color:#888; font-size:12px; }
  .sheet-row { display:grid; grid-template-columns:1fr 1fr; gap:6px; padding:6px; border-bottom:2px solid #333; height:calc(100vh - 90px); }
  .pane { background:#000; border:1px solid #333; overflow:auto; position:relative; display:flex; flex-direction:column; }
  .pane h3 { margin:0; padding:6px 12px; background:#1a1a1a; font-size:12px; font-weight:normal; color:#aaa; border-bottom:1px solid #333; position:sticky; top:0; z-index:5; }
  .pane.original > div.imgwrap { padding:4px; overflow:auto; flex:1; }
  img.original { max-width:100%; display:block; }
  .views { display:flex; flex-direction:column; }
  .view-block { border-bottom:2px solid #444; padding:8px; background:#fff; }
  .view-block h4 { margin:0 0 6px 0; font-size:11px; color:#345; }
  canvas { display:block; }
  .info { padding:6px 12px; background:#111; font-size:11px; color:#999; }
  .legend-bar { padding:6px 12px; background:#0d0d0d; font-size:11px; color:#ccc; border-bottom:1px solid #333; display:flex; gap:16px; flex-wrap:wrap; }
  .legend-bar span.sw { display:inline-block; width:12px; height:8px; vertical-align:middle; margin-right:4px; }
</style>
</head>
<body>
<header>
  <strong>다중 시트 누적 비교</strong>
  <span class="meta">Stage 10 추출 검증 — 행마다 좌(원본 PNG) / 우(Canvas 재구성)</span>
</header>
<div class="legend-bar">
  <span><span class="sw" style="background:#222"></span>벽</span>
  <span><span class="sw" style="background:rgba(100,150,200,0.25);border:1px solid #468"></span>실</span>
  <span><span class="sw" style="background:rgba(255,80,80,0.6)"></span>문</span>
  <span><span class="sw" style="background:rgba(160,80,200,0.4)"></span>샤프트</span>
  <span><span class="sw" style="background:rgba(0,160,80,0.4)"></span>EV</span>
  <span><span class="sw" style="background:#bbf;border:1px dashed #66a"></span>그리드</span>
  <span><span class="sw" style="background:#080"></span>치수</span>
  <span><span class="sw" style="background:#a0a;border-radius:50%;width:8px;height:8px"></span>기둥</span>
</div>
<div id="sheets"></div>
<script>
const SHEETS = __SHEETS__;

function cumsum(arr, fallback) {
  const out = [0]; let s = 0;
  for (const v of arr) { s += (v == null ? fallback : v); out.push(s); }
  return out;
}
function buildAxis(labels, spacings, fallback) {
  const n = labels.length;
  const sp = (spacings || []).slice(0, Math.max(0, n - 1));
  while (sp.length < n - 1) sp.push(null);
  const positions = cumsum(sp, fallback);
  const map = {};
  labels.forEach((lab, i) => { map[lab] = positions[i]; });
  return { labels, positions, map };
}

function renderView(container, view) {
  const xAxis = buildAxis(view.grid.x_labels, view.grid.x_spacings_mm, 3000);
  const yAxis = buildAxis(view.grid.y_labels, view.grid.y_spacings_mm, 3000);

  const wrap = document.createElement('div');
  wrap.className = 'view-block';
  const title = document.createElement('h4');
  title.textContent = `${view.view_id || ''} ${view.view_label || ''} (${view.view_scale || ''})`;
  wrap.appendChild(title);

  const pad = 4000;
  const wMin = -pad, wMax = xAxis.positions[xAxis.positions.length - 1] + pad;
  const hMin = -pad, hMax = yAxis.positions[yAxis.positions.length - 1] + pad;
  const worldW = wMax - wMin;
  const worldH = hMax - hMin;
  const targetW = 700;
  const scale = targetW / worldW;
  const canvas = document.createElement('canvas');
  canvas.width = targetW;
  canvas.height = Math.round(worldH * scale);
  wrap.appendChild(canvas);
  container.appendChild(wrap);

  const ctx = canvas.getContext('2d');
  function W2C(wx, wy) { return [(wx - wMin) * scale, (wy - hMin) * scale]; }

  // grid
  ctx.strokeStyle = '#bbf'; ctx.fillStyle = '#669';
  ctx.lineWidth = 0.5; ctx.font = '11px sans-serif';
  ctx.setLineDash([4, 4]);
  xAxis.positions.forEach((x, i) => {
    const [cx] = W2C(x, hMin); const [, cy0] = W2C(x, hMin); const [, cy1] = W2C(x, hMax);
    ctx.beginPath(); ctx.moveTo(cx, cy0); ctx.lineTo(cx, cy1); ctx.stroke();
    ctx.fillText(xAxis.labels[i] || '?', cx + 2, 12);
  });
  yAxis.positions.forEach((y, i) => {
    const [cx0, cy] = W2C(wMin, y); const [cx1] = W2C(wMax, y);
    ctx.beginPath(); ctx.moveTo(cx0, cy); ctx.lineTo(cx1, cy); ctx.stroke();
    ctx.fillText(yAxis.labels[i] || '?', 2, cy - 2);
  });
  ctx.setLineDash([]);

  function gridPt(g) {
    if (!g || g.length < 2) return null;
    const wx = xAxis.map[g[0]], wy = yAxis.map[g[1]];
    if (wx == null || wy == null) return null;
    return W2C(wx, wy);
  }

  (view.elements || []).filter(e => e.type === 'room' && e.polygon_grid).forEach(rm => {
    const pts = rm.polygon_grid.map(gridPt).filter(Boolean);
    if (pts.length < 3) return;
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.closePath();
    ctx.fillStyle = 'rgba(100,150,200,0.22)';
    ctx.strokeStyle = 'rgba(60,100,160,0.9)';
    ctx.lineWidth = 1; ctx.fill(); ctx.stroke();
    const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length;
    const cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    ctx.fillStyle = '#234'; ctx.font = 'bold 10px Malgun Gothic, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(rm.name || rm.id, cx, cy);
    ctx.textAlign = 'left';
  });

  (view.elements || []).filter(e => e.type === 'shaft' && e.polygon_grid).forEach(sh => {
    const pts = sh.polygon_grid.map(gridPt).filter(Boolean);
    if (pts.length < 3) return;
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.closePath();
    ctx.fillStyle = 'rgba(160,80,200,0.4)'; ctx.strokeStyle = '#624';
    ctx.fill(); ctx.stroke();
  });

  (view.elements || []).filter(e => e.type === 'elevator' && e.at_grid).forEach(ev => {
    const p = gridPt(ev.at_grid); if (!p) return;
    const sz = ((ev.size_mm && ev.size_mm.w) || 2500) * scale;
    ctx.fillStyle = 'rgba(0,160,80,0.4)'; ctx.strokeStyle = '#040';
    ctx.fillRect(p[0] - sz/2, p[1] - sz/2, sz, sz);
    ctx.strokeRect(p[0] - sz/2, p[1] - sz/2, sz, sz);
    ctx.fillStyle = '#020'; ctx.fillText(ev.label || 'EV', p[0] - 8, p[1] + 4);
  });

  ctx.strokeStyle = '#222';
  (view.elements || []).filter(e => e.type === 'wall' && e.path_grid).forEach(w => {
    const pts = w.path_grid.map(gridPt).filter(Boolean);
    if (pts.length < 2) return;
    ctx.lineWidth = Math.max(2, (w.thickness_mm || 200) * scale);
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.stroke();
  });
  ctx.lineWidth = 1;

  (view.elements || []).filter(e => e.type === 'column' && e.at_grid).forEach(c => {
    const p = gridPt(c.at_grid); if (!p) return;
    const r = 4;
    ctx.fillStyle = 'rgba(160,40,160,0.7)'; ctx.strokeStyle = '#404';
    ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI*2); ctx.fill(); ctx.stroke();
  });

  (view.elements || []).filter(e => e.type === 'door').forEach(d => {
    const a = gridPt(d.on_wall_from), b = gridPt(d.on_wall_to);
    if (!a || !b) return;
    const mx = (a[0]+b[0])/2, my = (a[1]+b[1])/2;
    const wpx = Math.max(6, (d.width_mm || 900) * scale);
    ctx.fillStyle = 'rgba(255,80,80,0.7)'; ctx.strokeStyle = '#a00';
    ctx.fillRect(mx - wpx/2, my - 4, wpx, 8);
    ctx.strokeRect(mx - wpx/2, my - 4, wpx, 8);
  });

  (view.elements || []).filter(e => e.type === 'stair' && e.at_grid).forEach(st => {
    const p = gridPt(st.at_grid); if (!p) return;
    ctx.fillStyle = '#950'; ctx.font = 'bold 10px sans-serif';
    ctx.fillText(st.label || 'UP', p[0]-10, p[1]+4);
  });

  ctx.fillStyle = '#080'; ctx.font = '9px sans-serif';
  (view.dimensions_raw || []).forEach(dim => {
    const a = gridPt(dim.from_grid), b = gridPt(dim.to_grid);
    if (!a || !b) return;
    const mx = (a[0]+b[0])/2, my = (a[1]+b[1])/2;
    ctx.fillText(dim.text, mx, my - 3);
  });
}

const sheetsBox = document.getElementById('sheets');
SHEETS.forEach((sh, idx) => {
  const row = document.createElement('div');
  row.className = 'sheet-row';
  const left = document.createElement('div');
  left.className = 'pane original';
  left.innerHTML = `<h3>${sh.label} — 원본</h3><div class="imgwrap"><img class="original" src="data:image/png;base64,${sh.img_b64}"></div>`;
  const right = document.createElement('div');
  right.className = 'pane';
  right.innerHTML = `<h3>${sh.label} — Canvas 재구성</h3>`;
  const views = document.createElement('div');
  views.className = 'views';
  right.appendChild(views);
  row.appendChild(left); row.appendChild(right);
  sheetsBox.appendChild(row);
  (sh.data.views || []).forEach(v => renderView(views, v));
  const info = document.createElement('div');
  info.className = 'info';
  const totalRooms = (sh.data.views||[]).reduce((s,v)=>s + (v.elements||[]).filter(e=>e.type==='room').length, 0);
  const totalWalls = (sh.data.views||[]).reduce((s,v)=>s + (v.elements||[]).filter(e=>e.type==='wall').length, 0);
  const totalCols = (sh.data.views||[]).reduce((s,v)=>s + (v.elements||[]).filter(e=>e.type==='column').length, 0);
  info.textContent = `시트: ${sh.data.sheet_number || '?'} | views: ${(sh.data.views||[]).length} | rooms: ${totalRooms} | walls: ${totalWalls} | columns: ${totalCols} | confidence: ${sh.data.global_confidence ?? 'n/a'}`;
  right.appendChild(info);
});
</script>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--pair", action="append", nargs=2, metavar=("JSON", "IMG"), required=True)
    ap.add_argument("--label", action="append", default=[], help="각 pair에 대응하는 라벨 (선택)")
    args = ap.parse_args()

    sheets = []
    for i, (json_path, img_path) in enumerate(args.pair):
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        img_b64 = base64.b64encode(Path(img_path).read_bytes()).decode("ascii")
        label = args.label[i] if i < len(args.label) else f"{Path(img_path).stem} / {Path(json_path).parent.name}"
        sheets.append({"label": label, "img_b64": img_b64, "data": data})

    html = HTML_TEMPLATE.replace("__SHEETS__", json.dumps(sheets, ensure_ascii=False))
    Path(args.out).write_text(html, encoding="utf-8")
    print(f"saved: {args.out}  ({len(sheets)} sheets)")
    print(f"  open: file:///{Path(args.out).as_posix()}")


if __name__ == "__main__":
    main()
