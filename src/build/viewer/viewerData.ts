// M4 2D 뷰어 데모 시드 — 카탈로그 §E·§F·§G·§H affordance용 정적 데이터.
// 실제 드로잉/영속/연산 없음(HUMAN_GATE). 캔버스는 "이미 그려진" 외관만 표현한다.

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

export type MarkupProperty = { label: string; value: string };

export type DemoMarkup = {
  id: string;
  kind: MarkupKind;
  label: string;
  author: string;
  date: string;
  color: string;
  // 캔버스 % 좌표(외관 배치용)
  left: number;
  top: number;
  width: number;
  height: number;
  properties: MarkupProperty[];
};

// 캡처 175535(텍스트)·175551(클라우드)·175610(폴리라인)·175630(도형)·175643(다각형) 재현
export const demoMarkups: DemoMarkup[] = [
  {
    id: "mk-text",
    kind: "텍스트",
    label: "치수 확인 요망",
    author: "김도면",
    date: "2026-06-20",
    color: "#d8232a",
    left: 12,
    top: 16,
    width: 22,
    height: 9,
    properties: [
      { label: "내용", value: "치수 확인 요망" },
      { label: "채우기 색", value: "투명" },
      { label: "글꼴", value: "맑은 고딕" },
      { label: "크기", value: "14 pt" },
      { label: "테두리", value: "1 px · 빨강" },
      { label: "불투명도", value: "100%" },
      { label: "정렬", value: "왼쪽" }
    ]
  },
  {
    id: "mk-cloud",
    kind: "클라우드",
    label: "리비전 클라우드",
    author: "이검토",
    date: "2026-06-21",
    color: "#e8590c",
    left: 40,
    top: 22,
    width: 26,
    height: 18,
    properties: [
      { label: "테두리 색", value: "주황" },
      { label: "선 두께", value: "2 px" },
      { label: "스타일", value: "점선" },
      { label: "불투명도", value: "100%" }
    ]
  },
  {
    id: "mk-polyline",
    kind: "폴리라인",
    label: "동선 화살표",
    author: "김도면",
    date: "2026-06-21",
    color: "#1971c2",
    left: 16,
    top: 52,
    width: 30,
    height: 16,
    properties: [
      { label: "선 색", value: "파랑" },
      { label: "두께", value: "3 px" },
      { label: "스타일", value: "실선" },
      { label: "화살표 머리", value: "끝점" },
      { label: "불투명도", value: "90%" }
    ]
  },
  {
    id: "mk-shape",
    kind: "도형",
    label: "주의 삼각형",
    author: "박감리",
    date: "2026-06-22",
    color: "#d8232a",
    left: 70,
    top: 50,
    width: 16,
    height: 16,
    properties: [
      { label: "테두리 색", value: "빨강" },
      { label: "채우기", value: "투명" },
      { label: "선 두께", value: "2 px" },
      { label: "불투명도", value: "100%" }
    ]
  },
  {
    id: "mk-polygon",
    kind: "다각형",
    label: "공사 영역",
    author: "이검토",
    date: "2026-06-22",
    color: "#2f9e44",
    left: 44,
    top: 60,
    width: 22,
    height: 20,
    properties: [
      { label: "채우기", value: "초록 12%" },
      { label: "테두리", value: "초록 · 점선" },
      { label: "불투명도", value: "80%" },
      { label: "면적", value: "약 42 ㎡" }
    ]
  }
];

// 캔버스 이슈 핀(175657 마크업→이슈 연계)
export type DemoIssuePin = { id: string; left: number; top: number; label: string; category: string };
export const demoIssuePins: DemoIssuePin[] = [
  { id: "pin-1", left: 33, top: 38, label: "1", category: "Coordination" },
  { id: "pin-2", left: 76, top: 64, label: "2", category: "Clash" }
];

// 좌측 이슈 탭 "검색 및 추가" 카테고리(175657)
export type IssueCategory = { id: string; name: string; description: string; count: number };
export const issueCategories: IssueCategory[] = [
  { id: "clash", name: "Clash", description: "간섭/충돌 항목", count: 3 },
  { id: "quality", name: "Quality", description: "품질 점검 항목", count: 1 },
  { id: "coordination", name: "Coordination", description: "협의/조정 항목", count: 2 }
];

// 측정 패널(175811) — 축척/단위/측정 타입 + 측정값 리스트
export type MeasureType = "선형" | "다각형 면적" | "지름" | "합산";
export const measureTypes: MeasureType[] = ["선형", "다각형 면적", "지름", "합산"];

export type MeasureRow = { id: string; type: MeasureType; value: string; marker: string };
export const measureRows: MeasureRow[] = [
  { id: "ms-1", type: "선형", value: "3.20 m", marker: "M1" },
  { id: "ms-2", type: "다각형 면적", value: "42.0 ㎡", marker: "M2" }
];

// 마크업 로그 탭 필터 드롭다운(175714)
export const markupColorFilters = ["모든 색", "빨강", "주황", "파랑", "초록"];
export const markupWeightFilters = ["모든 굵기", "1 px", "2 px", "3 px"];
export const markupKindFilters = ["모든 유형", "텍스트", "클라우드", "폴리라인", "도형", "다각형"];
