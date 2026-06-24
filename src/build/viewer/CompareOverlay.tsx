import { Maximize2, Minus, Plus, X } from "lucide-react";
import { useState } from "react";
import type { Sheet } from "../../buildSheetsData";

export default function CompareOverlay({
  sheetA,
  sheetB,
  onClose
}: {
  sheetA: Sheet;
  sheetB: Sheet;
  onClose: () => void;
}) {
  const [showPrevious, setShowPrevious] = useState(true);
  const [showCurrent, setShowCurrent] = useState(true);

  return (
    <div className="compare-overlay" aria-label={`비교 결과 ${sheetA.number} 대 ${sheetB.number}`}>
      <div className="compare-canvas static-sheet">
        <span>비교 결과 (정적 데모)</span>
        <div className="drawing-room room-large" />
        <div className="drawing-room room-small" />
        {showPrevious && <div className="compare-diff diff-previous" aria-hidden="true" />}
        {showCurrent && <div className="compare-diff diff-current" aria-hidden="true" />}
      </div>

      <div className="compare-doc-panel" aria-label="비교한 문서">
        <header>
          <strong>비교한 문서</strong>
          <button type="button" className="icon-button" aria-label="비교 닫기" onClick={onClose}>
            <X size={16} aria-hidden="true" />
          </button>
        </header>
        <label className="compare-toggle">
          <input type="checkbox" checked={showPrevious} onChange={(event) => setShowPrevious(event.target.checked)} />
          <span className="compare-swatch swatch-previous" aria-hidden="true" />
          이전 ({sheetA.number})
        </label>
        <label className="compare-toggle">
          <input type="checkbox" checked={showCurrent} onChange={(event) => setShowCurrent(event.target.checked)} />
          <span className="compare-swatch swatch-current" aria-hidden="true" />
          현재 ({sheetB.number})
        </label>
      </div>

      <div className="compare-bottom-controls" aria-label="비교 뷰 컨트롤">
        <button type="button" aria-label="축소">
          <Minus size={18} aria-hidden="true" />
        </button>
        <button type="button" aria-label="확대">
          <Plus size={18} aria-hidden="true" />
        </button>
        <button type="button" aria-label="맞춤">
          <Maximize2 size={18} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}
