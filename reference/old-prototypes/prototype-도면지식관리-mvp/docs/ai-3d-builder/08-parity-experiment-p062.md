# 08. Parity Experiment — arch_p062 페어 검증 (진행 로그)

**목적**: DWG→DXF→자가 렌더 결과와 공급 PDF 의 `arch_p062` 페이지를 비교해 "페어 하이브리드 + 파리티 체크" 아키텍처의 실효성을 실증.

**연관**: ISS-3D-004 (개념), `04-session-2026-04-21-ultrathink.md` (이전 p062 실험), `threejs-scene/p062/` (Phase 0 산출)

**원칙**: 이 문서는 **진행 로그**다. 성공만 기록하지 말고 실패·막힌 지점·선택한 우회로를 모두 기록. 다음 세션이 읽고 재개 가능해야 함.

---

## 1. 성공 기준 (Acceptance)

| 항목 | 기준 | 측정 방법 |
|---|---|---|
| 페어 발견 | `arch_p062.png` 의 도면번호 → 대응 DWG layout 1개 확정 | 타이틀블록 TEXT 자동 조인 |
| DXF 추출 | 벽·그리드·실 폴리곤 엔티티 카운트 > 0 | ezdxf 엔티티 열람 |
| 자가 렌더 | `ezdxf.addons.drawing` 으로 PNG 출력 성공 | 파일 생성 + 육안 확인 |
| Alignment | 그리드 교차점 4점 이상 매칭 | affine 변환 RMS |
| 그리드 diff | 교차점 좌표 RMS < 50mm | 계산 |
| 벽 diff | 벽 세그먼트 IoU > 0.85 | raster IoU |
| TEXT diff | 타이틀블록 도면번호 일치 | 문자열 비교 |

모두 통과 시 ISS-3D-004 → `Stage 0.5` 아키텍처 편입 확정.

---

## 2. 실험 계획 (Phase A → E)

### Phase A. 환경 준비
- [ ] 필요 도구 존재 확인: `ezdxf`, `pdfplumber`, `PyMuPDF(fitz)`, `Pillow`, `matplotlib`, `numpy`
- [ ] DWG→DXF 변환 경로 확정 (ODA File Converter CLI / LibreDWG / 기타)
- [ ] 작업 디렉토리: `docs/ai-3d-builder/parity-lab/p062/`

### Phase B. 입력 확보
- [ ] 건축 PDF 벡터 여부 확인 (pdfplumber.pages[0].chars)
- [ ] 건축 PDF 에서 `arch_p062` 에 해당하는 페이지 번호 식별
- [ ] 해당 페이지 타이틀블록 TEXT 추출 → 도면번호 확정
- [ ] 건축 DWG 55 개 순회 → 타이틀블록 TEXT 에 해당 도면번호 가진 layout 찾기

### Phase C. DXF 추출
- [ ] 매칭된 DWG → DXF 변환 (xref bind)
- [ ] ezdxf 로 해당 layout 열어 엔티티 dump
- [ ] 레이어 목록, 블록 목록, TEXT 목록 저장

### Phase D. 자가 렌더 & Alignment
- [ ] `ezdxf.addons.drawing.matplotlib` 로 layout → PNG
- [ ] 공급 PDF 페이지도 동일 해상도 PNG (PyMuPDF)
- [ ] paper space viewport 좌표로 alignment 시도
- [ ] 실패 시 그리드 교차점 4 점 수동 지정 → affine

### Phase E. Diff 3종
- [ ] 그리드: DXF 교차점 좌표 ↔ 공급 PDF 교차점 좌표 RMS
- [ ] 벽: 벽 레이어만 렌더 → 공급 PDF 영역과 IoU
- [ ] TEXT: 타이틀블록 도면번호·축척 일치 여부

### Phase F. 리포트
- [ ] parity_report.json
- [ ] 성공/실패 판정 + 다음 단계 권고
- [ ] ISS-3D-004 상태 업데이트

---

## 3. 실행 로그 (시간순)

_실행하며 append. 형식: `### [HH:MM] 단계명 / 결과 / 다음 액션`_

### [작성 시작] 2026-04-21

Phase A 환경 확인 착수 — 아래 "실행 결과" 섹션에서 이어 기록.

---

## 4. 실행 결과

### Phase A. 환경 확정 ✓
- Python 3.12, ezdxf 1.4.3, pdfplumber 0.11.9, PyMuPDF(fitz) 1.26.7, Pillow 12.1, numpy 2.4.3
- matplotlib / opencv 설치 실패 (numpy 2.x 호환 빌드 에러) — **fitz 백엔드로 우회**
- ODA File Converter 27.1.0 : `C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe`
- DWG TrueView 2025 : 설치됨 (GUI 수동 경로 대비용)
- 플롯 스타일: `토목.ctb` 만 발견 — 건축 CTB 없음. 기하 비교 전략 유지

### Phase B. p062 식별 ✓ — 자세한 내용은 `FINDINGS.md §1`

**결정적 매핑**:
- PDF **page 62** ↔ 도면번호 **A04.03** ↔ 도면명 **"확대평면도-3 (지상2층, 옥탑)"**
- 대응 DWG: `A04.01~03 확대평면도.dwg` (A04.01/02/03 세 sheet 합본)

**교훈**:
- Windows 콘솔(cp949) 의 한글 stdout 깨짐은 표시만의 문제. UTF-8 JSON 저장은 정상.
- 모든 Python 호출 앞에 `PYTHONIOENCODING=utf-8` 세팅 필수.

### Phase C. DWG → DXF + layout 조인 ✓ — 자세한 내용은 `FINDINGS.md §2-4`

**주요 장애물 3개 모두 해결**:

1. **xref 미동반 변환 실패** → xref/ 폴더 전체 복사 후 `recurse=1` 재변환 성공
2. **타이틀블록 TEXT 가 블록/ATTRIB 안에 숨음** → 블록·ATTRIB 재귀 탐색으로 발견
3. **ezdxf Vec3 slicing 미지원** → `.x, .y` 직접 접근 또는 `tuple(vec)` 로 변환

**A04.03 sheet 좌표 확정**: 메인 DXF modelspace 의 (168200, 0) 위치, **용지 간격 84100mm**.

**남은 수수께끼**: A04.03 영역에 XR-PLAN INSERT 가 없음 — ISS-3D-008 로 이슈 승격. 오늘 실험은 **축소 범위**로 진행.

### Phase D. 자가 렌더 (진행 중)

- 공급 PDF page 62 → 400dpi PNG 완료 (6617×4678, 1.77MB)
- MAIN msp / XR-PLAN msp 렌더 — ezdxf 1.4 `PyMuPdfBackend.get_pixmap_bytes(page, settings, dpi)` API 호출 형식 확정 후 백그라운드 실행 중

### Phase E. Alignment·Diff — 오늘 스코프에서 제외

당초 그리드 RMS / 벽 IoU / TEXT diff 3종을 계획했으나, xref 합성 (ISS-3D-007) 이 선행이라 **후속 세션으로 분리**. 오늘은 "렌더 산출 + 시각 확인"까지.

### Phase F. 리포트 ✓

**최종 판정**: ISS-3D-004 Phase 0 **GO** (정성적).

**산출**:
- `FINDINGS.md` 섹션 1~10 완성
- `07-open-issues.md` 에 ISS-3D-007/008/009/010 등록, ISS-3D-004 상태 갱신
- 메모리 `project_parity_experiment.md` 갱신
- `renders/` 에 3 개 이미지 (supply_p62_400dpi.png, xr_plan_msp.png, comparison_3panel.png)

## 5. 발견된 교훈 / 재발 금지

1. **xref 미동반 DWG→DXF 변환은 무의미**. `recurse=1` 로 xref 폴더 포함 재변환 필수.
2. **Windows bash stdout 한글 깨짐은 표시 문제만** — UTF-8 파일 저장은 정상. `PYTHONIOENCODING=utf-8` 세팅.
3. **ezdxf Vec3 는 slicing 불가** — `.x, .y` 직접 접근.
4. **타이틀블록 TEXT 는 INSERT 의 ATTRIB 에 숨음** — `dwgtitle`·`XR-SHEET$0$TITLE` 같은 블록 검사 시 반드시 ATTRIB 탐색.
5. **ezdxf 1.4 PyMuPdfBackend API** — `get_pixmap_bytes(page=Page(...), settings=Settings(fit_page=True), dpi=N)` 형식. `get_pdf_bytes` 도 같은 시그니처.
6. **ezdxf 는 xref DXF 를 자동 resolve 안 함** — 메인 DXF 의 INSERT 'XR-*' 은 blocks 섹션에서만 lookup. Importer 로 수동 주입 필요 (ISS-3D-007).
7. **MAIN modelspace 만 렌더하면 "empty bbox" 오류** 가능 — xref 비어있을 때 drawable 엔티티가 부족하면 ezdxf 가 bbox 실패. `render_box` 명시 또는 xref 주입 후 재시도.
8. **"확대평면도" 시트의 벽 기하는 상위 평면도(A03) 또는 다른 xref 에 있음** — "A04 에 벽이 있다"는 가정 위험 (ISS-3D-008).

## 6. 후속 이슈 (07-open-issues.md 에 등록됨)

- ISS-3D-007 xref 합성
- ISS-3D-008 확대평면도 벽 출처
- ISS-3D-009 ACAD_PROXY_OBJECT 누락
- ISS-3D-010 정밀 파리티 측정

---

## 5. 발견된 교훈 / 재발 금지 사항

_실험 종료 시 정리. 다음 실험 또는 본 구현이 반복하지 않도록._

- (pending)

---

## 6. 남은 질문·후속 이슈

_실험 도중 파생된 새 질문. 이슈로 승격할 것은 `07-open-issues.md` 로 이동._

- (pending)
