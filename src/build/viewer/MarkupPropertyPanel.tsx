import { X } from "lucide-react";
import type { DemoMarkup } from "./viewerData";

export default function MarkupPropertyPanel({
  markup,
  onClose
}: {
  markup: DemoMarkup;
  onClose: () => void;
}) {
  return (
    <aside className="viewer-aside" aria-label={`${markup.kind} 마크업 속성`}>
      <header className="viewer-aside-head">
        <div>
          <span className="viewer-aside-kicker">마크업 속성</span>
          <strong>{markup.kind}</strong>
        </div>
        <button type="button" className="icon-button" aria-label="속성 패널 닫기" onClick={onClose}>
          <X size={16} aria-hidden="true" />
        </button>
      </header>

      <dl className="viewer-prop-list">
        {markup.properties.map((prop) => (
          <div key={prop.label} className="viewer-prop-row">
            <dt>{prop.label}</dt>
            <dd>
              {prop.label.includes("색") && prop.value !== "투명" && (
                <span className="prop-swatch" style={{ background: markup.color }} aria-hidden="true" />
              )}
              {prop.value}
            </dd>
          </div>
        ))}
      </dl>

      <footer className="viewer-aside-meta">
        <span>작성자 {markup.author}</span>
        <span>{markup.date}</span>
      </footer>
    </aside>
  );
}
