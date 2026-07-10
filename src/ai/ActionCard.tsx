import { useState } from "react";
import { createIssue, updateIssue, type IssueStatus } from "../api/drawings";
import { createTask, type TaskPriority } from "../api/tasks";
import type { PendingAction } from "./aiClient";

const AUDIT_BASE =
  (import.meta.env?.VITE_BACKEND_BASE as string | undefined) ?? "http://127.0.0.1:8000";

interface Props {
  action: PendingAction;
  project: string;
  canEdit: boolean;
  conversationId?: string;
  onDone: (msg: string, ref?: { type: "issue"; id: string }) => void;
}

async function audit(a: PendingAction, project: string, targetId: string, cid?: string) {
  try {
    await fetch(`${AUDIT_BASE}/api/audit/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action_type: a.type, target_id: targetId, origin: "ai_chat",
        conversation_id: cid ?? "", project_name: project,
      }),
    });
  } catch {
    /* 감사 실패는 액션을 막지 않음 */
  }
}

export default function ActionCard({ action, project, canEdit, conversationId, onDone }: Props) {
  const [state, setState] = useState<"pending" | "running" | "done" | "cancelled" | "error">("pending");
  const [err, setErr] = useState("");
  const p = action.params as Record<string, string | null>;

  async function run() {
    setState("running");
    try {
      if (action.type === "create_issue") {
        const iss = await createIssue({
          title: String(p.title ?? ""), type: p.type ?? undefined, category: p.category ?? undefined,
          assignee: p.assignee ?? undefined, description: p.description ?? undefined,
          status: (p.status as IssueStatus) ?? undefined, projectName: project,
          fileId: p.file_id ?? null, sheetId: p.sheet_id ?? null,
        });
        await audit(action, project, iss.issue_id, conversationId);
        setState("done");
        onDone(`✓ 이슈 생성됨: ${iss.title}`, { type: "issue", id: iss.issue_id });
      } else if (action.type === "change_issue_status") {
        const id = String(p.issue_id ?? "");
        await updateIssue(id, { status: p.to_status as IssueStatus });
        await audit(action, project, id, conversationId);
        setState("done");
        onDone(`✓ 상태변경됨: ${action.target_label} → ${p.to_status}`, { type: "issue", id });
      } else {
        const t = await createTask({
          title: String(p.title ?? ""), assignee: p.assignee ?? undefined,
          priority: (p.priority as TaskPriority) ?? undefined, due_date: p.due_date ?? undefined,
          description: p.description ?? undefined, projectName: project,
        });
        await audit(action, project, t.task_id, conversationId);
        setState("done");
        onDone(`✓ 작업 생성됨: ${t.title}`);
      }
    } catch (e) {
      setState("error");
      setErr(e instanceof Error ? e.message : String(e));
    }
  }

  if (state === "done" || state === "cancelled") return null;

  return (
    <div className="ai-action-card" role="group" aria-label="AI 제안 액션">
      <div className="ai-action-summary">{action.summary}</div>
      <ul className="ai-action-fields">
        {Object.entries(p).filter(([, v]) => v).map(([k, v]) => (
          <li key={k}><span>{k}</span>: {String(v)}</li>
        ))}
      </ul>
      {state === "error" ? <div className="ai-action-error">실패: {err}</div> : null}
      <div className="ai-action-btns">
        <button type="button" disabled={!canEdit || state === "running"} onClick={run}>
          {state === "running" ? "실행 중…" : "실행"}
        </button>
        <button type="button" onClick={() => setState("cancelled")}>취소</button>
      </div>
      {!canEdit ? <div className="ai-action-hint">뷰어 권한은 실행할 수 없습니다.</div> : null}
    </div>
  );
}
