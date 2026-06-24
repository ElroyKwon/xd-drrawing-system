import { X } from "lucide-react";
import type { MeasureRow, MeasureType } from "./viewerData";

export default function MeasurePanel({
  measureTypes,
  activeMeasureType,
  measureRows,
  onSelectMeasureType,
  onCalibrate,
  onClose
}: {
  measureTypes: MeasureType[];
  activeMeasureType: MeasureType;
  measureRows: MeasureRow[];
  onSelectMeasureType: (type: MeasureType) => void;
  onCalibrate: () => void;
  onClose: () => void;
}) {
  return (
    <aside className="viewer-aside" aria-label="측정 교정">
      <header className="viewer-aside-head">
        <div>
          <span className="viewer-aside-kicker">측정</span>
          <strong>교정</strong>
        </div>
        <button type="button" className="icon-button" aria-label="측정 패널 닫기" onClick={onClose}>
          <X size={16} aria-hidden="true" />
        </button>
      </header>

      <div className="measure-settings">
        <label>
          <span>축척 설정</span>
          <select aria-label="축척 설정" defaultValue={`1/2"=1'-0"`}>
            <option>{`1/2"=1'-0"`}</option>
            <option>{`1/4"=1'-0"`}</option>
            <option>1:50</option>
            <option>1:100</option>
          </select>
        </label>
        <label>
          <span>단위 설정</span>
          <select aria-label="단위 설정" defaultValue="밀리미터 (mm)">
            <option>밀리미터 (mm)</option>
            <option>미터 (m)</option>
            <option>피트 (ft)</option>
          </select>
        </label>
      </div>

      <div className="measure-types" role="group" aria-label="측정 타입">
        {measureTypes.map((type) => (
          <button
            key={type}
            type="button"
            aria-pressed={activeMeasureType === type}
            onClick={() => onSelectMeasureType(type)}
          >
            {type}
          </button>
        ))}
      </div>

      <ul className="measure-rows" aria-label="측정값">
        {measureRows.map((row) => (
          <li key={row.id}>
            <span className="measure-marker">{row.marker}</span>
            <span className="measure-type-label">{row.type}</span>
            <span className="measure-value">{row.value}</span>
          </li>
        ))}
      </ul>

      <div className="measure-actions">
        <button type="button" className="ghost-action" aria-label="측정값 추가">
          측정값 추가
        </button>
        <button type="button" className="secondary-action" onClick={onCalibrate}>
          교정
        </button>
      </div>
    </aside>
  );
}
