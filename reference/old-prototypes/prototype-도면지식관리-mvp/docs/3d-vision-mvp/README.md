# 3D Vision MVP — Staged Image-to-3D Modeling

> **2026-04-22 착수**. 이전 `docs/ai-3d-builder/` 트랙과 **완전 분리된 별개 MVP**. 결과·코드 모두 여기서만 누적.

---

## 목적

**3D 모델링**. PDF 도면 이미지를 AI 로 단계별 분석해서 Three.js 3D 씬에 엔티티를 **누적 추가**한다. 온톨로지·지식그래프·검색 등은 이 MVP 의 목적이 **아니다** — 순수 기하 모델링.

---

## 원칙 (왜 별개 MVP 인가)

1. **입력은 PDF 원본에서 시작**. DWG/DXF 경로 금지 (2026-04-22 feedback 확정).
2. **AI 는 한 번에 이미지 분석 못함**. 목적 단위로 큰 step 을 쪼개고, 각 step 안에서 세부 유연 조정. 한 프롬프트에 grid+rooms+walls+dims 를 다 넣는 이전 `stage-10` 방식은 앵커율 낮음이 실측으로 드러남 (`docs/ai-3d-builder/04-session-2026-04-21-ultrathink.md` §10).
3. **엔티티 타입을 누적 확장**. 1차는 **실(room) 만**, 검수 후 설비 → 층외곽 → 벽/코어/단면 순으로 추가. 각 추가는 기존 3D 씬에 얹기(누적).
4. **검수 → 추가 루프**가 본질. 자동 Agent 가 다 해버리면 오류 누적. 각 엔티티 집합 완성 후 사람이 씬을 확인하고 다음 타입 확장 결정.
5. **이전 트랙 자산은 완전 read-only 참조만**. `docs/ai-3d-builder/` 의 classifications.json·sheets/·threejs-scene/p062/ 는 건드리지 않는다. 필요 시 비교용으로만.

---

## 구조

```
docs/3d-vision-mvp/
├── README.md                  ← 이 파일 (진입점)
├── 00-approach.md             ← 4 Step 설계 + 검수 게이트 상세
├── 01-entity-roadmap.md       ← 엔티티 추가 순서 (실→설비→층외곽→...)
├── _inputs_ref.md             ← 입력 PDF/PNG 경로 (read-only 참조)
├── steps/
│   ├── step1-identify.md      ← 문서 식별
│   ├── step2-coordinates.md   ← 좌표계 수립 (grid + level)
│   ├── step3-entities.md      ← 엔티티 추출 (타입 파라미터)
│   └── step4-3d-and-review.md ← 3D 생성 + 검수 게이트
├── prompts/                   ← Step 별 Vision 프롬프트 (다음 세션)
├── scripts/                   ← Python 스크립트 (다음 세션)
└── scene/                     ← Three.js 3D 산출물 (다음 세션)
```

---

## 4 Step 요약

| Step | 목적 | 산출 | 검수 게이트 |
|---|---|---|---|
| 1. Identify | 이 시트 무엇·뷰 몇 개 | `{discipline, view_type, views[]}` | classifier confidence ≥ 0.8 |
| 2. Coordinates | 그리드·FL mm 수립 | `{grid, level}` validated | sum(spacings)=total_dim |
| 3. Entities | 타입별 객체 추출 (1차=실) | `rooms[]` grid-anchored | 앵커율 ≥ 70% |
| 4. 3D + Review | 씬 누적 + 사람 검수 | `scene/{type}.js` 추가 | 사람 OK 후 다음 타입 진입 |

**큰 step 안에 세부 유연**: 예컨대 Step 2 내부에서 "grid 라벨 먼저 → 간격 다음 → 검증 실패 시 치수선 crop 재호출" 같은 adaptive 로직. Step 3 내부에서 "이름·위치 coarse → polygon fine → 앵커 실패 시 fallback" 같은.

---

## 1차 타겟 (이번 MVP 의 완성 정의)

- **엔티티**: 실(room) 만
- **범위**: arch_p060/p061/p062#v1 (지상1~2층 확대평면도) 3 시트
- **산출**: 실 polygon 이 Three.js 씬에 매싱되고, 브라우저에서 층별 실 이름·위치 확인 가능
- **검수 통과 조건**: 각 시트별 실 개수가 육안 확인과 일치, polygon 이 grid 안에 들어가 있음

완성 후 `01-entity-roadmap.md` 의 다음 엔티티 타입으로 확장.

---

## 다음 세션 진입점

1. `README.md` (이 파일)
2. `00-approach.md` — 4 Step 상세 + 검수 게이트
3. `01-entity-roadmap.md` — 확장 순서
4. `steps/step1-identify.md` — 구현 시작
