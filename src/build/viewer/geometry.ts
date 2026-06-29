// S4 측정 기하 — 순수 함수(테스트 가능). VectorCanvas가 world 좌표 측정 연산에 쓴다.
import type { MeasureType } from "./viewerData";

export type Pt = [number, number];

export function distance(a: Pt, b: Pt): number {
  return Math.hypot(a[0] - b[0], a[1] - b[1]);
}

/** 다각형 면적(shoelace, 절대값). */
export function polygonArea(pts: Pt[]): number {
  let s = 0;
  for (let i = 0; i < pts.length; i++) {
    const [x1, y1] = pts[i];
    const [x2, y2] = pts[(i + 1) % pts.length];
    s += x1 * y2 - x2 * y1;
  }
  return Math.abs(s) / 2;
}

/**
 * 측정 타입별 실척 값 계산.
 * toMeter는 도면 model 1단위가 몇 미터인지(vector units). null이면 단위 미상 →
 * 도면 단위 그대로(무성 가정 금지). 선형/지름=양 끝 거리, 다각형 면적=shoelace.
 */
export function measureValue(
  type: MeasureType,
  pts: Pt[],
  toMeter: number | null,
  unitName = "unit"
): { geometry: Pt[]; value: number; unit: string } {
  if (type === "다각형 면적") {
    const areaModel = polygonArea(pts);
    const value = toMeter != null ? areaModel * toMeter * toMeter : areaModel;
    const unit = toMeter != null ? "㎡" : `${unitName}²`;
    return { geometry: pts, value, unit };
  }
  // 선형 / 지름: 양 끝 거리
  const a = pts[0];
  const b = pts[pts.length - 1];
  const d = distance(a, b);
  const value = toMeter != null ? d * toMeter : d;
  const unit = toMeter != null ? "m" : unitName;
  return { geometry: [a, b], value, unit };
}
