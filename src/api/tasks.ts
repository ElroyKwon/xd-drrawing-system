// S9: 작업(Tasks) API 클라이언트. 프로젝트 전역 작업 항목(담당·상태·기한).
import { BACKEND_BASE } from "./drawings";

export type TaskStatus = "할 일" | "진행중" | "완료";
export type TaskPriority = "높음" | "보통" | "낮음";

export const TASK_STATUSES: TaskStatus[] = ["할 일", "진행중", "완료"];
export const TASK_PRIORITIES: TaskPriority[] = ["높음", "보통", "낮음"];

export type Task = {
  task_id: string;
  title: string;
  description: string;
  assignee: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string;
  project_name: string;
  created_at: string;
  updated_at: string;
};

export type TaskSummary = {
  total: number;
  open: number;
  done: number;
  by_status: Record<string, number>;
};

export async function listTasks(
  projectName = "Study_Project",
  filters: { status?: TaskStatus; assignee?: string } = {},
): Promise<Task[]> {
  const url = new URL(`${BACKEND_BASE}/api/tasks`);
  url.searchParams.set("project_name", projectName);
  if (filters.status) url.searchParams.set("status", filters.status);
  if (filters.assignee) url.searchParams.set("assignee", filters.assignee);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`작업 조회 실패 (${res.status})`);
  return res.json();
}

export async function taskSummary(projectName = "Study_Project"): Promise<TaskSummary> {
  const url = new URL(`${BACKEND_BASE}/api/tasks/summary`);
  url.searchParams.set("project_name", projectName);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`작업 집계 실패 (${res.status})`);
  return res.json();
}

export async function createTask(input: {
  title: string;
  description?: string;
  assignee?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  projectName?: string;
}): Promise<Task> {
  const res = await fetch(`${BACKEND_BASE}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: input.title,
      description: input.description ?? "",
      assignee: input.assignee ?? "",
      status: input.status ?? "할 일",
      priority: input.priority ?? "보통",
      due_date: input.due_date ?? "",
      project_name: input.projectName ?? "Study_Project",
    }),
  });
  if (!res.ok) throw new Error(`작업 생성 실패 (${res.status}): ${await res.text()}`);
  return res.json();
}

export async function updateTask(
  taskId: string,
  patch: Partial<Pick<Task, "title" | "description" | "assignee" | "status" | "priority" | "due_date">>,
): Promise<Task> {
  const res = await fetch(`${BACKEND_BASE}/api/tasks/${taskId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(`작업 수정 실패 (${res.status})`);
  return res.json();
}

export async function deleteTask(taskId: string): Promise<void> {
  const res = await fetch(`${BACKEND_BASE}/api/tasks/${taskId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`작업 삭제 실패 (${res.status})`);
}
