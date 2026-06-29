// S4: 뷰어 §E·§F·§G 타입/상수. 마크업·측정은 백엔드에 영속(실데이터)되며
// 정적 데모 시드(demoMarkups·measureRows·demoIssuePins)는 제거됐다.

export type MarkupKind = "텍스트" | "클라우드" | "폴리라인" | "도형" | "다각형";

export type MarkupTool =
  | "선택"
  | "텍스트"
  | "도형"
  | "클라우드"
  | "폴리라인"
  | "다각형"
  | "펜"
  | "지우개"
  | "이슈 핀"
  | "측정";

export type ViewerLeftTab = "마크업" | "마크업 로그" | "이슈";

// 좌측 이슈 탭 "검색 및 추가" 카테고리(175657)
export type IssueCategory = { id: string; name: string; description: string; count: number };
export const issueCategories: IssueCategory[] = [
  { id: "clash", name: "Clash", description: "간섭/충돌 항목", count: 3 },
  { id: "quality", name: "Quality", description: "품질 점검 항목", count: 1 },
  { id: "coordination", name: "Coordination", description: "협의/조정 항목", count: 2 }
];

// 측정 패널(175811) — 축척/단위/측정 타입 + 측정값 리스트
// S4: 측정 타입(실연산 대상). "합산"은 후속(범위 외).
export type MeasureType = "선형" | "다각형 면적" | "지름";
export const measureTypes: MeasureType[] = ["선형", "다각형 면적", "지름"];

// 마크업 로그 탭 필터 드롭다운(175714)
export const markupColorFilters = ["모든 색", "빨강", "주황", "파랑", "초록"];
export const markupWeightFilters = ["모든 굵기", "1 px", "2 px", "3 px"];
export const markupKindFilters = ["모든 유형", "텍스트", "클라우드", "폴리라인", "도형", "다각형"];
