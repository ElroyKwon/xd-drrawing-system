"""
build_final_report.py — 모든 treatment를 한 화면에 비교하는 최종 리포트 viewer.

각 sheet에 대해 원본 + 여러 treatment(baseline/B/D/C/A)의 Canvas 재구성을 나란히 표시.
집계 통계(views, rooms, walls, dims) 포함.

사용:
  python build_final_report.py <out.html> --sheet p060 <orig.png> --entry label json1 --entry label json2 ... --sheet p062 <orig.png> --entry ...

간단히 하드코딩 버전:
  python build_final_report.py <out.html>
"""
import argparse
import base64
import json
from pathlib import Path


ROOT = Path(r"D:/_Project/prototype-도면지식관리-mvp")
OUT = ROOT / "docs" / "ai-3d-builder" / "outputs"


SHEETS = [
    {
        "sheet_id": "p060",
        "original_png": ROOT / "dwg" / "1) 건축공사" / "0. PDF 도면" / "_png_dpi400" / "arch_p060.png",
        "entries": [
            ("Baseline Opus (단일)", OUT / "2026-04-21_100010_arch_p060_opus" / "stage-10-parsed.json"),
            ("Baseline Gemini", OUT / "2026-04-21_100820_arch_p060_gemini-3.1-flash-image" / "stage-10-parsed.json"),
            ("B: Opus↔Gemini (hop2)", OUT / "2026-04-21_112440_arch_p060_opus_ref_hop2" / "stage-10-parsed.json"),
            ("D: Opus Multistage", OUT / "2026-04-21_112443_arch_p060_opus_multistage" / "stage-10-parsed.json"),
            ("C: Opus+Gemini 합의", OUT / "consensus" / "consensus_p060.json"),
            ("A: D + Critique", OUT / "critique" / "p060_critiqued" / "stage-10-parsed.json"),
        ],
    },
    {
        "sheet_id": "p062",
        "original_png": ROOT / "dwg" / "1) 건축공사" / "0. PDF 도면" / "_png_dpi400" / "arch_p062.png",
        "entries": [
            ("Baseline Opus (단일)", OUT / "2026-04-21_101145_arch_p062_opus" / "stage-10-parsed.json"),
            ("Baseline Gemini", OUT / "2026-04-21_101237_arch_p062_gemini-3.1-flash-image" / "stage-10-parsed.json"),
            ("B: Opus↔Gemini (hop2)", OUT / "2026-04-21_112442_arch_p062_opus_ref_hop2" / "stage-10-parsed.json"),
            ("D: Opus Multistage", OUT / "2026-04-21_112444_arch_p062_opus_multistage" / "stage-10-parsed.json"),
            ("C: Opus+Gemini 합의", OUT / "consensus" / "consensus_p062.json"),
            ("A: D + Critique", OUT / "critique" / "p062_critiqued" / "stage-10-parsed.json"),
        ],
    },
]


HTML = r"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"><title>최종 비교 리포트</title>
<style>
  *{box-sizing:border-box;}
  body{margin:0;font-family:'Malgun Gothic','맑은 고딕',sans-serif;background:#0f0f0f;color:#ddd;}
  header{position:sticky;top:0;z-index:10;padding:10px 16px;background:#000;border-bottom:1px solid #333;display:flex;gap:20px;align-items:center;}
  header strong{font-size:15px;color:#fff;}
  header .meta{color:#888;font-size:12px;}
  table.stats{border-collapse:collapse;margin:8px 16px;font-size:12px;background:#111;}
  table.stats th,table.stats td{border:1px solid #333;padding:5px 10px;text-align:center;}
  table.stats th{background:#1a1a1a;color:#ccc;font-weight:normal;}
  table.stats td.sheet{background:#1a1a1a;color:#fa8;text-align:left;}
  .sheet-row{display:grid;gap:4px;padding:4px;background:#0a0a0a;border-top:3px solid #333;}
  .cell{background:#fff;border:1px solid #444;overflow:hidden;display:flex;flex-direction:column;}
  .cell h3{margin:0;padding:5px 8px;font-size:11px;background:#222;color:#ddd;border-bottom:1px solid #444;}
  .cell h3 .lbl{color:#fa8;font-weight:bold;}
  .imgbox{flex:1;overflow:auto;background:#fff;padding:2px;}
  img.orig{max-width:100%;display:block;}
  canvas{display:block;}
  .views{display:flex;flex-direction:column;}
  .view-block{border-bottom:1px solid #ccc;padding:4px;}
  .view-block h4{margin:0 0 2px 0;font-size:10px;color:#345;}
  .info{padding:3px 8px;background:#eef;font-size:10px;color:#357;border-top:1px solid #ccd;}
</style></head><body>
<header>
  <strong>AI 3D Builder — treatment 비교 리포트</strong>
  <span class="meta">각 시트 × 원본 + 6개 treatment · Canvas 재구성 · 집계 포함</span>
</header>
<div id="stats"></div>
<div id="sheets"></div>
<script>
const SHEETS = __SHEETS__;

function cumsum(arr,fb){const out=[0];let s=0;for(const v of arr){s+=(v==null?fb:v);out.push(s);}return out;}
function buildAxis(labels,spacings,fb){
  labels=labels||[]; const sp=(spacings||[]).slice(0,Math.max(0,labels.length-1));
  while(sp.length<labels.length-1)sp.push(null);
  const positions=cumsum(sp,fb); const map={}; labels.forEach((l,i)=>map[l]=positions[i]);
  return {labels,positions,map};
}
function renderView(container,view,targetW){
  const g=view.grid||{};
  const xA=buildAxis(g.x_labels||[], g.x_spacings_mm||[], 3000);
  const yA=buildAxis(g.y_labels||[], g.y_spacings_mm||[], 3000);
  const wrap=document.createElement('div'); wrap.className='view-block';
  const h=document.createElement('h4');
  h.textContent=`${view.view_id||''} ${view.view_label||''} ${view.view_scale||''}`;
  wrap.appendChild(h);
  if(!xA.positions.length||!yA.positions.length){
    const p=document.createElement('div'); p.style.fontSize='10px'; p.style.color='#a00';
    p.textContent='(grid 누락)'; wrap.appendChild(p); container.appendChild(wrap); return;
  }
  const pad=4000;
  const wMin=-pad, wMax=xA.positions[xA.positions.length-1]+pad;
  const hMin=-pad, hMax=yA.positions[yA.positions.length-1]+pad;
  const worldW=wMax-wMin, worldH=hMax-hMin;
  const scale=targetW/worldW;
  const canvas=document.createElement('canvas');
  canvas.width=targetW; canvas.height=Math.round(worldH*scale);
  wrap.appendChild(canvas); container.appendChild(wrap);
  const ctx=canvas.getContext('2d');
  function W2C(x,y){return [(x-wMin)*scale,(y-hMin)*scale];}
  function gp(g){if(!g||g.length<2)return null;const wx=xA.map[g[0]],wy=yA.map[g[1]];if(wx==null||wy==null)return null;return W2C(wx,wy);}
  ctx.strokeStyle='#bbf'; ctx.fillStyle='#669'; ctx.lineWidth=0.5; ctx.font='9px sans-serif'; ctx.setLineDash([4,4]);
  xA.positions.forEach((x,i)=>{const[cx]=W2C(x,hMin);ctx.beginPath();ctx.moveTo(cx,0);ctx.lineTo(cx,canvas.height);ctx.stroke();ctx.fillText(xA.labels[i]||'?',cx+1,10);});
  yA.positions.forEach((y,i)=>{const[,cy]=W2C(wMin,y);ctx.beginPath();ctx.moveTo(0,cy);ctx.lineTo(canvas.width,cy);ctx.stroke();ctx.fillText(yA.labels[i]||'?',1,cy-1);});
  ctx.setLineDash([]);
  (view.elements||[]).filter(e=>e.type==='room'&&e.polygon_grid).forEach(rm=>{
    const pts=rm.polygon_grid.map(gp).filter(Boolean); if(pts.length<3)return;
    ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
    for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]); ctx.closePath();
    ctx.fillStyle='rgba(100,150,200,0.22)'; ctx.strokeStyle='rgba(60,100,160,0.9)'; ctx.lineWidth=1;
    ctx.fill(); ctx.stroke();
    const cx=pts.reduce((s,p)=>s+p[0],0)/pts.length, cy=pts.reduce((s,p)=>s+p[1],0)/pts.length;
    ctx.fillStyle='#234'; ctx.font='bold 9px Malgun Gothic,sans-serif'; ctx.textAlign='center';
    ctx.fillText(rm.name||rm.id||'',cx,cy); ctx.textAlign='left';
  });
  ctx.strokeStyle='#222';
  (view.elements||[]).filter(e=>e.type==='wall'&&e.path_grid).forEach(w=>{
    const pts=w.path_grid.map(gp).filter(Boolean); if(pts.length<2)return;
    ctx.lineWidth=Math.max(2,(w.thickness_mm||200)*scale);
    ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
    for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]); ctx.stroke();
  });
  ctx.lineWidth=1;
  (view.elements||[]).filter(e=>e.type==='shaft'&&e.polygon_grid).forEach(sh=>{
    const pts=sh.polygon_grid.map(gp).filter(Boolean); if(pts.length<3)return;
    ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
    for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]); ctx.closePath();
    ctx.fillStyle='rgba(160,80,200,0.4)'; ctx.strokeStyle='#624'; ctx.fill(); ctx.stroke();
  });
  ctx.fillStyle='#080'; ctx.font='8px sans-serif';
  (view.dimensions_raw||[]).forEach(d=>{
    const a=gp(d.from_grid),b=gp(d.to_grid); if(!a||!b)return;
    const mx=(a[0]+b[0])/2, my=(a[1]+b[1])/2;
    ctx.fillText(d.text,mx,my-2);
  });
}

function tally(data){
  let rooms=0, walls=0, dims=0, dimsAnchored=0;
  (data.views||[]).forEach(v=>{
    (v.elements||[]).forEach(e=>{
      if(e.type==='room') rooms++; else if(e.type==='wall') walls++;
    });
    (v.dimensions_raw||[]).forEach(d=>{
      dims++;
      if(d.from_grid && d.to_grid) dimsAnchored++;
    });
  });
  return {views:(data.views||[]).length, rooms, walls, dims, dimsAnchored};
}

// stats table
const statsDiv=document.getElementById('stats');
const tbl=document.createElement('table'); tbl.className='stats';
const hdr=document.createElement('tr');
hdr.innerHTML='<th>Sheet</th><th>Treatment</th><th>Views</th><th>Rooms</th><th>Walls</th><th>Dims</th><th>Dims (grid 앵커)</th>';
tbl.appendChild(hdr);
SHEETS.forEach(sh=>{
  sh.entries.forEach((en,i)=>{
    const row=document.createElement('tr');
    const t=tally(en.data);
    const sheetCell=(i===0?`<td class="sheet" rowspan="${sh.entries.length}">${sh.sheet_id}</td>`:'');
    row.innerHTML=`${sheetCell}<td>${en.label}</td><td>${t.views}</td><td>${t.rooms}</td><td>${t.walls}</td><td>${t.dims}</td><td>${t.dimsAnchored}</td>`;
    tbl.appendChild(row);
  });
});
statsDiv.appendChild(tbl);

// per-sheet rows
const sheetsBox=document.getElementById('sheets');
SHEETS.forEach(sh=>{
  const row=document.createElement('div'); row.className='sheet-row';
  // n+1 cells: original + n treatments
  const n=sh.entries.length;
  row.style.gridTemplateColumns=`repeat(${n+1}, minmax(0,1fr))`;
  // original
  const orig=document.createElement('div'); orig.className='cell';
  orig.innerHTML=`<h3><span class="lbl">${sh.sheet_id}</span> 원본</h3><div class="imgbox"><img class="orig" src="data:image/png;base64,${sh.origB64}"></div>`;
  row.appendChild(orig);
  sh.entries.forEach(en=>{
    const c=document.createElement('div'); c.className='cell';
    c.innerHTML=`<h3><span class="lbl">${en.label}</span></h3>`;
    const box=document.createElement('div'); box.className='imgbox';
    const views=document.createElement('div'); views.className='views';
    box.appendChild(views); c.appendChild(box);
    (en.data.views||[]).forEach(v=>renderView(views,v,400));
    const t=tally(en.data);
    const info=document.createElement('div'); info.className='info';
    info.textContent=`views:${t.views} rooms:${t.rooms} walls:${t.walls} dims:${t.dims} (앵커:${t.dimsAnchored})`;
    c.appendChild(info);
    row.appendChild(c);
  });
  sheetsBox.appendChild(row);
});
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_html")
    args = ap.parse_args()

    sheets_data = []
    for sh in SHEETS:
        orig_b64 = base64.b64encode(sh["original_png"].read_bytes()).decode("ascii")
        entries = []
        for label, jpath in sh["entries"]:
            if jpath.exists():
                data = json.loads(jpath.read_text(encoding="utf-8"))
            else:
                data = {"_missing": str(jpath), "views": []}
            entries.append({"label": label, "path": str(jpath), "data": data})
        sheets_data.append({"sheet_id": sh["sheet_id"], "origB64": orig_b64, "entries": entries})

    html = HTML.replace("__SHEETS__", json.dumps(sheets_data, ensure_ascii=False))
    Path(args.out_html).write_text(html, encoding="utf-8")
    print(f"saved: {args.out_html}")
    missing = [(s["sheet_id"], e["label"]) for s in sheets_data for e in s["entries"] if "_missing" in e["data"]]
    if missing:
        print(f"missing: {missing}")


if __name__ == "__main__":
    main()
