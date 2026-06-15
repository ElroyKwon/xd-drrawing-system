# Findings — Parity Experiment arch_p062 (진행 중)

작성: 2026-04-21 (세션 중). 실험 진행에 따라 추가.

## 1. Phase B 성공 — PDF 인덱싱

- 건축 통합 PDF: 122 페이지, 38.85MB, **벡터 + 텍스트 레이어 OK** (pdfplumber 추출 성공)
- **교훈**: Windows 콘솔의 한글은 cp949 로 표시 시도하여 깨지지만, **UTF-8 로 저장한 JSON 파일은 정상**. 스크립트는 항상 JSON 파일 출력 + `PYTHONIOENCODING=utf-8` 환경변수 필수.
- **p062 = 페이지 62 = 도면번호 A04.03 = "확대평면도-3 (지상2층, 옥탑)"** 확정. 이전 세션 `arch_p062` 명명 규칙 (PDF 페이지 번호 = 파일명 NNN) 검증됨.
- 인접: page 60=A04.01(PIT+지상1층), page 61=A04.02(지상1층), page 63=A05.01(계단실).

## 2. Phase C 경로 — xref bind 필수

### 1차 시도: 메인 DWG 단독 변환 → 실패
- ODA File Converter 27.1 로 `A04.01~03 확대평면도.dwg` 단독 변환: 1.3초, 2.3MB DXF 생성
- 하지만 MAIN DXF 의 `XR-PLAN`·`XR-SHEET` 블록이 **entities=0** (빈 참조)
- 결과: LINE 10 개, LWPOLYLINE 43 개만 — 벽·그리드·타이틀블록 **전부 누락**
- TEXT 검색 "A04.03" 0 hits — 타이틀블록이 xref 에 있어서
- Paper space (`배치1`, `배치2`) 도 빈 상태

### 2차 시도: xref 폴더 포함 변환 → 성공
- 원본 `xref/` 의 10 개 DWG 을 `_dwg_in/xref/` 에 복사
- ODA 를 `recurse=1` 로 재실행 → `_dxf_out/xref/*.dxf` 10 개 생성
- 주목 크기: **XR-PLAN.dxf 37.2MB**, XR-SSECTION 40.4MB, XR-SHEET 0.8MB

### 교훈 (재발 금지)
- **xref DWG 가 동반되지 않은 DXF 변환은 무의미**. ODA CLI 에 bind 옵션 없음 — 해결은 항상 "원본 폴더 구조 유지 + recurse=1".
- 상용 DWG TrueView 2025 나 AutoCAD 로 사전 bind 하면 단일 DXF 로 합쳐짐 — 하지만 GUI 필요.
- ezdxf 는 INSERT 해석 시 **메인 DXF 의 blocks 섹션**만 봄. xref DXF 파일의 modelspace 를 따로 가져오지 않으므로, 수동 합성 필요 (후속 이슈).

## 3. 핵심 발견 — A04.03 영역 좌표계

메인 DXF 의 타이틀블록 오버레이 구조:

```
XR-SHEET$0$TITLE INSERT @ (0.0, 0.0)        ATTRIB A0.00="A04.01" TITLE2="확대평면도-1"
XR-SHEET$0$TITLE INSERT @ (84100, 0.0)       ATTRIB A0.00="A04.02" TITLE2="확대평면도-2"
XR-SHEET$0$TITLE INSERT @ (168200, 0.0)      ATTRIB A0.00="A04.03" TITLE2="확대평면도-3"
```

- 3 개 시트가 **x 축 간격 84100mm** (A1 용지 폭) 로 나란히 배치
- **A04.03 sheet 영역 = 메인 (168200, 0) ~ (252300, 84100) 근사**
- dwgtitle 블록 (로컬) 도 비슷한 위치에 3개 — 개별 "지상1층 확대평면도-1" 식 소제목

## 4. 풀지 못한 수수께끼 — A04.03 의 벽 기하 위치

메인 DXF 의 **XR-PLAN INSERT 5 개가 모두 A04.03 영역 밖**:

```
XR-PLAN @ (-214810, -34637)   ← 가장 왼쪽 (A04.01 왼쪽 밖)
XR-PLAN @ ( -80886, -34637)   ← A04.01 왼쪽 밖
XR-PLAN @ (  -8829, -34637)   ← A04.01 영역
XR-PLAN @ (  33109, -34637)   ← A04.01 영역
XR-PLAN @ (  87249, -21361)   ← A04.02 영역 (y 만 다름)
```

가능 가설:
- (a) A04.03 의 평면 기하는 **XR-PLAN 이 아닌 다른 xref** (XR-SPLAN, XR-SSECTION 등) 에서 옴 → 확인 필요
- (b) XR-PLAN INSERT 의 **XCLIP (SPATIAL_FILTER)** 이 각 INSERT 별 다른 영역을 표시 — 하지만 INSERT 위치가 sheet 영역 밖이므로 불일치
- (c) XR-PLAN 내부의 큰 좌표 (옥탑 @ x=619707) 를 sheet 위치로 끌어오는 INSERT 가 **누락** — DWG 이 미완성 or 저장 상태

**실용 결론**: 이 퍼즐을 오늘 풀지 말고 **축소된 최소 실험** (DXF 자가 렌더의 기술적 가능성 증명) 으로 전환.

메인 modelspace 의 **room INSERT 는 A04.03 영역 안에 다수 존재** (예: (181780, 33767), (190694, 11911) 등) — 즉 **실 배치·장비·가구 등 주석은 메인에 있으나 벽/그리드는 누락**. 이는 **"확대평면도"의 일반적 패턴** (벽은 A03 상위 도면에서, 확대도는 디테일만) 일 수 있음.

## 5. Phase D — 자가 렌더 (진행 중)

### API 발견
- `ezdxf.addons.drawing.pymupdf.PyMuPdfBackend` 의 1.4.3 시그니처:
  - `get_pixmap_bytes(page, fmt='png', settings, dpi, alpha, render_box)` — 바로 PNG bytes
  - `get_pdf_bytes(page, settings, render_box)` — PDF bytes
  - `layout.Page(width, height, margins=Margins.all(5))` — mm 단위
  - `layout.Settings(fit_page=True, ...)` — fit 옵션
- 1차 코드에 `page` 인자 없이 호출 → TypeError. 2차 코드에서 수정.

### 공급 PDF 페이지 62 추출 성공
- fitz 400dpi → 6617×4678px PNG, 1.77MB (`renders/supply_p62_400dpi.png`)

### DXF 렌더 결과
- **MAIN msp**: `ValueError: empty bounding box` — 실패. 예상대로 MAIN 의 msp 엔티티(LINE 10, LWPOLYLINE 43, INSERT 168 중 XR-* 는 빈 블록)만으로는 ezdxf 가 유효 bbox 산출 불가.
- **XR-PLAN msp**: 성공. 3310×2338 PNG, 234KB. A1 landscape 100dpi.
- **공급 PDF p62**: 6617×4678 PNG, 1.77MB, 400dpi.

### 렌더 시각 분석 (`renders/comparison_3panel.png`)

**XR-PLAN 렌더의 구조**:
- **5 개의 작은 평면 프레임이 수평 배치** — 왼쪽부터 오른쪽으로 대략 PIT/지상1층(여러 버전)/지상2층/옥탑
- 각 프레임에 그리드(빨강)·벽(흰)·일부 실 라벨 보임
- **4 번째 프레임은 거의 비어있음** — 그리드만 있고 기하 없음 (가능한 해석: DWG 저장 당시 작업 중)
- **5 번째 프레임은 작은 옥탑 평면** — 장비·선홈통 등 보임

**공급 PDF page 62 (A04.03) 구조**:
- 좌측: "1 지상2층 확대평면도", 우측: "2 옥탑 확대평면도"
- 그리드 라벨 5/6/7 (상단), A/B1/B2/C (좌측) 명확
- 실 이름·치수·설비 다수
- 타이틀블록: R-Center / 가운건축 / A04.03 / 확대평면도-3 / 2024.05

**비교 결론 (시각 판정)**:
- ✅ **자가 렌더 기술 작동 확인** — DXF → PNG 파이프라인 성립
- ✅ **공급 PDF 와 같은 건물 구조물을 보고 있음** — 그리드·평면 윤곽 일치
- ⚠ **"확대평면도" 수준의 디테일은 XR-PLAN 에 없음** — 공급 PDF 쪽이 훨씬 더 풍부 (실 이름·장비·치수) → ISS-3D-008 의 강한 증거. "확대평면도 A04.03 의 디테일은 XR-PLAN 외의 소스에서 옴".

## 6. Phase E — Alignment·Diff (후속 세션으로 분리)

당초 계획 (그리드 RMS, 벽 IoU, TEXT diff) 은 xref 합성 선행 필요 — **후속 세션으로 분리**.

오늘은 **시각 확인만**: 자가 렌더 3장 (main_msp, xr_plan_msp) 과 공급 PDF (supply_p62) 를 나란히 놓고 "기하가 존재하는가" 확인.

## 7. 최종 판정 (Phase 0 파리티 실험)

**ISS-3D-004 GO/NO-GO: GO**

근거:
1. PDF ↔ DXF 페어링 가능 (타이틀블록 ATTRIB 의 도면번호 조인)
2. DWG → DXF 변환 성공 (xref 동반 필수)
3. DXF → PNG 자가 렌더 성공 (ezdxf PyMuPdfBackend)
4. 공급 PDF 와 동일 건물 기하를 시각적으로 대응 확인

**하지만 정밀 파리티 (alignment RMS, 벽 IoU) 는 이번에 측정하지 못함** — xref 합성 (ISS-3D-007) 이 선행 요구이기 때문. 축소 범위에서 "정성적 GO" 를 얻음.

## 8. 후속 이슈 (07-open-issues.md 에 등록됨)

- **ISS-3D-007**: xref 합성 전략 — `ezdxf.addons.importer.Importer` 경로 권장
- **ISS-3D-008**: "확대평면도" 유형의 벽 기하 출처 — XR-PLAN 외 소스 추적
- **ISS-3D-009**: ACAD_PROXY_OBJECT 누락 경고 영향도
- **ISS-3D-010** (신규): 정밀 파리티 측정 — xref 합성 완료 후 grid RMS/wall IoU/TEXT diff 실측

## 9. 다음 세션 재개 방법

1. `08-parity-experiment-p062.md` 섹션 5 까지가 이번 실험. 섹션 6 (후속) 부터 재개
2. 먼저 `ISS-3D-007` 해결 시도 — `ezdxf.addons.importer.Importer` 로 XR-PLAN.dxf modelspace 를 MAIN.dxf 의 `blocks['XR-PLAN']` 에 주입하는 스크립트 작성
3. 성공 시 MAIN 을 다시 렌더 → 공급 PDF 와 **A04.03 영역 crop 후 overlay** → 정량 측정
4. 병행으로 ISS-3D-008 — 메인 DXF 의 비-XR INSERT (DET1, SEC11 등) 내부 기하 조사

## 10. 세션 자산

```
docs/ai-3d-builder/parity-lab/p062/
├── 01_probe_pdf.py                 PDF 인덱싱
├── 01_probe_pdf.out.json
├── 02_convert_dwg.py               1차 DWG → DXF (xref 미동반 — 실패 케이스 기록용)
├── 02_convert_dwg.out.json
├── 03_scan_dxf.py                  1차 스캔 (Vec3 slicing 버그 남음 — 기록용)
├── 03_scan_dxf.out.json
├── 04_convert_with_xrefs.py        2차 변환 (xref 동반) — 성공
├── 04_convert_with_xrefs.out.json
├── 05_scan_xrefs.py                2차 스캔 (Vec3 버그)
├── 05b_scan_xrefs.py               3차 스캔 (ATTRIB 재귀) — 성공
├── 05b_scan_xrefs.out.json         A04.03 좌표 (168200, 0) 확정
├── 06_render_and_pdf.py            PyMuPdfBackend get_pdf_bytes() 1차 — API 오류
├── 06b_render_and_pdf.py           get_pixmap_bytes(page,...) 2차 — XR-PLAN 성공 / MAIN 실패
├── 06b_render_and_pdf.out.json
├── 07_extract_pdf_grid.py          공급 PDF 그리드 라벨 좌표
├── 07_extract_pdf_grid.out.json    A/B/D (y=111.8/394.7/721.2), 5/6/7 (y=36.8)
├── 08_compare_visual.py            3-panel 합성
├── 08_compare.out.json
├── FINDINGS.md                     요약 (이 파일)
├── _dwg_in/                        원본 DWG + xref/ 복사본
├── _dxf_out/                       변환된 DXF (main + xref 11 개)
└── renders/
    ├── supply_p62_400dpi.png       공급 PDF p62 (1.77 MB)
    ├── xr_plan_msp.png             자가 렌더 XR-PLAN 전체 (234 KB)
    └── comparison_3panel.png       합성 (395 KB)
```
