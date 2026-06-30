import { MapPin, X } from "lucide-react";
import { useState, type FormEvent } from "react";
import { issueTypes, type IssueCategory } from "./viewerData";

/**
 * S5: 뷰어에서 핀을 찍은 뒤 인라인으로 이슈를 작성하는 패널.
 * 핀 좌표(coord_space)는 SheetViewerShell이 캔버스에서 산출해 주입한다.
 */
export default function IssueCreateForm({
  coordLabel,
  categories,
  defaultCategoryId,
  onSubmit,
  onCancel
}: {
  coordLabel: string;
  categories: IssueCategory[];
  defaultCategoryId: string | null;
  onSubmit: (input: { title: string; type: string; category: string; assignee: string }) => void;
  onCancel: () => void;
}) {
  const [title, setTitle] = useState("");
  const [type, setType] = useState<string>("현장 확인");
  const [category, setCategory] = useState<string>(defaultCategoryId ?? categories[0]?.id ?? "");
  const [assignee, setAssignee] = useState("도면 검토자");
  const [error, setError] = useState(false);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!title.trim()) {
      setError(true);
      return;
    }
    onSubmit({ title: title.trim(), type, category, assignee });
  }

  return (
    <aside className="viewer-aside issue-create-form" aria-label="이슈 작성">
      <header className="viewer-aside-head">
        <h2>
          <MapPin size={15} aria-hidden="true" /> 이슈 핀 작성
        </h2>
        <button type="button" className="modal-close" aria-label="닫기" onClick={onCancel}>
          <X size={18} />
        </button>
      </header>
      <form onSubmit={submit}>
        <label className="field">
          <span>제목 <b aria-hidden="true">*</b></span>
          <input
            name="issue-title"
            aria-label="이슈 제목"
            value={title}
            autoFocus
            aria-invalid={error}
            onChange={(e) => {
              setTitle(e.target.value);
              if (e.target.value.trim()) setError(false);
            }}
            placeholder="예: 현장 패널 번호와 도면 표기가 다름"
          />
          {error ? <span className="field-error">제목을 입력하세요.</span> : null}
        </label>
        <label className="field select-field">
          <span>유형</span>
          <select name="issue-type" value={type} onChange={(e) => setType(e.target.value)}>
            {issueTypes.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </label>
        <label className="field select-field">
          <span>카테고리</span>
          <select name="issue-category" value={category} onChange={(e) => setCategory(e.target.value)}>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>담당자</span>
          <input name="issue-assignee" value={assignee} onChange={(e) => setAssignee(e.target.value)} />
        </label>
        <p className="issue-coord-hint">핀 위치: {coordLabel}</p>
        <div className="viewer-aside-actions">
          <button type="button" className="secondary-action" onClick={onCancel}>취소</button>
          <button type="submit" className="primary-action">이슈 작성</button>
        </div>
      </form>
    </aside>
  );
}
