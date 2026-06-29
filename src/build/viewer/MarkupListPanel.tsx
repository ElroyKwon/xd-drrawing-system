import type { Markup } from "../../api/drawings";
import { markupColorFilters, markupKindFilters, markupWeightFilters } from "./viewerData";

function shortDate(iso: string): string {
  return iso ? iso.slice(0, 10) : "";
}

export default function MarkupListPanel({
  markups,
  selectedMarkupId,
  isLog,
  onSelectMarkup
}: {
  markups: Markup[];
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

      {markups.length === 0 ? (
        <p className="viewer-empty" role="status">
          아직 마크업이 없습니다. 도구를 선택해 도면 위에 그려보세요.
        </p>
      ) : (
        <ul className="markup-list">
          {markups.map((markup) => (
            <li key={markup.markup_id}>
              <button
                type="button"
                className="markup-list-item"
                aria-pressed={selectedMarkupId === markup.markup_id}
                onClick={() => onSelectMarkup(markup.markup_id)}
              >
                <span
                  className="markup-list-thumb"
                  style={{ background: markup.style?.color || "#d8232a" }}
                  aria-hidden="true"
                />
                <span className="markup-list-text">
                  <strong>{markup.kind}</strong>
                  <span>{markup.text || `${markup.kind} 마크업`}</span>
                </span>
                <span className="markup-list-meta">
                  <span>{markup.author}</span>
                  <span>{shortDate(markup.created_at)}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
