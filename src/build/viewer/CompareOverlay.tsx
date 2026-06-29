import { X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { compareVersions, fileUrl, type CompareResult } from "../../api/drawings";

const MAX_DIM = 1400;

/**
 * S4 시트 비교(§G). 같은 version_set 두 버전을:
 *  (a) 클라이언트 색상 합성 — 이전=빨강/현재=파랑을 캔버스 픽셀로 합성(+투명도·스와이프 슬라이더)
 *  (b) 백엔드 픽셀 diff 마스크 — 변경 영역 하이라이트 토글
 * 두 방식으로 보여준다.
 */
export default function CompareOverlay({
  aLabel,
  bLabel,
  aUrl,
  bUrl,
  fileId,
  againstId,
  sheetIndex,
  onClose
}: {
  aLabel: string;
  bLabel: string;
  aUrl?: string;
  bUrl?: string;
  fileId: string;
  againstId: string;
  sheetIndex: number;
  onClose: () => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgARef = useRef<ImageData | null>(null);
  const imgBRef = useRef<ImageData | null>(null);
  const [ready, setReady] = useState(false);
  const [tainted, setTainted] = useState(false);
  const [showPrev, setShowPrev] = useState(true);
  const [showCur, setShowCur] = useState(true);
  const [opacity, setOpacity] = useState(0.5); // 현재(B) 비중
  const [swipe, setSwipe] = useState(100); // 100=전체 합성, <100이면 좌측 A / 우측 B 와이프
  const [diff, setDiff] = useState<CompareResult | null>(null);
  const [showDiff, setShowDiff] = useState(false);
  const [diffError, setDiffError] = useState<string | null>(null);

  // 백엔드 diff 마스크 + 변경 통계 조회.
  useEffect(() => {
    let alive = true;
    compareVersions(fileId, againstId, sheetIndex)
      .then((r) => alive && setDiff(r))
      .catch((e) => alive && setDiffError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, [fileId, againstId, sheetIndex]);

  // 두 PNG 로드 → ImageData 추출(A 크기로 정규화).
  useEffect(() => {
    const a = aUrl ?? fileUrl(diff?.png_a_url);
    const b = bUrl ?? fileUrl(diff?.png_b_url);
    if (!a || !b) return;
    let alive = true;
    const load = (src: string) =>
      new Promise<HTMLImageElement>((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => resolve(img);
        img.onerror = reject;
        // 일반 <img>가 CORS 헤더 없이 캐시한 응답을 crossOrigin 요청이 재사용하면
        // taint된다. 쿼리로 캐시 키를 분리해 Origin 포함 요청이 ACAO를 받게 한다.
        img.src = src + (src.includes("?") ? "&" : "?") + "cors=1";
      });
    Promise.all([load(a), load(b)])
      .then(([ia, ib]) => {
        if (!alive) return;
        let w = ia.naturalWidth;
        let h = ia.naturalHeight;
        const s = Math.min(1, MAX_DIM / Math.max(w, h));
        w = Math.round(w * s);
        h = Math.round(h * s);
        const tmp = document.createElement("canvas");
        tmp.width = w;
        tmp.height = h;
        const tctx = tmp.getContext("2d", { willReadFrequently: true })!;
        try {
          tctx.drawImage(ia, 0, 0, w, h);
          imgARef.current = tctx.getImageData(0, 0, w, h);
          tctx.clearRect(0, 0, w, h);
          tctx.drawImage(ib, 0, 0, w, h);
          imgBRef.current = tctx.getImageData(0, 0, w, h);
          const cv = canvasRef.current!;
          cv.width = w;
          cv.height = h;
          setReady(true);
        } catch {
          // 캔버스 오염(CORS) → 색상 합성 불가, 단순 교차페이드로 폴백.
          setTainted(true);
        }
      })
      .catch(() => {
        if (!alive) return;
        // 이미지 로드 하드 실패: 스피너를 닫고 폴백/에러를 노출(무한 로딩 방지).
        setTainted(true);
        setDiffError("비교 이미지를 불러오지 못했습니다.");
      });
    return () => {
      alive = false;
    };
  }, [aUrl, bUrl, diff?.png_a_url, diff?.png_b_url]);

  // 색상 합성 렌더.
  const render = useCallback(() => {
    const cv = canvasRef.current;
    const A = imgARef.current;
    const B = imgBRef.current;
    if (!cv || !A || !B) return;
    const ctx = cv.getContext("2d")!;
    const w = cv.width;
    const h = cv.height;
    const out = ctx.createImageData(w, h);
    const da = A.data;
    const db = B.data;
    const od = out.data;
    const swipeX = (swipe / 100) * w;
    for (let i = 0; i < od.length; i += 4) {
      const px = (i / 4) % w;
      // 스와이프: 경계 왼쪽은 A만, 오른쪽은 B만(100이면 전체 합성)
      const inA = showPrev && (swipe >= 100 || px <= swipeX);
      const inB = showCur && (swipe >= 100 || px > swipeX);
      const aLine = inA ? (255 - (da[i] * 0.299 + da[i + 1] * 0.587 + da[i + 2] * 0.114)) / 255 : 0;
      const bLineRaw = inB ? (255 - (db[i] * 0.299 + db[i + 1] * 0.587 + db[i + 2] * 0.114)) / 255 : 0;
      // 투명도 슬라이더: A=(1-opacity), B=opacity 가중
      const aW = aLine * (1 - opacity) * 2;
      const bW = bLineRaw * opacity * 2;
      od[i] = 255 - Math.min(255, bW * 255); // 빨강: B선이 줄임
      od[i + 1] = 255 - Math.min(255, Math.max(aW, bW) * 255); // 초록: 둘 다 줄임
      od[i + 2] = 255 - Math.min(255, aW * 255); // 파랑: A선이 줄임
      od[i + 3] = 255;
    }
    ctx.putImageData(out, 0, 0);
  }, [opacity, swipe, showPrev, showCur]);

  useEffect(() => {
    if (ready) render();
  }, [ready, render]);

  const changedPct = diff ? (diff.changed_ratio * 100).toFixed(2) : null;

  return (
    <div className="compare-overlay" aria-label={`비교 결과 ${aLabel} 대 ${bLabel}`}>
      <div className="compare-canvas-wrap">
        {tainted ? (
          <div className="compare-fallback">
            <img src={aUrl ?? fileUrl(diff?.png_a_url)} alt={`${aLabel} 도면`} style={{ opacity: 1 - opacity }} />
            <img src={bUrl ?? fileUrl(diff?.png_b_url)} alt={`${bLabel} 도면`} style={{ opacity }} className="compare-fallback-top" />
          </div>
        ) : (
          <>
            <canvas ref={canvasRef} className="compare-canvas" aria-label="버전 색상 합성" />
            {showDiff && diff?.mask_url ? (
              <img className="compare-diff-mask" src={fileUrl(diff.mask_url)} alt="변경 영역 마스크" />
            ) : null}
          </>
        )}
        {!ready && !tainted ? (
          <div className="vector-status" role="status">
            <span>비교 이미지 합성 중...</span>
          </div>
        ) : null}
      </div>

      <div className="compare-doc-panel" aria-label="비교한 문서">
        <header>
          <strong>버전 비교</strong>
          <button type="button" className="icon-button" aria-label="비교 닫기" onClick={onClose}>
            <X size={16} aria-hidden="true" />
          </button>
        </header>

        <label className="compare-toggle">
          <input type="checkbox" checked={showPrev} onChange={(e) => setShowPrev(e.target.checked)} />
          <span className="compare-swatch swatch-previous" aria-hidden="true" />
          이전 ({aLabel})
        </label>
        <label className="compare-toggle">
          <input type="checkbox" checked={showCur} onChange={(e) => setShowCur(e.target.checked)} />
          <span className="compare-swatch swatch-current" aria-hidden="true" />
          현재 ({bLabel})
        </label>

        <label className="compare-slider">
          <span>투명도 (이전 ↔ 현재)</span>
          <input
            type="range"
            min={0}
            max={100}
            value={Math.round(opacity * 100)}
            aria-label="투명도"
            onChange={(e) => setOpacity(Number(e.target.value) / 100)}
          />
        </label>
        <label className="compare-slider">
          <span>스와이프</span>
          <input
            type="range"
            min={0}
            max={100}
            value={swipe}
            aria-label="스와이프"
            onChange={(e) => setSwipe(Number(e.target.value))}
          />
        </label>

        <hr />
        <label className="compare-toggle">
          <input
            type="checkbox"
            checked={showDiff}
            disabled={!diff?.mask_url}
            onChange={(e) => setShowDiff(e.target.checked)}
          />
          변경 영역 강조 (백엔드 diff)
        </label>
        {changedPct != null ? (
          <p className="compare-stat">변경 픽셀 {changedPct}%</p>
        ) : diffError ? (
          <p className="compare-slot-note compare-error">{diffError}</p>
        ) : (
          <p className="compare-stat">diff 계산 중...</p>
        )}
      </div>
    </div>
  );
}
