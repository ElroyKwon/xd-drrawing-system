import { X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { Sheet } from "../../buildSheetsData";
import { listDrawingVersions, type Drawing } from "../../api/drawings";
import { useModalDismiss } from "../../hooks/useModalDismiss";

export default function CompareModal({
  currentSheet,
  onClose,
  onCompare
}: {
  currentSheet: Sheet;
  onClose: () => void;
  onCompare: (against: Drawing) => void;
}) {
  const dialogRef = useRef<HTMLDivElement>(null);
  useModalDismiss(onClose, dialogRef);

  const [versions, setVersions] = useState<Drawing[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string>("");

  useEffect(() => {
    const fileId = currentSheet.fileId;
    if (!fileId) {
      setError("이 시트는 버전 비교를 지원하지 않습니다.");
      return;
    }
    let alive = true;
    listDrawingVersions(fileId)
      .then((rows) => alive && setVersions(rows))
      .catch((e) => alive && setError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, [currentSheet.fileId]);

  // 현재 버전을 제외한 비교 후보(같은 version_set).
  const others = versions.filter((v) => v.file_id !== currentSheet.fileId);
  const selected = others.find((v) => v.file_id === selectedId) || null;

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        ref={dialogRef}
        tabIndex={-1}
        className="compare-modal"
        role="dialog"
        aria-modal="true"
        aria-label="시트 비교"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <h2>버전 비교</h2>
          <button type="button" className="modal-close" aria-label="닫기" onClick={onClose}>
            <X size={18} aria-hidden="true" />
          </button>
        </header>

        <div className="compare-slots">
          <div className="compare-slot">
            <span className="compare-slot-kicker">현재 (시트 A)</span>
            <strong>{currentSheet.number}</strong>
            <span className="compare-slot-sub">버전 {currentSheet.version}</span>
          </div>

          <div className="compare-slot">
            <span className="compare-slot-kicker">비교 대상 (시트 B)</span>
            <label className="field">
              <span>다른 버전 선택</span>
              <select
                name="compare-version"
                aria-label="비교 버전 선택"
                value={selectedId}
                onChange={(event) => setSelectedId(event.target.value)}
                disabled={others.length === 0}
              >
                <option value="">버전 선택</option>
                {others.map((v) => (
                  <option key={v.file_id} value={v.file_id}>
                    버전 {v.version}{v.is_latest ? " (최신)" : ""}
                  </option>
                ))}
              </select>
            </label>
            {others.length === 0 && !error ? (
              <p className="compare-slot-note">비교할 다른 버전이 없습니다. 파일 관리에서 새 버전을 올리세요.</p>
            ) : null}
            {error ? <p className="compare-slot-note compare-error">{error}</p> : null}
          </div>
        </div>

        <footer className="modal-footer">
          <button type="button" className="ghost-action" onClick={onClose}>
            취소
          </button>
          <button
            type="button"
            className="primary-action"
            disabled={!selected}
            onClick={() => selected && onCompare(selected)}
          >
            비교
          </button>
        </footer>
      </div>
    </div>
  );
}
