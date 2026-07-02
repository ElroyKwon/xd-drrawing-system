import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import BuildTasksView from "./BuildTasksView";

// S9: 작업은 백엔드 실데이터. listTasks/createTask/updateTask/deleteTask를 목킹한다.
const openTask = {
  task_id: "t1", title: "수전실 접지저항 측정 결과 제출", description: "",
  assignee: "시공 전기팀", status: "진행중", priority: "높음", due_date: "2026-07-10",
  project_name: "Study_Project", created_at: "2026-06-29T02:00:00", updated_at: "2026-06-29T02:00:00",
};
const doneTask = {
  ...openTask, task_id: "t2", title: "접지 시스템 준공 검사 신청", status: "완료",
  priority: "보통", created_at: "2026-06-29T01:00:00",
};

vi.mock("../api/tasks", async (importActual) => {
  const actual = await importActual<typeof import("../api/tasks")>();
  return {
    ...actual,
    listTasks: vi.fn(() => Promise.resolve([openTask, doneTask])),
    createTask: vi.fn((input: { title: string }) =>
      Promise.resolve({ ...openTask, task_id: "new", title: input.title, status: "할 일" })),
    updateTask: vi.fn((id: string, patch: { status?: string }) =>
      Promise.resolve({ ...openTask, task_id: id, status: patch.status ?? "진행중" })),
    deleteTask: vi.fn(() => Promise.resolve()),
  };
});

import * as api from "../api/tasks";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("BuildTasksView (S9 작업)", () => {
  it("renders real tasks from the backend", async () => {
    render(<BuildTasksView projectName="Study_Project" />);
    expect(await screen.findByText("수전실 접지저항 측정 결과 제출")).toBeInTheDocument();
    expect(screen.getByText("접지 시스템 준공 검사 신청")).toBeInTheDocument();
    expect(api.listTasks).toHaveBeenCalledWith("Study_Project");
  });

  it("creates a task through the modal (real POST)", async () => {
    const user = userEvent.setup();
    render(<BuildTasksView projectName="Study_Project" />);
    await screen.findByText("수전실 접지저항 측정 결과 제출");
    await user.click(screen.getByRole("button", { name: "작업 작성" }));
    await user.type(screen.getByLabelText("제목"), "22.9kV 인입 케이블 발주");
    await user.click(screen.getByRole("button", { name: "작성" }));
    expect(api.createTask).toHaveBeenCalledWith(
      expect.objectContaining({ title: "22.9kV 인입 케이블 발주", projectName: "Study_Project" }),
    );
    expect((await screen.findAllByText("22.9kV 인입 케이블 발주")).length).toBeGreaterThan(0);
  });

  it("changes task status (persisted via updateTask)", async () => {
    const user = userEvent.setup();
    render(<BuildTasksView projectName="Study_Project" />);
    await user.click(await screen.findByText("수전실 접지저항 측정 결과 제출"));
    const statusSelect = await screen.findByLabelText("작업 상태");
    await user.selectOptions(statusSelect, "완료");
    expect(api.updateTask).toHaveBeenCalledWith("t1", { status: "완료" });
  });

  it("filters by status", async () => {
    const user = userEvent.setup();
    render(<BuildTasksView projectName="Study_Project" />);
    await screen.findByText("수전실 접지저항 측정 결과 제출");
    await user.click(screen.getByRole("button", { name: "완료" }));
    // 완료 필터: 완료 작업만 남고 진행중 작업은 사라짐.
    expect(screen.getByText("접지 시스템 준공 검사 신청")).toBeInTheDocument();
    expect(screen.queryByText("수전실 접지저항 측정 결과 제출")).not.toBeInTheDocument();
  });

  it("gates create/status/delete for viewers (canEdit=false)", async () => {
    const user = userEvent.setup();
    render(<BuildTasksView projectName="Study_Project" canEdit={false} />);
    await screen.findByText("수전실 접지저항 측정 결과 제출");
    expect(screen.getByRole("button", { name: "작업 작성" })).toBeDisabled();
    await user.click(screen.getByText("수전실 접지저항 측정 결과 제출"));
    expect(await screen.findByLabelText("작업 상태")).toBeDisabled();
    expect(screen.queryByRole("button", { name: /작업 삭제/ })).not.toBeInTheDocument();
  });
});
