import { Search } from "lucide-react";
import type { IssueCategory } from "./viewerData";

export default function IssueAddPanel({
  categories,
  selectedCategoryId,
  onSelectCategory
}: {
  categories: IssueCategory[];
  selectedCategoryId: string | null;
  onSelectCategory: (id: string) => void;
}) {
  return (
    <div className="viewer-panel-section" aria-label="이슈 검색 및 추가">
      <div className="issue-add-search">
        <Search size={15} aria-hidden="true" />
        <input type="text" name="issue-search" aria-label="이슈 검색" placeholder="검색 및 추가" />
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
              <span className="issue-category-count">{category.count}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
