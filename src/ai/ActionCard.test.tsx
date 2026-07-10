import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { test, expect, vi } from "vitest";
import ActionCard from "./ActionCard";

vi.mock("../api/drawings", () => ({
  createIssue: vi.fn().mockResolvedValue({ issue_id: "ISS-9", title: "T" }),
}));

const base = {
  action_id: "a1",
  type: "create_issue" as const,
  summary: "이슈 생성: 차단기 정격",
  params: { title: "차단기 정격", status: "열림" },
  target_label: "EE-01-001",
};

test("뷰어는 실행 버튼 비활성", () => {
  render(<ActionCard action={base} project="P" canEdit={false} onDone={() => {}} />);
  expect(screen.getByRole("button", { name: /실행/ })).toBeDisabled();
});

test("실행 시 createIssue 호출 + onDone", async () => {
  const onDone = vi.fn();
  const { createIssue } = await import("../api/drawings");
  render(<ActionCard action={base} project="P" canEdit={true} onDone={onDone} />);
  fireEvent.click(screen.getByRole("button", { name: /실행/ }));
  await waitFor(() => expect(createIssue).toHaveBeenCalled());
  await waitFor(() => expect(onDone).toHaveBeenCalled());
});
