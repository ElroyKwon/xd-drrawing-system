// S9.3: 프로젝트 템플릿(허브 레벨) API 클라이언트.
import { BACKEND_BASE } from "./drawings";
import type { MemberRole } from "./admin";

export type TemplateMember = { member_id: string; role: MemberRole };

export type ProjectTemplate = {
  template_id: string;
  name: string;
  access: string;
  source: "blank" | "existing";
  source_project: string | null;
  folders: string[];
  default_members: TemplateMember[];
  created_by: string;
  created_at: string;
};

export async function listTemplates(): Promise<ProjectTemplate[]> {
  const res = await fetch(`${BACKEND_BASE}/api/templates`);
  if (!res.ok) throw new Error(`템플릿 목록 실패 (${res.status})`);
  return res.json();
}

export async function createTemplate(input: {
  name: string;
  access?: string;
  source?: "blank" | "existing";
  source_project?: string | null;
}): Promise<ProjectTemplate> {
  const res = await fetch(`${BACKEND_BASE}/api/templates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: input.name,
      access: input.access ?? "일반 액세스",
      source: input.source ?? "blank",
      source_project: input.source_project ?? null,
    }),
  });
  if (!res.ok) throw new Error(`템플릿 작성 실패 (${res.status}): ${await res.text()}`);
  return res.json();
}

export async function deleteTemplate(templateId: string): Promise<void> {
  const res = await fetch(`${BACKEND_BASE}/api/templates/${templateId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`템플릿 삭제 실패 (${res.status})`);
}
