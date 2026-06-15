# 세션 인계 — 2026-04-21 (ISS-3D-007 착수 세션)

> **다음 세션이 이 파일을 먼저 읽고 계속 진행한다.**
> 이번 세션 목표: ISS-3D-007 (xref 합성) 시도 + DXF→3D 렌더 가능성 판정
> 결과: **기술 성공, 실용 실패**. 공급 PDF 수준의 평면 기하는 modelspace 직접 렌더로 재현되지 않는다. 원인 규명 + 대안 경로 후보 정리.

---

## 1. 이 세션에서 한 일

| # | 스크립트 | 목적 | 결과 |
|---|---|---|---|
| 09 | `09_xref_bind.py` | xref DXF 10개를 MAIN DXF 의 동일 이름 BLOCK 에 주입 | ✅ XR-PLAN=2926, XR-SHEET=127, XR-현황측량도=1502 엔티티 주입 |
| 10 | `10_render_bound.py` | 바인딩된 MAIN msp 렌더 (A0 landscape) | ⚠ 렌더 성공, 그러나 기하가 픽셀 수준으로 축소 |
| 11 | `11_diagnose_bound.py` | msp 엔티티 분포·sheet 영역별 INSERT 분석 | ✅ msp bbox 453m×90m 확인 / A04.03 영역에 벽 기하 INSERT 없음 확증 |
| 12 | `12_render_per_sheet.py` | sheet 3개 영역별 `render_box` crop 렌더 | ⚠ A04.01 일부만 보임, A04.03 완전 비어있음 |
| 13 | `13_probe_paperspace.py` | paper space layout 확인 | ✅ `배치1`/`배치2` 모두 0 엔티티 — viewport 트릭 없음 |
| 14 | `14_render_filtered.py` | sheet 영역 교차 엔티티만 필터링 후 렌더 | ❌ `entity.bbox()` 가 대부분 None 리턴 — 필터 무의미 |

---

## 2. 확정된 사실 (재현 가능)

1. **xref 합성은 기술적으로 가능**. `ezdxf.addons.importer.Importer.import_entities(src_msp_entities, target_layout=target_block)` + `finalize()` 패턴이 작동. 중첩 BLOCK 도 자동 재귀 import.
2. **MAIN DXF 자체가 평면 기하를 sheet 좌표에 "올려놓지" 않는 구조**:
   - MAIN msp INSERT 168개 중 **XR-PLAN INSERT 5개가 모두 음의 y (-34637)** 에 배치
   - Sheet 영역 (y=0~84100) 에는 주석만 존재: `NEW_BUB`(그리드 버블), `room`(실 라벨), `LEVEL1`(레벨 표시), `SLOPE1`, 타이틀블록
   - A04.03 영역 INSERT 63개 분포: NEW_BUB 20 / room 18 / SLOPE1 8 / LEVEL1 7 / DET1 4 / 기타. **벽 기하 INSERT 0개**
3. **Paper space 비어있음**. ODA CLI 변환이 paper space 를 보존 못 했을 가능성, 또는 원 DWG 자체가 paper space 를 사용하지 않을 가능성.
4. **AutoCAD 실제 plot 은 XCLIP + model space 직접 plot** 방식으로 추정. ezdxf 는 이를 그대로 재현하지 못함 (확인 미완).

---

## 3. 이번 세션의 교훈 (재발 금지)

1. **`ezdxf.addons.importer.Importer` 는 target_layout 에 BlockLayout 전달 가능**. msp→block 주입 패턴이 공식 API 로 지원됨.
2. **`entity.bbox()` 는 DIMENSION / INSERT / TEXT 등 참조/파생 엔티티에 대해 자주 None 을 리턴**. 영역 필터링에 신뢰할 수 없음. 다음 세션에서 다른 필터 방식 필요.
3. **`Settings(fit_page=True)` 와 `render_box` 를 함께 쓰면 의도대로 동작하지 않는 듯**. ezdxf PyMuPdfBackend 의 render_box 동작을 소스 레벨에서 확인해야 함.
4. **전체 msp bbox 가 매우 크면 fit_page 로 렌더한 결과에 기하가 픽셀 단위로 축소**. 해상도를 높이거나 (DPI 500+) 영역을 줄여야 함.
5. **xref 가 BLOCK 으로 ODA 변환될 때, 사용되지 않은 xref (이 DWG 의 경우 XR-ELEV·XR-SECTION·XR-SPLAN·XR-SSECTION·XR-SITE PLAN·XR-확대배치도·xr-key) 는 MAIN 의 blocks 에 등록되지 않음**. `no_matching_block` 처리 정상.

---

## 4. 블로킹 이슈 (다음 세션 해결 대상)

### BLOCK-A: XCLIP (SPATIAL_FILTER) 해석
- 가설: AutoCAD 는 XR-PLAN INSERT 각각에 XCLIP 경계를 설정하고, 그 경계에 클립된 기하를 sheet 영역으로 옮겨 plot.
- 확인할 것:
  - XR-PLAN INSERT 5개 각각의 `e.has_spatial_filter()` 여부
  - ezdxf drawing addon 이 XCLIP 을 실제로 적용하는지 (문서상 지원이나 실제 작동 미검증)
- 실패 시: XCLIP 경계 좌표를 추출해 수동으로 INSERT 영역 crop 렌더 파이프라인 구현

### BLOCK-B: render_box 동작 방식
- 가설: `render_box` 는 paper space viewport 용이지 modelspace crop 이 아닐 수 있음.
- 확인할 것: ezdxf 소스 `ezdxf/addons/drawing/pymupdf.py` 의 `get_pixmap_bytes(render_box)` 구현
- 대안: `draw_entities()` 에 필터된 엔티티 목록 전달 + fit_page. 필터 방식은 **INSERT 위치 기반** (`e.dxf.insert` 좌표만으로 판정, bbox 계산 우회)

### BLOCK-C: A04.03 벽 기하 출처 (ISS-3D-008)
- 가설: **상위 A03 평면도 DWG** 에 벽 기하가 있고, A04 는 그걸 xref 로 참조 — 하지만 우리가 변환한 A04 DWG 에는 그 xref 가 포함되지 않았을 가능성.
- 확인할 것: `1. 도면/A03.01~04 평면도.dwg` (존재하면) 를 같은 방식으로 변환·스캔
- 파생: 만약 A03 에서 벽 기하 발견 → 건축 도면 파이프라인의 **주 소스를 A04 에서 A03 으로 이동**. 이미 ISS-3D-008 로 등록됨

### BLOCK-D: 공급 PDF 를 "정답" 으로 쓰는 역방향 비교
- 공급 PDF p62 는 이미 400dpi PNG 로 추출돼 있음 (`renders/supply_p62_400dpi.png`)
- 거기서 **그리드·벽 outline 을 OpenCV Hough transform 으로 추출** 후 DXF 에서 추출한 요소와 좌표 매칭 — 역방향 파리티 실험
- ezdxf 렌더 성공 여부와 독립적으로 진행 가능

---

## 5. 다음 세션에서 테스트할 것 (우선순위)

### T-1 (최우선): A03 평면도 DWG 변환 & 스캔 — ISS-3D-008
```bash
# 입력: D:\_Project\prototype-도면지식관리-mvp\dwg\1. 건축공사\A03.01~04 평면도.dwg (존재 여부 확인 필요)
# 작업:
# 1. 파일 존재·xref 폴더 구조 확인
# 2. 04_convert_with_xrefs.py 와 동일 패턴으로 DXF 변환
# 3. msp INSERT·XR-PLAN 기하 분포 스캔 (05b 유사)
# 4. 벽 기하가 어느 좌표계에 있는지 확인
```
성공하면 건축 파이프라인의 주 소스가 A03 으로 이동하고, A04 는 주석/상세만 담당하는 것으로 확정.

### T-2: XCLIP 해석 실험
```python
# MAIN_bound.dxf 의 XR-PLAN INSERT 5개
for insert in msp.query('INSERT[name=="XR-PLAN"]'):
    has_clip = insert.has_spatial_filter()  # ezdxf API 확인 필요
    if has_clip:
        clip = insert.get_spatial_filter()
        print(clip.boundary_vertices)  # 경계 꼭짓점 추출
```
성공 시 XCLIP 경계 좌표로 기하 수동 crop 가능.

### T-3: `draw_entities` + INSERT 위치 기반 필터로 재렌더
```python
# bbox() 우회 — INSERT 자체의 dxf.insert 좌표만 보고 sheet 교차 판정
sheet_box = (0, 0, 84100, 84100)
entities = []
for e in msp:
    if e.dxftype() == 'INSERT':
        x, y = e.dxf.insert.x, e.dxf.insert.y
        # INSERT 위치가 sheet 근방 (확장 margin 100000) 이면 포함
        if -100000 <= x <= sheet_box[2] + 100000 and -100000 <= y <= sheet_box[3] + 100000:
            entities.append(e)
    else:
        entities.append(e)  # 나머지는 모두 포함
Frontend(ctx, backend).draw_entities(entities)
```
XR-PLAN INSERT 도 포함될 것이므로 기하가 sheet 영역 위로 올라올 수 있는지 확인.

### T-4: ezdxf PyMuPdfBackend 소스 확인
- 파일: `<python_site_packages>/ezdxf/addons/drawing/pymupdf.py`
- `get_pixmap_bytes` 의 `render_box` 파라미터가 무엇을 의미하는지 (paper space viewport 인지 modelspace crop 인지)
- fit_page 와의 상호작용

### T-5: 공급 PDF OpenCV 분석 (역방향 파리티)
- `supply_p62_400dpi.png` 에서 Hough line transform 으로 직선 추출
- DXF TEXT 좌표 (예: A04.03 영역 NEW_BUB 20개) 와 공급 PDF OCR 결과 정렬
- 그리드 RMS 측정 — DXF 렌더 성공 여부와 독립

### T-6 (선택): Canvas 워크벤치 (ISS-3D-005)
- Three.js 3D 가 막혀있는 동안 **Canvas 2D 워크벤치** 가 훨씬 빠른 MVP 경로일 수 있음
- DXF 기하를 그대로 SVG 또는 Canvas 2D 로 투영 + 주석·측정 기능
- 3D 경로가 완전히 막히면 대안이 아니라 주 경로 후보

---

## 6. 파일 지도 (이 세션 산출)

```
docs/ai-3d-builder/parity-lab/p062/
├── 09_xref_bind.py                        ← xref 합성 (작동)
├── 09_xref_bind.out.json                  ← XR-PLAN=2926 주입 확인
├── 10_render_bound.py                     ← 바인딩 DXF 렌더
├── 10_render_bound.out.json
├── 11_diagnose_bound.py                   ← 영역별 엔티티 분포 분석
├── 11_diagnose_bound.out.json             ← **핵심 진단 결과**
├── 12_render_per_sheet.py                 ← sheet crop 렌더
├── 12_render_per_sheet.out.json
├── 13_probe_paperspace.py                 ← paper space 빈 것 확인
├── 13_probe_paperspace.out.json
├── 14_render_filtered.py                  ← 필터 렌더 (실패 — bbox None)
├── 14_render_filtered.out.json
├── _dxf_out/
│   ├── A04.01~03 확대평면도.dxf            ← 원본 (2.3 MB)
│   ├── A04.01~03 확대평면도_bound.dxf      ← **바인딩 후 (33.9 MB)**
│   └── xref/*.dxf (11개)
└── renders/
    ├── supply_p62_400dpi.png              ← 공급 PDF p62 (6617×4678, 1.77 MB)
    ├── xr_plan_msp.png                    ← XR-PLAN 자가 렌더 (이전 세션)
    ├── main_bound_msp.png                 ← 전체 렌더 (기하 너무 작음)
    ├── main_bound_a0403.png               ← A04.03 crop (일부만)
    ├── main_bound_sheet_A04_01~03.png     ← 시트별 crop 3장
    ├── main_bound_filtered_A04_01~03.png  ← 필터 렌더 3장 (필터 안 됨)
    └── comparison_3panel.png              ← 이전 세션 3-panel
```

---

## 7. 핵심 결정 (사용자 관점)

> 질문: "진짜 3D 결과물은 언제쯤 볼 수 있을까?"

**현재 정량적 답변**:

| 경로 | 현 상태 | 다음 마일스톤 | ETA |
|---|---|---|---|
| **Vision (Phase 0 MVP)** | ✅ 작동 — `threejs-scene/p062/` 3D HTML 렌더됨 | Phase 1 (tool 함수화) 보류 중 | 사용자 지시 시 2~3일 |
| **DXF Parity (현재 진행)** | ⚠ xref 합성 성공, 그러나 ezdxf 로 공급 PDF 수준 재현 불가 | T-1 (A03 DWG 검증) + T-2 (XCLIP) | 1~2 세션 내 판정 |
| **DXF → 3D** | ❌ 아직 착수 못 함 | DXF 기하 추출이 돼야 시작 | DXF Parity 판정 후 |

**솔직한 리스크**:
- AutoCAD plot 을 **DXF 수준에서 재현하는 건 시간이 더 드는 일**. 상용 DWG TrueView 또는 AutoCAD 로 pre-bind 하면 단일 DXF 로 합쳐져 쉽게 해결되지만 GUI 필요.
- **Canvas 워크벤치 (ISS-3D-005) 가 빠른 데모 경로로 더 현실적** 일 수 있음.

**권장 의사결정 (사용자에게)**:
1. DXF Parity 를 포기하지 않는다면: T-1 (A03 DWG) 먼저 해보고 그 결과로 판단
2. 시연 데드라인이 가까우면: Vision 경로 Phase 1 착수 + Canvas 워크벤치 병행이 안전
3. 지금 판단 대기면: 이번 세션에서 발견한 **"A04 는 주석, 벽은 A03 이 주 소스" 가 맞는지** 만 T-1 로 빠르게 확인

---

## 8. 이번 세션에 보류한 것

1. **Tool 함수화 (Phase 1)** — 사용자 지시 "별도 트랙으로 유지". 메모 `project_ai_3d_builder_track.md` 에 잠김.
2. **6-panel 비교 이미지 합성** (공급 PDF p60/61 추출) — 14 필터 실패로 무의미. 필요시 다음 세션에 `15_supply_pdf_extract.py` 로.
3. **FINDINGS.md 섹션 11 추가** — 이 인계 문서가 대체 역할 수행. 정식화는 다음 세션.
4. **ISS-3D-007 상태 업데이트** (07-open-issues.md) — "기술 성공, 실용 실패"로 변경 예정.

---

## 9. 다음 세션 첫 멘트 (사용자가 Claude 에게 줄 만한)

- "parity-lab/p062/SESSION-HANDOFF-2026-04-21.md 읽고 T-1 진행해줘"
- "A03 DWG 변환부터 해보자"
- "이거 DXF 로는 포기하자. Canvas 워크벤치 쪽으로 가보자"
- "Vision 경로 Phase 1 (tool 함수화) 먼저 들어가자"
