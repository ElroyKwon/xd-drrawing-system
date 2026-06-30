import { MapPin, Search } from "lucide-react";
import { useState } from "react";
import type { Issue } from "../../api/drawings";
import type { IssueCategory } from "./viewerData";

const STATUS_DOT: Record<string, string> = {
  열림: "#e8590c",
  진행중: "#1971c2",
  답변됨: "#2f9e44",
  닫힘: "#868e96"
};

/**
 * S5: 뷰어 좌측 "이슈" 탭. 카테고리별 실집계 count(검색 및 추가) +
 * 이 시트의 이슈 목록(핀 선택). 정적 count 시드는 제거됐다.
 */
export default function IssueAddPanel({
  categories,
  counts,
  selectedCategoryId,
  onSelectCategory,
  issues,
  selectedIssueId,
  onSelectIssue
}: {
  categories: IssueCategory[];
  counts: Record<string, number>;
  selectedCategoryId: string | null;
  onSelectCategory: (id: string) => void;
  issues: Issue[];
  selectedIssueId: string | null;
  onSelectIssue: (id: string) => void;
}) {
  const [query, setQuery] = useState("");
  const normalized = query.trim().toLowerCase();
  const visible = normalized
    ? issues.filter((i) => i.title.toLowerCase().includes(normalized))
    : issues;

  return (
    <div className="viewer-panel-section" aria-label="이슈 검색 및 추가">
      <div className="issue-add-search">
        <Search size={15} aria-hidden="true" />
        <input
          type="text"
          name="issue-search"
          aria-label="이슈 검색"
          placeholder="검색 및 추가"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      <ul className="issue-category-list">
        {categories.map((category) => (
          <li key={category.id}>
            <button
              type="button"
              className="issue-category-item"
              aria-pressed={selectedCategoryId === category.id}
              onClick={() => onSelectCategory(category.id)}
            >
              <span className="issue-category-text">
                <strong>{category.name}</strong>
                <span>{category.description}</span>
              </span>
              <span className="issue-category-count">{counts[category.id] ?? 0}</span>
            </button>
          </li>
        ))}
      </ul>

      <div className="issue-sheet-list" aria-label="이 시트의 이슈">
        <h3 className="issue-sheet-list-head">이 시트의 이슈 ({visible.length})</h3>
        {visible.length === 0 ? (
          <p className="issue-empty">이슈 핀 도구로 도면 위에 이슈를 추가하세요.</p>
        ) : (
          <ul>
            {visible.map((issue) => (
              <li key={issue.issue_id}>
                <button
                  type="button"
                  className="issue-row-item"
                  aria-pressed={selectedIssueId === issue.issue_id}
                  onClick={() => onSelectIssue(issue.issue_id)}
                >
                  <span className="issue-status-dot" style={{ background: STATUS_DOT[issue.status] ?? "#868e96" }} aria-hidden="true" />
                  {issue.pin ? <MapPin size={13} aria-hidden="true" /> : null}
                  <span className="issue-row-text">
                    <strong>{issue.title}</strong>
                    <span>{issue.type} · {issue.status}</span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
