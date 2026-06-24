import type { DemoMarkup } from "./viewerData";
import { markupColorFilters, markupKindFilters, markupWeightFilters } from "./viewerData";

export default function MarkupListPanel({
  markups,
  selectedMarkupId,
  isLog,
  onSelectMarkup
}: {
  markups: DemoMarkup[];
  selectedMarkupId: string | null;
  isLog: boolean;
  onSelectMarkup: (id: string) => void;
}) {
  return (
    <div className="viewer-panel-section" aria-label={isLog ? "마크업 로그" : "마크업 목록"}>
      {isLog && (
        <div className="markup-log-filters">
          <label>
            <span>색상</span>
            <select aria-label="색상 필터" defaultValue={markupColorFilters[0]}>
              {markupColorFilters.map((opt) => (
                <option key={opt}>{opt}</option>
              ))}
            </select>
          </label>
          <label>
            <span>굵기</span>
            <select aria-label="굵기 필터" defaultValue={markupWeightFilters[0]}>
              {markupWeightFilters.map((opt) => (
                <option key={opt}>{opt}</option>
              ))}
            </select>
          </label>
          <label>
            <span>유형</span>
            <select aria-label="유형 필터" defaultValue={markupKindFilters[0]}>
              {markupKindFilters.map((opt) => (
                <option key={opt}>{opt}</option>
              ))}
            </select>
          </label>
        </div>
      )}

      <ul className="markup-list">
        {markups.map((markup) => (
          <li key={markup.id}>
            <button
              type="button"
              className="markup-list-item"
              aria-pressed={selectedMarkupId === markup.id}
              onClick={() => onSelectMarkup(markup.id)}
            >
              <span className="markup-list-thumb" style={{ background: markup.color }} aria-hidden="true" />
              <span className="markup-list-text">
                <strong>{markup.kind}</strong>
                <span>{markup.label}</span>
              </span>
              <span className="markup-list-meta">
                <span>{markup.author}</span>
                <span>{markup.date}</span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
