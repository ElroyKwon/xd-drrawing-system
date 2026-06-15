# arch_p062 — MVP 에이전트 결정 로그 & 문제 해결 메모

> **세션**: 2026-04-21  
> **에이전트**: Claude Code (Opus 4.7, 1M ctx) — 프로덕션 이식 대상  
> **입력 KB**: `outputs/consensus/consensus_p062.json` (Opus + Gemini consensus merge, v1 42 elements, v2 29 elements)  
> **산출물**: `knowledge-base/sheets/arch_p062.yml`, `knowledge-base/level-stack.yml`, `threejs-scene/p062/{index.html, scene.js, kb-loader.js}`, screenshots 9장.

---

## 1. Gate 판정 요약

| Gate | 판정 | 근거 |
|---|---|---|
| **Gate 1 (추출 정확도)** | ✅ | Consensus 소스 v1: rooms 18개(anchored 8=44%), walls 6/6=100%, dims 20/65=31%. v2: rooms 3개(2 anchored), walls 6/6=100%. Level stack 4개(GL/1FL/2FL/RFL)와 offset 3개 정규식 파싱 성공. |
| **Gate 4 (에이전트 계획)** | ✅ | Claude Code 세션이 KB 읽고 → Three.js 3파일 생성 → 서버 구동 → screenshot 연쇄를 자율 수행. 사용자 개입은 피드백 2회(슬래브 투명 문제, 확대 요청)에 국한. |
| **Gate 5 (에이전트 코딩)** | ✅ | OrbitControls+CSS2DRenderer+shapeExtrude 스택이 정상 렌더. 4층 스택 (GL/1FL/2FL/RFL) + 파라펫 + 그리드 라벨 가시. 5/9 screenshot 이 인식 가능한 건물 형태. |
| **Gate 6 (피드백 루프)** | ✅ | 첫 렌더(01) → 버그 3종 발견(슬래브 떠 있음, Z 뒤집힘, 바닥 투명) → 수정 → 재렌더(05,06,08,09) 에서 해소 확인. **자기 비판 → 교정 1 사이클 수렴**. |
| **Gate 7 (비용·재현성)** | ⚠️ | Gemini 재추출 2회(stage-10=26.8s, stage-00 fallback 테스트=8.3s) + Opus(Claude Code) 세션 토큰 측정 안 함. 재실행 시 temperature 0.1 이라 유사 결과 기대되나 실측 필요. |

**종합**: MVP 1 사이클로 **"Claude 에이전트 → 도면 KB → Three.js 3D" 경로의 실현 가능성 입증**. 다만 추출 정확도(Gate 1) 가 "넓고 얕음" 상태 — 3D 상세도는 데이터 품질이 상한선.

---

## 2. 🔥 해결된 버그 (반복 금지 — 다른 시트로 확장 시 주의)

### 2.1 **[BUG-A] makeExtrudedShape 에 불필요한 translate**

**증상**: 첫 렌더 iso 뷰(`01-initial-iso.png`)에서 2FL 실 박스가 보이지 않음. 상면뷰(`02-top.png`)에서 2FL 과 RFL 이 분리된 사각형으로 나타남 (서로 겹쳐 있어야 정상).

**원인**: `makeExtrudedShape` 내부에 `mesh.geometry.translate(0, heightMm, 0)` 가 있어 결과 mesh 의 **바닥이 baseY + heightMm**, **윗면이 baseY + 2·heightMm** 에 위치. 즉 한 층 위로 떠올라서 RFL 슬래브와 겹치거나 천장에 가려 안 보임. ExtrudeGeometry(+Z depth) + rotateX(-π/2) 의 결과는 이미 bottom y=0 / top y=+depth 이라 추가 translate 불필요.

**수정 (scene.js)**:
```js
// BEFORE
if (heightMm >= 0) mesh.geometry.translate(0, heightMm, 0);  // ← 삭제

// AFTER
// 별도 translate 불필요. mesh.position.y 로만 Y 위치 제어.
```

**교훈**: Three.js `ExtrudeGeometry` 는 XY 평면 shape + Z depth. `rotateX(-π/2)` 행렬 `(x,y,z)→(x,z,-y)` 을 실제로 계산해 extrude 결과의 y 범위를 확인 후 추가 변환을 결정할 것. **"회전 후에도 위로 올라가겠거니" 가정 금지**.

### 2.2 **[BUG-B] Z축 부호 불일치 — 가장 큰 착시**

**증상**: `06-top.png` 에서 2FL 건물과 RFL 옥탑이 **X-Z 상에서 완전 분리된 위치**에 있는 것처럼 보임. 두 view 의 grid 가 동일한데.

**진단 (evaluate_script dump)**:
```
v1_rooms:  {min: [0, 99700, -32000], max: [21000, 102700, -13000]}   ← 음수 Z!
v1_walls:  {min: [-250, 99700, -250], max: [21250, 102700, 30250]}   ← 양수 Z
v1_slabs:  {min: [0, 99500, -30000], max: [21000, 99700, 0]}         ← 음수 Z
grid line: 양수 Z 에 그려져 있음
```

**원인**: `makeExtrudedShape` 에서 `shape.moveTo(x, y)` 에 `(pts[i][0], pts[i][1])` 을 그대로 넣음. 이 `y` 가 scene 의 Z 좌표 입력값인데, `rotateX(-π/2)` 행렬 `(x,y,z)→(x,z,-y)` 로 shape.y → scene.-z 로 매핑되어 **Z 부호가 뒤집힘**. 반면 wall(`buildWallSegment`) 과 grid line(`buildGridLines`) 은 좌표 변환 없이 positive Z 직접 사용 → **같은 데이터가 두 좌표계(음수/양수 Z) 에 분산**.

**수정 (scene.js)**:
```js
// BEFORE
shape.moveTo(pts[0][0], pts[0][1]);
for (...) shape.lineTo(pts[i][0], pts[i][1]);

// AFTER  (shape.y 에 Z 를 negate 해서 넣어 rotate 후 scene.z 가 원래 값이 되도록)
shape.moveTo(pts[0][0], -pts[0][1]);
for (...) shape.lineTo(pts[i][0], -pts[i][1]);
```

**교훈**: 좌표계 변환이 있는 geometry 유틸(`rotateX`·`rotateY` 등)을 쓸 때는 **모든 다른 object(wall/line/grid)가 어느 부호계를 쓰는지 일치** 시킬 것. 특히 혼용 시 top 뷰 screenshot + bounding box dump 로 즉시 검출 가능.

### 2.3 **[BUG-C] 슬래브 반투명으로 "바닥" 인식 안 됨**

**증상**: 사용자 피드백 "바닥에 선들은 보이는데 투명해서 바닥으로 안 보이는 것 같다".

**원인**: 슬래브 material 에 `{opacity: 0.85, transparent: true}` 로 반투명 설정. 어두운 배경(`#1e2025`) 위에서 구분 안 됨.

**수정 (scene.js)**:
- 슬래브: `opacity: 1.0, transparent: false` (불투명)
- 추가: **각 room 마다 바닥 패치 추가** (높이 20mm, 불투명, room 색) + 기존 room 박스는 opacity 0.28 로 더 낮춤 (내부 가시성 유지)

```js
// Room 1) 바닥 패치 (불투명)
const floorPatch = makeExtrudedShape(pts, 20, COLOR.room, { transparent: false, opacity: 1.0 });
floorPatch.position.y = baseY + 1;
groups.rooms.add(floorPatch);
// Room 2) 측벽+천장 (얕은 투명으로 내부 구조 보임)
const mesh = makeExtrudedShape(pts, h, COLOR.room, { transparent: true, opacity: 0.28 });
```

**교훈**: "바닥"처럼 공간의 참조 평면이 되는 객체는 **불투명 + 명도 콘트라스트** 필수. 측벽/천장은 내부 가시성을 위해 반투명 OK.

---

## 3. 판단 조정 (MVP 진행 중 결정)

### 3.1 Stage 1 소스 — 새 Gemini 추출 대신 기존 consensus 사용
계획은 "flash-image 로 재추출 + fallback 검증" 이었으나, 실 측정에서:
- 새 Gemini flash-image: rooms 7개, annotations_ko **0줄** (level 스택 파싱 불가)
- 기존 consensus: rooms 18개, annotations_ko 에 "GL±0=EL+94.00, 1FL±0=EL+94.20, 2FL±0=1FL+5,500=EL+99.70, RFL±0=1FL+10,000=EL+104.20" 포함

**결정**: KB 입력으로 consensus 사용. 새 Gemini 결과는 재현성 증거로 보존(`outputs/2026-04-21_134506_arch_p062_gemini-3.1-flash-image/`).

**근거**: 04 문서의 관찰("Gemini 단독: 앵커율↑ 항목수↓") 과 일치. 3D 완성도에는 **항목 수·주기 텍스트**가 앵커율보다 더 중요.

### 3.2 Fallback 로직 검증 별도 실행
실 추출은 1차 gemini-3.1-flash-image-preview 에서 바로 성공(fallback 미발동). 로직 자체 검증을 위해 **잘못된 모델명(`gemini-nonexistent-test-model`) → 2차 flash-image-preview** 로 1회 시험. 404 NOT_FOUND 잡고 fallback 성공 확인. 출력 디렉토리 tag 에 `_fb` suffix 추가됨(`outputs/2026-04-21_134619_arch_p062_gemini-3.1-flash-image_fb/`).

### 3.3 1FL 외곽 = 2FL 외곽 가정
arch_p062 에는 1FL(지상1층) view 없음. 1FL 슬래브는 arch_p060 에서 가져와야 하나 MVP 범위 밖. **가정**: 2FL grid/외곽이 1FL 에도 동일 적용. 실 배치는 표시 안 함.

### 3.4 카메라 fit 기준 XZ 전용
초기 `fitCamera` 가 `maxDim = max(x, y, z)` 로 계산하여 **층 스택 Y(10m)가 footprint XZ(21×30m)보다 커서 카메라가 너무 멀어짐**. XZ 만 기준으로 변경 + topView 는 `camera.up.set(0, 0, -1)` 로 남북 방향 위쪽으로.

---

## 4. 남은 데이터 품질 이슈 (Scene 에서 해결 불가)

이들은 `scene.js` 가 고칠 수 없음 — 원본 추출(consensus_p062.json) 의 한계.

### 4.1 Grid y_spacings mismatch
```yaml
y_labels: [A, B, B1, B2, C, D]   # 6개
y_spacings_mm: [13000, 6950, 4100, null, 5950, 13000]  # 6개 (정상은 labels-1=5개)
```
4번째 null 은 "B2→C spacing 불명" 의도일 수 있으나, labels 6개/spacings 6개 라 len 불일치. 현재 `buildGridCoords` 가 `spacings.slice(0, n-1)` 로 5개만 취함. 마지막 13000 값은 무시됨. `grid_validation.y_labels_vs_spacings_ok: false` 로 KB 에 명시.

**영향**: B1 과 B2 가 Z=24050 으로 겹침 → 중회의실(r3) 박스가 두께 0 strip 으로 렌더.

### 4.2 1~2점 polygon 의 fallback 사각형
원본 데이터의 `polygon_grid` 가 1점(예: r16=PS, r17=EPS/TPS)·2점(r6 중층 조망공간, r7 남자화장실, r8 자료실 일부)인 경우 `expandToQuadIfDegenerate` 로 기본 4m×4m 또는 두 점 기준 직사각형 생성. **실제 치수와 다를 수 있음**. 도면 원본 재추출 시 Gemini 에 "실 polygon 은 최소 4개 꼭짓점" 프롬프트 강화 필요.

### 4.3 실 배치의 편향
top 뷰에서 2FL 실들이 5B~7 / A~B1 영역에 거의 없음. 이는 그 영역이 **보이드(v1=fold/void, "보이드(吹抜)" 4점 polygon)** 와 **복도**만 존재하기 때문. 3D 렌더로 이해하기엔 문제 없음 — 실제 도면이 그렇게 생겼음.

### 4.4 Caged ladder 의 점 좌표
RFL 의 `cl1=[["7","B"]]`, `cl2=[["5","B1"]]` 단일 점. 1점 polygon 은 사각형으로 확장되지만 **사다리 수직 객체**로 렌더되지 않음. 상세 프롬프트로 "CAGED LADDER → vertical_element(height, at_grid)" 구조화 필요.

---

## 5. Screenshot 인덱스

| # | 파일 | 상태 | 관찰 |
|---|---|---|---|
| 01 | `01-initial-iso.png` | 버그 상태 | 실 박스 한 층 위로 떠서 안 보임. RFL 과 겹침. |
| 02 | `02-top.png` | 버그 상태 | 2FL 과 RFL 이 서로 떨어진 위치(Z 뒤집힘) |
| 03 | `03-fixed-iso.png` | 중간 수정 | translate 버그만 수정 후. 층 스택 위치 정상화. 여전히 슬래브 투명. |
| 04 | `04-fixed-top.png` | 중간 수정 | 2FL·RFL 분리 여전 (Z 버그 미수정) |
| 05 | `05-zfix-iso.png` | ✅ 성공 | 전체 Z 버그 수정 후. 3층 스택 + 파라펫 + 실 박스 정상 |
| 06 | `06-zfix-top.png` | ✅ 성공 | Top 뷰에서 2FL·RFL 동일 footprint 위에 겹쳐짐. 실명 라벨 정확 |
| 07 | `07-2fl-focus.png` | ✅ 2FL only | 정면 측면 뷰 |
| 08 | `08-2fl-southeast-low.png` | ✅ 남동 낮은 각도 | 2FL 실 박스 측면에서 높이 확인 |
| 09 | `09-2fl-northwest.png` | ✅ 북서 높은 각도 | 실 내부 분할·화장실 천장 낮음 시각화 |

---

## 6. Claude API 이식 시 재사용할 교훈

`05-claude-api-roadmap.md` 와 연계. Agent SDK 이식 시 **이 세션의 tool-call 패턴** 을 에이전트 프롬프트에 예시로 넣을 것:

1. **KB 먼저, 재추출은 최후** — 기존 consensus JSON 을 KB 소스로 쓰면 Gemini 호출 1~3회 절감. 에이전트 시스템 프롬프트에 "consensus/ 디렉토리 존재 여부 먼저 확인" 지시.
2. **좌표계 통일 체크리스트** — extrude + rotate + direct line 이 공존하는 씬은 Top 뷰 + bbox dump 로 좌표계 분리 버그 가능. `validate_coordinate_system()` 같은 검증 tool 추가 고려.
3. **시각 디버깅 도구** — `render_preview` + dump script 가 1 사이클에 3개 버그를 잡음. 이 2-tool 조합은 이식 시 필수.
4. **피드백 루프 효율** — 사용자 피드백 2회("바닥 투명", "대각선 확대") 가 GO/NO-GO 판단 각각에 1회씩. 에이전트 자체 피드백 루프도 비슷한 frequency 로 self-critique 할 것.
5. **`expandToQuadIfDegenerate`** 같은 fallback 유틸은 MVP 필수 — 실세계 도면 추출 결과는 항상 부분적. **에이전트가 "데이터 품질 이슈는 render 에서 해결 안 됨, KB 재추출 or 사람 검수 필요" 를 구분 판단** 해야 함.
6. **투명도 정책** — "참조 평면(바닥)" 은 불투명, "공간 박스(실)" 는 반투명 + 불투명 바닥 패치. 이 시각 언어는 재사용 가능한 Three.js 스타일 가이드.

---

## 7. 다음 세션 추천

MVP 1 사이클 성공. 확장 방향:

1. **(데이터 개선)** 좁은 프롬프트(`11-grid-only.md`) 작성 → p062 재추출 → consensus 와 병합. `r6/r7/r8`처럼 2점 polygon 을 4점으로 강화.
2. **(다른 시트)** arch_p060(지상1층+PIT) 에 동일 파이프라인 적용 → 1FL 실 배치 실데이터로 대체.
3. **(Agent SDK 이식)** 05-claude-api-roadmap.md §이식 단계 착수. Tool 5개(extract_sheet, build_kb, render_preview, ask_human, log_decision) 구현.
4. **(단면도 통합)** `_png_dpi400/arch_p118~122` classifier 돌려서 단면도 확인 → 슬라브 두께·지붕 형상 보강.
