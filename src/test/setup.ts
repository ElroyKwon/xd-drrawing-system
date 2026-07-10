import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// react-force-graph-2d 는 canvas 크기 측정에 의존해 jsdom 에서 마운트 시 크래시한다(adjustCanvasSize).
// 전역 스텁으로 대체해 메타그래프 뷰를 포함한 App 렌더 테스트가 통과하게 한다. 개별 테스트 파일이
// 자체 vi.mock("react-force-graph-2d") 를 선언하면(예: KnowledgeGraphView.test.tsx 의 props 캡처) 그쪽이 우선한다.
vi.mock("react-force-graph-2d", () => ({ default: () => null }));
