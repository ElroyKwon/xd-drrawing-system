// S2: 실데이터 공종은 A/E/M/P 외에 S(구조)·C(토목)·G(기타) 등이 나오므로 문자열로 넓힌다.
// 색상 클래스(discipline-a/e/m/p)는 알려진 4종에만 적용, 그 외는 기본 칩 스타일.
export type SheetDisciplineCode = string;

export type BuildProject = {
  id: string;
  name: string;
};

export type Sheet = {
  id: string;
  projectId: string;
  number: string;
  title: string;
  version: string;
  versionSet: string;
  disciplineCode: SheetDisciplineCode;
  disciplineLabel: string;
  tag: string;
  lastUpdatedBy: string;
  /** S1: 업로드·변환된 실제 도면 시트의 렌더 이미지(백엔드 PNG URL). 정적 시드는 비어 있음. */
  imageUrl?: string;
  /** S1.5: ②벡터 경로용 백엔드 도면 id. DWG/DXF만 채워지며 PDF/정적 시드는 비어 있음. */
  fileId?: string;
  /** S1.5: 시트 소스("modelspace"|"paperspace"|"pdf-page"). 벡터 가용 판단에 사용. */
  source?: string;
  /** S4: 도면 내 시트 인덱스(비교 diff에서 같은 페이지 대응에 사용). */
  sheetIndex?: number;
  /** S4: 버전세트 id(비교 대상 후보 묶음). */
  versionSetId?: string;
};

export const selectedBuildProject: BuildProject = {
  id: "project-study",
  name: "Study_Project"
};

// S2: 정적 시드(initialSheets)는 실데이터 교체로 제거됨. 시트 목록은 백엔드 업로드 도면에서 구성한다.

export type SheetSortKey = "number-asc" | "number-desc";

/** 시트번호 자연정렬(EE-01-002 < EE-01-010). asc/desc 토글. */
export function sortSheets(sheets: Sheet[], key: SheetSortKey): Sheet[] {
  const sorted = [...sheets].sort((a, b) =>
    a.number.localeCompare(b.number, undefined, { numeric: true, sensitivity: "base" })
  );
  return key === "number-desc" ? sorted.reverse() : sorted;
}

export function filterSheets(projectId: string, sheets: Sheet[], query: string): Sheet[] {
  const projectSheets = sheets.filter((sheet) => sheet.projectId === projectId);
  const normalized = query.trim().toLowerCase();

  if (!normalized) {
    return projectSheets;
  }

  return projectSheets.filter((sheet) => {
    return [sheet.number, sheet.title, sheet.disciplineLabel, sheet.tag].some((value) =>
      value.toLowerCase().includes(normalized)
    );
  });
}
