import { describe, expect, it } from "vitest";
import { distance, measureValue, polygonArea, type Pt } from "./geometry";

describe("S4 측정 기하", () => {
  it("두 점 거리(distance)", () => {
    expect(distance([0, 0], [3, 4])).toBe(5);
  });

  it("다각형 면적(shoelace) — 10×10 사각형 = 100", () => {
    const sq: Pt[] = [
      [0, 0],
      [10, 0],
      [10, 10],
      [0, 10]
    ];
    expect(polygonArea(sq)).toBe(100);
  });

  it("선형 측정: mm 도면(to_meter=0.001)에서 3000mm = 3.00 m", () => {
    const r = measureValue("선형", [[0, 0], [3000, 0]], 0.001, "mm");
    expect(r.value).toBeCloseTo(3.0, 6);
    expect(r.unit).toBe("m");
    expect(r.geometry).toEqual([[0, 0], [3000, 0]]);
  });

  it("지름 측정: 양 끝점 거리를 실척으로", () => {
    const r = measureValue("지름", [[0, 0], [0, 5000]], 0.001, "mm");
    expect(r.value).toBeCloseTo(5.0, 6);
    expect(r.unit).toBe("m");
  });

  it("다각형 면적: mm 도면 10000×10000mm = 100 ㎡", () => {
    const poly: Pt[] = [
      [0, 0],
      [10000, 0],
      [10000, 10000],
      [0, 10000]
    ];
    const r = measureValue("다각형 면적", poly, 0.001, "mm");
    expect(r.value).toBeCloseTo(100, 3); // (10000*0.001)^2 = 10m × 10m = 100㎡
    expect(r.unit).toBe("㎡");
  });

  it("단위 미상(to_meter=null): 도면 단위 그대로(무성 가정 금지)", () => {
    const r = measureValue("선형", [[0, 0], [100, 0]], null, "unit");
    expect(r.value).toBe(100);
    expect(r.unit).toBe("unit");
    const ra = measureValue("다각형 면적", [[0, 0], [10, 0], [10, 10], [0, 10]], null, "unit");
    expect(ra.value).toBe(100);
    expect(ra.unit).toBe("unit²");
  });
});
