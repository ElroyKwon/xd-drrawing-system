"""
build_canvas_only.py — stage-10 JSON만 Canvas로 렌더 (원본 이미지 없음).
A단계 critique 입력용 — 렌더 결과를 깨끗한 PNG로 추출.

사용:
  python build_canvas_only.py <stage-10.json> <out.html>
"""
import argparse
import json
from pathlib import Path


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><title>Canvas Only</title>
<style>
 body{margin:0;background:#fff;font-family:'Malgun Gothic','맑은 고딕',sans-serif;}
 .views{display:flex;flex-direction:column;gap:1px;background:#333;}
 .view-block{background:#fff;padding:8px;}
 .view-block h4{margin:0 0 4px 0;font-size:12px;color:#234;}
 canvas{display:block;border:1px solid #aaa;}
</style></head><body>
<div id="root"></div>
<script>
const DATA = __DATA__;
function cumsum(arr, fb) { const out=[0]; let s=0; for (const v of arr){ s += (v==null?fb:v); out.push(s);} return out; }
function buildAxis(labels, spacings, fb) {
  const sp = (spacings||[]).slice(0, Math.max(0, labels.length-1));
  while (sp.length < labels.length-1) sp.push(null);
  const positions = cumsum(sp, fb);
  const map = {}; labels.forEach((l,i)=>{map[l]=positions[i];});
  return { labels, positions, map };
}
function renderView(container, view) {
  const xA = buildAxis(view.grid.x_labels||[], view.grid.x_spacings_mm||[], 3000);
  const yA = buildAxis(view.grid.y_labels||[], view.grid.y_spacings_mm||[], 3000);
  const wrap = document.createElement('div'); wrap.className='view-block';
  const h = document.createElement('h4');
  h.textContent = `${view.view_id||''} ${view.view_label||''} ${view.view_scale||''}`;
  wrap.appendChild(h);
  const pad = 4000;
  const wMin=-pad, wMax=xA.positions[xA.positions.length-1]+pad;
  const hMin=-pad, hMax=yA.positions[yA.positions.length-1]+pad;
  const worldW=wMax-wMin, worldH=hMax-hMin;
  const target=800, scale=target/worldW;
  const canvas=document.createElement('canvas');
  canvas.width=target; canvas.height=Math.round(worldH*scale);
  wrap.appendChild(canvas); container.appendChild(wrap);
  const ctx=canvas.getContext('2d');
  function W2C(x,y){return [(x-wMin)*scale,(y-hMin)*scale];}
  ctx.strokeStyle='#bbf'; ctx.fillStyle='#669'; ctx.lineWidth=0.5;
  ctx.font='11px sans-serif'; ctx.setLineDash([4,4]);
  xA.positions.forEach((x,i)=>{const[cx]=W2C(x,hMin);ctx.beginPath();ctx.moveTo(cx,0);ctx.lineTo(cx,canvas.height);ctx.stroke();ctx.fillText(xA.labels[i]||'?',cx+2,12);});
  yA.positions.forEach((y,i)=>{const[,cy]=W2C(wMin,y);ctx.beginPath();ctx.moveTo(0,cy);ctx.lineTo(canvas.width,cy);ctx.stroke();ctx.fillText(yA.labels[i]||'?',2,cy-2);});
  ctx.setLineDash([]);
  function gp(g){if(!g||g.length<2)return null;const wx=xA.map[g[0]],wy=yA.map[g[1]];if(wx==null||wy==null)return null;return W2C(wx,wy);}
  (view.elements||[]).filter(e=>e.type==='room'&&e.polygon_grid).forEach(rm=>{
    const pts=rm.polygon_grid.map(gp).filter(Boolean); if(pts.length<3)return;
    ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
    for(let i=1;i<pts.length;i++) ctx.lineTo(pts[i][0],pts[i][1]);
    ctx.closePath();
    ctx.fillStyle='rgba(100,150,200,0.22)'; ctx.strokeStyle='rgba(60,100,160,0.9)'; ctx.lineWidth=1;
    ctx.fill(); ctx.stroke();
    const cx=pts.reduce((s,p)=>s+p[0],0)/pts.length, cy=pts.reduce((s,p)=>s+p[1],0)/pts.length;
    ctx.fillStyle='#234'; ctx.font='bold 10px Malgun Gothic,sans-serif'; ctx.textAlign='center';
    ctx.fillText(rm.name||rm.id,cx,cy); ctx.textAlign='left';
  });
  (view.elements||[]).filter(e=>e.type==='shaft'&&e.polygon_grid).forEach(sh=>{
    const pts=sh.polygon_grid.map(gp).filter(Boolean); if(pts.length<3)return;
    ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
    for(let i=1;i<pts.length;i++) ctx.lineTo(pts[i][0],pts[i][1]); ctx.closePath();
    ctx.fillStyle='rgba(160,80,200,0.4)'; ctx.strokeStyle='#624'; ctx.fill(); ctx.stroke();
  });
  (view.elements||[]).filter(e=>e.type==='void'&&e.polygon_grid).forEach(v=>{
    const pts=v.polygon_grid.map(gp).filter(Boolean); if(pts.length<3)return;
    ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
    for(let i=1;i<pts.length;i++) ctx.lineTo(pts[i][0],pts[i][1]); ctx.closePath();
    ctx.fillStyle='rgba(200,200,100,0.15)'; ctx.strokeStyle='#960'; ctx.setLineDash([3,3]); ctx.fill(); ctx.stroke(); ctx.setLineDash([]);
  });
  ctx.strokeStyle='#222';
  (view.elements||[]).filter(e=>e.type==='wall'&&e.path_grid).forEach(w=>{
    const pts=w.path_grid.map(gp).filter(Boolean); if(pts.length<2)return;
    ctx.lineWidth=Math.max(2,(w.thickness_mm||200)*scale);
    ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
    for(let i=1;i<pts.length;i++) ctx.lineTo(pts[i][0],pts[i][1]); ctx.stroke();
  });
  ctx.lineWidth=1;
  (view.elements||[]).filter(e=>e.type==='column'&&e.at_grid).forEach(c=>{
    const p=gp(c.at_grid); if(!p) return;
    ctx.fillStyle='rgba(160,40,160,0.7)'; ctx.strokeStyle='#404';
    ctx.beginPath(); ctx.arc(p[0],p[1],4,0,Math.PI*2); ctx.fill(); ctx.stroke();
  });
  (view.elements||[]).filter(e=>e.type==='door').forEach(d=>{
    const a=gp(d.on_wall_from), b=gp(d.on_wall_to); if(!a||!b)return;
    const mx=(a[0]+b[0])/2, my=(a[1]+b[1])/2;
    const wpx=Math.max(6,(d.width_mm||900)*scale);
    ctx.fillStyle='rgba(255,80,80,0.7)'; ctx.strokeStyle='#a00';
    ctx.fillRect(mx-wpx/2,my-4,wpx,8); ctx.strokeRect(mx-wpx/2,my-4,wpx,8);
  });
  ctx.fillStyle='#080'; ctx.font='9px sans-serif';
  (view.dimensions_raw||[]).forEach(d=>{
    const a=gp(d.from_grid),b=gp(d.to_grid); if(!a||!b)return;
    const mx=(a[0]+b[0])/2, my=(a[1]+b[1])/2;
    ctx.fillText(d.text,mx,my-3);
  });
}
const root=document.getElementById('root');
const views=document.createElement('div'); views.className='views'; root.appendChild(views);
(DATA.views||[]).forEach(v=>renderView(views,v));
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_json")
    ap.add_argument("out_html")
    args = ap.parse_args()
    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    Path(args.out_html).write_text(html, encoding="utf-8")
    print(f"saved: {args.out_html}")


if __name__ == "__main__":
    main()
