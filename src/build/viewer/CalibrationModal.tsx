import { X } from "lucide-react";
import { useRef } from "react";
import type { VectorUnits } from "../../api/drawings";
import { useModalDismiss } from "../../hooks/useModalDismiss";

export default function CalibrationModal({
  units,
  onClose,
  onConfirm
}: {
  units?: VectorUnits;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const dialogRef = useRef<HTMLDivElement>(null);
  useModalDismiss(onClose, dialogRef);

  const known = units && units.to_meter != null;

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        ref={dialogRef}
        tabIndex={-1}
        className="calibration-modal"
        role="dialog"
        aria-modal="true"
        aria-label="도면 단위 확인"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <h2>도면 단위 확인</h2>
          <button type="button" className="modal-close" aria-label="닫기" onClick={onClose}>
            <X size={18} aria-hidden="true" />
          </button>
        </header>

        <div className="modal-body">
          {known ? (
            <>
              <p className="modal-desc">
                이 DXF 도면의 단위는 <strong>$INSUNITS</strong>에서 자동으로 읽어 실척으로 환산합니다.
                별도 수동 교정 없이 측정값이 실제 길이/면적으로 계산됩니다.
              </p>
              <dl className="viewer-prop-list">
                <div className="viewer-prop-row">
                  <dt>도면 단위</dt>
                  <dd>{units!.name}</dd>
                </div>
                <div className="viewer-prop-row">
                  <dt>INSUNITS 코드</dt>
                  <dd>{units!.insunits}</dd>
                </div>
                <div className="viewer-prop-row">
                  <dt>1 단위 = 미터</dt>
                  <dd>{units!.to_meter}</dd>
                </div>
              </dl>
            </>
          ) : (
            <p className="modal-desc">
              이 도면은 단위 정보($INSUNITS)가 없어 측정값을 도면 단위 그대로 표시합니다.
              수동 2점 캘리브레이션은 후속 단계에서 제공됩니다.
            </p>
          )}
        </div>

        <footer className="modal-footer">
          <button type="button" className="primary-action" onClick={onConfirm}>
            확인
          </button>
        </footer>
      </div>
    </div>
  );
}
