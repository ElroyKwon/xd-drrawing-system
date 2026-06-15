# Step 4 — 3D 생성 + 검수 게이트

## 목적

Step 3 의 entities 를 Three.js 씬에 **누적 추가**하고, 사람이 검수한다. 검수 통과가 다음 엔티티 타입 확장의 전제조건.

## 입력

- Step 1 산출 (view 메타)
- Step 2 산출 (grid, level)
- Step 3 산출 (entities[], 타입별)

## 산출

```
scene/
├── index.html                    ← 모든 타입 누적 로더
├── core.js                       ← Three.js 초기화 + OrbitControls + dumpBBox
├── grid.js                       ← Step 2 grid 라인·라벨 (참고용)
├── rooms.js                      ← v1 타겟
├── equipment.js                  ← v2 (검수 후 추가)
├── slabs.js                      ← v3 (검수 후 추가)
├── review-rooms.md               ← 검수 기록
├── review-equipment.md           ← v2 검수 기록
└── data/
    ├── step1_{sheet_id}.json     ← 캐시 복제 (런타임 로드)
    ├── step2_{sheet_id}_{view}.json
    └── step3_{sheet_id}_{view}_{type}.json
```

## 세부 구현

### 4.1 첫 타입 (rooms) — scene 스켈레톤 구축

- `core.js`: THREE.Scene, PerspectiveCamera, OrbitControls, CSS2DRenderer 초기화
- `grid.js`: Step 2 grid 가시화 (반투명 라인 + 라벨)
- `rooms.js`: Step 3 entity_type=room 산출을 읽어 실 polygon 을 `makeExtrudedShape` 로 매싱
- `index.html`: 위 3 파일 import

**BUG-A/B/C 방지 코드** (이전 세션 교훈, `docs/ai-3d-builder/threejs-scene/p062/decisions.md` §2 read-only 참조):
- Shape 의 y 좌표에 `-` 부호 (BUG-B 방지)
- 추가 `geometry.translate` 금지 (BUG-A 방지)
- 슬라브·바닥 패치는 `opacity: 1.0, transparent: false` (BUG-C 방지)

### 4.2 이후 타입 추가 (equipment 등)

- 기존 `index.html` 의 import 목록에 `<script type="module" src="./equipment.js"></script>` 한 줄 추가
- 기존 파일 **건드리지 않음** (core/grid/rooms.js 수정 금지)
- 새 타입이 기존 씬 파괴 시 → 해당 타입만 롤백

## 검수 게이트 ★ 본질

### 자동 사전 검증
- `render_preview` 로 스크린샷 (iso, top, southeast 3장)
- `validate_coordinate_system` 으로 scene_bbox 검사 (BUG 자동 탐지)
- console_errors 없는지 확인

### 수동 검수 (사람)

브라우저로 `scene/index.html` 열어 확인:

1. **개수 확인**: 원본 도면의 실 개수와 씬의 실 mesh 개수 일치?
2. **위치 확인**: 실 이름 라벨이 실제 실 위치에 있는가?
3. **크기 확인**: polygon 크기가 원본 도면과 비례하는가? (grid 기준)
4. **층 확인**: 지상1층·지상2층 layout 이 분리되어 보이는가?

검수 결과를 `review-{type}.md` 에 기록:

```markdown
# Review — rooms (2026-04-xx)

## 시트별 결과
- arch_p060#v1 (PIT): 6개 실 렌더, 원본 7개 → 1개 누락 (PS 실)
- arch_p060#v2 (1F): 10개 실 렌더, 원본 10개 ✓
- arch_p062#v1 (2F): 22개 실 렌더, 원본 22개 ✓

## 이슈
- [ ] p060#v1 PS 실 polygon 1점 → fallback 4m×4m. 재추출 필요
- [x] 2F 중회의실 라벨이 복도에 있음 → name 매칭 오류, Step 3 재호출

## 판정
- 조건부 통과 (이슈 2건, 후속 재추출 후 v2 진입)
```

### 검수 통과 조건

다음 모두 충족:
1. 시트별 실 개수 일치 (오차 ±2 허용)
2. 라벨 위치 명백한 오류 없음
3. 이슈 리스트가 명시적으로 문서화됨

**통과** → `review-{type}.md` 마지막 줄에 "통과: YYYY-MM-DD" 서명 → v2 진입 허용
**실패** → Step 3 재호출 (해당 type 만)

## 실패 복구

- Step 4 렌더 자체가 실패 (Three.js 에러): scene.js 코드 버그 → 수정 후 재렌더
- BUG 재현 감지: `validate_coordinate_system.issues[]` 에 error 있음 → 시스템 프롬프트 강화 또는 수동 수정
- 데이터 품질 문제: Step 3 재호출 → Step 4 재실행

## 프롬프트 계획

Step 4 는 **Vision 호출 없음** (결정론적 코드 생성). 프롬프트 불필요.
단, 검수 단계에서 "이 3D 뷰와 원본 도면의 차이점은?" 을 사람 대신 AI 에 물어보는 선택지 가능:
- `prompts/step4-self-critique.md` (선택, v3 이상에서)

## 캐시

- Step 4 산출 자체는 scene/ 에 영속
- 각 타입별 `review-{type}.md` 가 히스토리 기록
