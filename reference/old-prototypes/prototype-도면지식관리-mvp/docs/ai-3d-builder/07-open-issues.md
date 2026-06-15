# 07. Open Issues — AI 3D Builder 트랙

진행 중인 미해결 결정·리스크·향후 과제 추적 문서. 각 이슈는 **상태 / 배경 / 영향 / 다음 액션**을 명시한다. 새 이슈는 하단에 append.

---

## ISS-3D-001: Agent 자율 tool-use 구현 (Q2)

**상태**: 설계 완료, 구현 대기
**최초 등록**: 2026-04-21

**배경**: Phase 0 MVP는 Claude Code Opus가 수동으로 tool 순차 호출한 결과. Phase 1에서 Claude Agent SDK로 동일 5-tool (`extract_sheet`, `build_kb`, `render_preview`, `ask_human`, `log_decision`) 을 자율 반복하도록 이식.

**영향**: 자동화 핵심. 55개 시트를 수동 처리하면 수십 시간, 에이전트면 2~3일 내.

**제약**: 에이전트 루프에서 `render_preview` 후 스크린샷 재판독 정확도가 병목. DXF 도입(ISS-3D-004)으로 완화 기대. 완전 자율보다 `ask_human` tool 남기는 human-in-the-loop 설계가 유리.

**다음 액션**: ISS-3D-004 파리티 실험 결과 확인 후 Phase 1 착수 여부 결정.

**참조**: `06-agent-implementation-phases.md`, `05-claude-api-roadmap.md`

---

## ISS-3D-002: 뷰 간 동일 객체 매핑 (평면↔입면↔단면)

**상태**: 미해결
**최초 등록**: 2026-04-21

**배경**: "2층 평면도의 201호" ↔ "남측 입면의 해당 창" ↔ "A-A 단면의 그 벽"을 자동 연결하는 문제. 2D→3D 복원의 고전 난제이며 페어 하이브리드(DWG+PDF)로도 해결되지 않음.

**영향**: 이것 없이는 3D가 "평면 extrude + 정해진 층고"에서 멈춤. 입면 디테일·단면 보이드 반영 불가.

**후보 접근**:
- (a) 격자 고정(grid-locked) 휴리스틱 — 같은 그리드 좌표의 객체는 동일 객체로 가정
- (b) human-in-the-loop 매핑 UI (시트 간 객체 드래그 연결)
- (c) BIM 표준(IFC) 속성 재활용 — GUID 기반

**다음 액션**: 다중 뷰 시트(`A03.21~23 단면도.dwg`, `A03.11~12 입면도.dwg`)가 페어 실험에 진입한 후 재검토.

---

## ISS-3D-003: 페어 매칭 실패 (건축 N:M)

**상태**: 신규
**최초 등록**: 2026-04-21

**배경**: 건축은 1개 PDF(39MB) ↔ 55개 DWG(각 여러 layout). 타이틀블록 도면번호 자동 조인이 기본이나 실패 사례 예상 (도면번호 형식 변형, 타이틀블록 TEXT 누락 등).

**영향**: 실패 건은 수동 manifest 보완 필요. 빈도에 따라 워크플로 비용 차이 큼.

**다음 액션**: ISS-3D-004 파리티 실험에서 매칭 실패율 측정. 실패율 > 20%면 보완 전략 필요.

---

## ISS-3D-004: 자가 렌더 vs 공급 PDF 파리티 검증

**상태**: Phase 0 완료 (정성적 GO) — 2026-04-21
**최초 등록**: 2026-04-21

**배경**: 사용자 제안 — DWG→DXF→자가 렌더 PDF 와 공급 PDF 를 비교해 DXF 해석 품질을 자동 검증.

**Phase 0 실험 결과** (`parity-lab/p062/FINDINGS.md`):
- ✅ PDF ↔ DXF 페어링 가능 (타이틀블록 ATTRIB 도면번호 조인)
- ✅ DWG→DXF 변환 성공 (xref 동반 필수)
- ✅ DXF 자가 렌더 기술 작동 (ezdxf PyMuPdfBackend)
- ✅ 공급 PDF 와 시각적 일치 — 동일 건물 그리드·평면 윤곽
- ⚠ 정밀 측정 (RMS / IoU) 은 ISS-3D-007 (xref 합성) 선행 필요 → ISS-3D-010 으로 분리

**Stage 0.5 아키텍처 편입 판정**: **긍정적**. 단, 정량 검증은 ISS-3D-007·010 완료 후 재확정.

---

## ISS-3D-005: Canvas 기반 경량 엔지니어링 워크벤치

**상태**: 구상 단계
**최초 등록**: 2026-04-21

**배경**: 사용자 제안 — Three.js(WebGL) 3D 외에, Canvas 2D 또는 SVG 기반의 "대략이라도 그려주는" 엔지니어링 워크벤치가 MVP 다음 확장 기반. 정밀 편집·주석·측정 기능은 3D보다 2D 구현 비용 낮음.

**후보 라이브러리**: KonvaJS, Fabric.js, Paper.js, PDF.js 레이어링, Autodesk Forge Viewer (상용).

**영향**: Three.js 3D MVP 와는 별도 트랙. 본 MVP 가 "건축 도면 → 3D 웹페이지" 가능성 실증 후 다음 단계로 이행 가능한지 평가.

**다음 액션**: 3D MVP Phase 1 완료 후 재검토. 그 전에 파리티 실험 산출물(DXF 벡터 그래프)이 Canvas 레이어로 재활용 가능한지만 스케치.

---

## ISS-3D-006: 플롯 스타일(CTB/STB) 미적용 렌더의 비교 한계

**상태**: 파생
**최초 등록**: 2026-04-21

**배경**: 자가 렌더가 CTB/STB 플롯 스타일을 모르면 선두께·색상이 공급 PDF 와 달라 픽셀 비교 무의미. 기하 위치만 비교하는 전략으로 우회.

**영향**: 파리티 점수의 상한 고정. 정밀 시각 비교는 CTB 파일 확보 시에만 가능.

**다음 액션**: `dwg/` 폴더에 `.ctb` 검색. 있으면 ezdxf 렌더에 반영, 없으면 기하 비교만.

---

---

## ISS-3D-007: xref 합성 전략 (ezdxf 자동 resolve 불가)

**상태**: 신규
**최초 등록**: 2026-04-21 (ISS-3D-004 실험 중 파생)

**배경**: ODA File Converter CLI 에 xref bind 옵션이 없다. xref DWG 을 동반 변환하면 각각 독립 DXF 가 나오지만, 메인 DXF 의 `INSERT XR-PLAN` 은 여전히 `blocks['XR-PLAN']` 에 엔티티가 없어 ezdxf 렌더 시 비어있음.

**대안 경로**:
- (a) `ezdxf.addons.importer.Importer` 로 xref DXF 의 modelspace 를 메인의 blocks 섹션에 주입
- (b) `ezdxf.xref` 모듈 탐색 (API 안정성 미확인)
- (c) 상용: DWG TrueView 2025 / AutoCAD 의 `XREF > bind` → 단일 DWG 로 저장 후 DXF 변환 (GUI 필요)
- (d) 각 xref DXF 를 독립 렌더 후 **Python 이미지 합성** (INSERT 위치로 affine translate)

**영향**: 파리티 실험의 핵심 — 이게 안 되면 벽·그리드 자가 렌더 자체가 불가.

**다음 액션**: (a) 먼저 시도. 실패 시 (d) 이미지 합성으로 돌아갈 수 있음.

---

## ISS-3D-008: "확대평면도" 유형의 벽 기하 출처 수수께끼

**상태**: 신규
**최초 등록**: 2026-04-21 (ISS-3D-004 실험 중 파생)

**배경**: `A04.01~03 확대평면도.dwg` 의 메인 modelspace 에서, **A04.03 sheet 영역 (x≈168200~252300)** 에 XR-PLAN INSERT 가 전혀 없음. XR-PLAN INSERT 5 개 모두 A04.01/A04.02 영역에 위치. 반면 `room` / `NEW_BUB` / `SLOPE1` 등 주석 블록은 A04.03 영역에 정상 분포.

**가설**:
- (H1) A04.03 은 **다른 xref** (XR-SPLAN? XR-SSECTION?) 에서 평면을 가져옴 → 타 xref 의 INSERT 탐색 필요
- (H2) 확대평면도는 **상위 도면(A03 평면도)의 벽 기하를 참조하지 않고 독자적으로 그림** — 즉 A03·A04 도면이 서로 독립적인 기하 레이어
- (H3) DWG 가 미완성 상태로 저장됨 (가능성 낮음 — 공급 PDF 에선 평면 벽이 명확히 보임)

**영향**: "확대평면도" 카테고리 시트 일반에 해당. 건축 55 개 DWG 중 확대평면도·상세도가 상당 비중이라 큰 리스크.

**다음 액션**:
- 메인 DXF 의 모든 비-XR INSERT (특히 DET1, SEC11 등) 내부 검사
- 공급 PDF page 62 의 벽 기하 좌표와 메인 DXF 의 어떤 엔티티 좌표가 매칭되는지 역추적
- A03.01~04 평면도.dwg 를 별도 변환해 연관성 조사

---

## ISS-3D-010: 정밀 파리티 측정 (alignment + IoU)

**상태**: 신규
**최초 등록**: 2026-04-21

**배경**: ISS-3D-004 Phase 0 에서 정성적 GO 를 얻었으나 정량 측정은 스코프에서 제외. ISS-3D-007 (xref 합성) 완료 후 착수.

**필요 구성**:
- 그리드 교차점 좌표 매칭: DXF ↔ PDF → affine → RMS
- 벽 세그먼트 렌더 → IoU (A04.03 영역 crop)
- 타이틀블록 TEXT 교차검증

**성공 기준**: RMS < 50mm, IoU > 0.85, TEXT 일치.

**참조**: `parity-lab/p062/07_extract_pdf_grid.py` (PDF 그리드 라벨 좌표 사전 추출됨)

---

## ISS-3D-009: ACAD_PROXY_OBJECT 누락 경고

**상태**: 신규
**최초 등록**: 2026-04-21

**배경**: ezdxf 가 메인 DXF 를 읽을 때 `copy process ignored ACAD_PROXY_OBJECT(#...)` 경고 다수. AutoCAD 의 proprietary proxy 오브젝트 — 서드파티 ObjectARX 확장이 생성한 custom entity.

**영향**: 대부분 주석·심볼 수준이라 렌더에 치명적이지 않을 것으로 추정. 그러나 일부 프로젝트 특수 심볼이 누락되면 파리티 점수 하락.

**다음 액션**: 렌더 결과에서 공급 PDF 대비 누락 영역이 proxy 와 상관있는지 확인. 필요 시 DWG TrueView 2025 export 경로로 우회.

---

## 이슈 번호 규칙

- `ISS-3D-NNN` — 3D Builder 트랙 전용
- 기존 프로젝트의 `ISS-034`(업로드) 등과 구분
- 신규는 하단 append. 종결된 이슈는 삭제하지 않고 상태만 `[CLOSED YYYY-MM-DD]` 로 업데이트.
