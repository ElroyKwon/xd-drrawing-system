import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import VectorCanvas from "./VectorCanvas";

vi.mock("../../api/drawings", () => ({
  fetchVector: vi.fn(),
}));
import { fetchVector } from "../../api/drawings";

const sample = {
  strokes: [{ pts: [[0, 0], [10, 10]] as [number, number][], color: "#ffffff", layer: "A", width: 1 }],
  fills: [{ pts: [[0, 0], [10, 0], [10, 10]] as [number, number][], color: "#00ff00", layer: "B" }],
  points: [],
  layers: ["A", "B"],
  bbox: [0, 0, 10, 10] as [number, number, number, number],
  stats: {},
};

beforeEach(() => {
  // jsdom 미구현 API 목킹: ResizeObserver + canvas 2D 컨텍스트.
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
  HTMLCanvasElement.prototype.getContext = vi.fn(() => null) as never;
  vi.mocked(fetchVector).mockReset();
});

describe("VectorCanvas — S1.5 ②벡터 렌더러", () => {
  it("벡터 데이터를 받아 컨트롤과 레이어 토글을 렌더한다", async () => {
    vi.mocked(fetchVector).mockResolvedValue(sample);
    render(<VectorCanvas fileId="f1" />);

    // 로딩 상태 → 데이터 도착 후 컨트롤
    expect(screen.getByText(/벡터 로딩 중/)).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: "레이어" })).toBeInTheDocument());

    // 레이어 패널 열기 + 토글
    fireEvent.click(screen.getByRole("button", { name: "레이어" }));
    const cbA = screen.getByLabelText("A") as HTMLInputElement;
    expect(cbA.checked).toBe(true);
    fireEvent.click(cbA);
    expect(cbA.checked).toBe(false);
    expect(fetchVector).toHaveBeenCalledWith("f1");
  });

  it("벡터 조회 실패 시 에러 메시지를 보여준다", async () => {
    vi.mocked(fetchVector).mockRejectedValue(new Error("400: PDF"));
    render(<VectorCanvas fileId="f2" />);
    await waitFor(() => expect(screen.getByText(/벡터 렌더 불가/)).toBeInTheDocument());
  });

  it("이슈 핀 도구로 캔버스를 클릭하면 world 좌표로 onPlacePin을 호출한다 (S5 H4)", async () => {
    vi.mocked(fetchVector).mockResolvedValue(sample);
    const onPlacePin = vi.fn();
    const { container } = render(
      <VectorCanvas fileId="f3" activeTool="이슈 핀" onPlacePin={onPlacePin} />
    );
    await waitFor(() => expect(screen.getByRole("button", { name: "레이어" })).toBeInTheDocument());
    const canvas = container.querySelector(".vector-canvas") as HTMLCanvasElement;
    // 클릭(이동 없는 down→up) → 핀 배치
    fireEvent.pointerDown(canvas, { clientX: 40, clientY: 30, pointerId: 1 });
    fireEvent.pointerUp(canvas, { clientX: 40, clientY: 30, pointerId: 1 });
    expect(onPlacePin).toHaveBeenCalledTimes(1);
    const pt = onPlacePin.mock.calls[0][0];
    expect(pt).toHaveLength(2);
    expect(Number.isFinite(pt[0]) && Number.isFinite(pt[1])).toBe(true);
  });

  it("이슈 핀(world)을 받으면 선택 클릭 시 onSelectIssue를 호출한다 (S5 H5)", async () => {
    vi.mocked(fetchVector).mockResolvedValue(sample);
    const onSelectIssue = vi.fn();
    const issue = {
      issue_id: "i1", file_id: "f4", sheet_id: "s1", title: "패널 표기 상이",
      type: "현장 확인", status: "열림" as const, category: "clash", assignee: "",
      author: "사용자", description: "", project_name: "P",
      pin: { point: [5, 5] as [number, number], coord_space: "world" as const },
      created_at: "t", updated_at: "t",
    };
    const { container } = render(
      <VectorCanvas fileId="f4" activeTool="선택" issues={[issue]} onSelectIssue={onSelectIssue} />
    );
    await waitFor(() => expect(screen.getByRole("button", { name: "레이어" })).toBeInTheDocument());
    const canvas = container.querySelector(".vector-canvas") as HTMLCanvasElement;
    // 핀 월드(5,5) → 화면 좌표로 클릭(worldToScreen 역산). jsdom rect=0 기준.
    const scale = 0.095; // fit: min(1/10,1/10)*0.95
    const sx = 0.025 + 5 * scale;
    const sy = 0.525 - 5 * scale;
    fireEvent.pointerDown(canvas, { clientX: sx, clientY: sy, pointerId: 1 });
    fireEvent.pointerUp(canvas, { clientX: sx, clientY: sy, pointerId: 1 });
    expect(onSelectIssue).toHaveBeenCalledWith("i1");
  });
});
