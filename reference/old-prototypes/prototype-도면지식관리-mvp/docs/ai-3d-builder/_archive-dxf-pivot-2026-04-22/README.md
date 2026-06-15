# DXF 경로 아카이브 (2026-04-22)

## 왜 아카이브?

2026-04-21 세션에서 "DWG → DXF 자가 렌더" 경로가 **기술 성공 / 실용 실패** 판정을 받았다. 사용자 결정으로 해당 경로 포기, Vision-first 자동 파이프라인으로 피벗(2026-04-22).

## 핵심 교훈 (요약)

- **xref 합성**은 ezdxf API 로 가능하나, AutoCAD 의 XCLIP + modelspace 직접 plot 방식을 재현 못함 → 공급 PDF 수준 렌더 불가.
- **A04.03 DWG 는 주석 전용 시트**. 벽 기하는 상위 도면(A03) 에 있음 — 이 정보를 DXF 경로로 뚫는 비용이 Vision 경로 비용을 초과.
- **평면 기하 추출 자체**가 현재 오픈소스 스택(ezdxf + PyMuPdfBackend) 으로 안정 불가.

전체 진단은 `../parity-lab/p062/SESSION-HANDOFF-2026-04-21.md` 참조.

## 아카이브 내용

```
dxf-artifacts/                                       (137MB)
├── A04.01~03 확대평면도.dxf              ( 2.3MB, 원본 DWG→DXF 변환)
├── A04.01~03 확대평면도_bound.dxf        (34.0MB, xref 합성 산출)
└── xref/                                  (100.7MB)
    ├── XR-ELEV.dxf         (  2.0MB)
    ├── XR-PLAN.dxf         ( 38.0MB)
    ├── XR-SECTION.dxf      ( 12.0MB)
    ├── XR-SHEET.dxf        (  0.9MB)
    ├── XR-SITE PLAN.dxf    (  2.2MB)
    ├── XR-SPLAN.dxf        (  4.4MB)
    ├── XR-SSECTION.dxf     ( 41.4MB)
    ├── XR-현황측량도.dxf     (  2.0MB)
    ├── XR-확대배치도.dxf     (  1.9MB)
    └── xr-key.dxf          (  0.5MB)
```

## 재생성 가능성

- 원본 DWG(`../parity-lab/p062/_dwg_in/`)는 그대로 보존.
- `scripts/09_xref_bind.py` 로 `_bound.dxf` 재생성 가능(소요 ~3분).
- xref DXF 는 ODA File Converter 또는 AutoCAD 에서 DWG→DXF 변환으로 재생성.

## 언제 재참조할 가능성?

1. Vision 경로가 **그리드 mm 정밀도 부족**으로 막히는 경우 → DXF 의 실제 치수 데이터 참조용.
2. 특정 단면도 · 상세도에서 Vision 정확도 < 40% 로 내려가는 경우.
3. BIM 급 정확도(±50mm) 를 요구하는 서비스 요구사항 추가 시.

위 3 조건이 나오기 전까지는 이 아카이브를 건드리지 않는다.

## 관련 스크립트 (보존 — 이동 X)

다음 스크립트들은 `../parity-lab/p062/scripts/` 에 남아있으며, 위 조건이 발생 시 바로 재사용 가능:

- `09_xref_bind.py` — DXF xref 합성
- `10_render_bound.py` — 바인딩된 DXF → PNG 렌더
- `11_diagnose_bound.py` — 엔티티 분포 진단
- `12_render_per_sheet.py` — 시트 영역별 crop 렌더
- `13_probe_paperspace.py` — paperspace 검증
- `14_render_filtered.py` — 영역 필터 렌더 (실패 — 재설계 필요)

## 피벗 이후 경로

- 신규 파이프라인 계획: `C:\Users\cruel\.claude\plans\sprightly-churning-umbrella.md`
- Stage 1~5: 분류 → 공간 인덱스 → 뷰타입 인덱스 → 모델링 순서 → Agent SDK 실행
