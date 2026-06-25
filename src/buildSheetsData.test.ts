import { describe, expect, it } from "vitest";
import { filterSheets, selectedBuildProject, sortSheets, type Sheet } from "./buildSheetsData";

// S2: 정적 시드 제거 후 로컬 픽스처로 helper를 검증한다(시트 목록은 실데이터로 구성).
function sheet(partial: Partial<Sheet> & Pick<Sheet, "id" | "number">): Sheet {
  return {
    projectId: selectedBuildProject.id,
    title: partial.number,
    version: "1",
    versionSet: "-",
    disciplineCode: "A",
    disciplineLabel: "A (건축)",
    tag: "architectural",
    lastUpdatedBy: "업로드",
    ...partial
  } as Sheet;
}

const fixture: Sheet[] = [
  sheet({ id: "s1", number: "A101", title: "FLOOR PLAN LEVEL1", disciplineCode: "A", disciplineLabel: "A (건축)", tag: "architectural" }),
  sheet({ id: "s2", number: "E101", title: "POWER PLAN", disciplineCode: "E", disciplineLabel: "E (전기)", tag: "electrical" }),
  sheet({ id: "s3", number: "EE-01-010", title: "단선결선도", disciplineCode: "E", disciplineLabel: "E (전기)", tag: "pdf-page" }),
  sheet({ id: "s4", number: "EE-01-002", title: "수전설비", disciplineCode: "E", disciplineLabel: "E (전기)", tag: "pdf-page" })
];

describe("build sheets data helpers", () => {
  it("filters by number, title, discipline, and tag", () => {
    expect(filterSheets(selectedBuildProject.id, fixture, "A101").map((s) => s.number)).toEqual(["A101"]);
    expect(filterSheets(selectedBuildProject.id, fixture, "전기").map((s) => s.number)).toEqual(["E101", "EE-01-010", "EE-01-002"]);
    expect(filterSheets(selectedBuildProject.id, fixture, "수전").map((s) => s.number)).toEqual(["EE-01-002"]);
  });

  it("does not return sheets from another project", () => {
    expect(filterSheets("project-seaport", fixture, "")).toHaveLength(0);
  });

  it("sorts sheet numbers naturally (EE-01-002 before EE-01-010)", () => {
    const asc = sortSheets(fixture, "number-asc").map((s) => s.number);
    expect(asc).toEqual(["A101", "E101", "EE-01-002", "EE-01-010"]);
    const desc = sortSheets(fixture, "number-desc").map((s) => s.number);
    expect(desc).toEqual(["EE-01-010", "EE-01-002", "E101", "A101"]);
  });
});
