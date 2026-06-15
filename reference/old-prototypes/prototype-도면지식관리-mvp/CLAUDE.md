# DKS 도면지식관리 — MVP 프로토타입

이 파일은 **세션 진입 시 가장 먼저 읽을 문서**다. 읽은 뒤 사용자 지시를 기다린다.

> **진입 시 첫 행위**:
> 1. `docs/upgrade-plan/STATUS.md` — S1 업그레이드 트랙 현황
> 2. `docs/search-saas-study/15-next-session-handoff.md` — S3 Foundation 트랙 현황 (목업 종결 시점 핸드오프)
> 3. `npm run dev` → 사용자 지시 대기

---

## 절대 제약 (위반 시 즉시 정지)

1. **`D:\_Project\prototype-도면지식관리\` 절대 수정 금지** — 비교용 sibling, 원본 보존
2. **보존 6항목 건드리지 말 것** → `docs/baseline-mvp/07-quirks-and-todo.md §4`
3. **DWG/DXF 루트 금지** — Vision(PDF→이미지) 경로만 사용
4. **3D Builder 입력은 PDF부터** — BIM 정밀도 요구 전까지 DWG 없음

---

## 프로젝트 요약

기존 sibling(`prototype-도면지식관리`)은 8인 페르소나 검증 결과 채택 2.3/10, 지불 의사 0명. 이 프로젝트는 **Layer 0 가설** 검증용 신규 빌드:

> "검색 + PDF 인라인 + 핀 주석 + 설비 역추적" 4요소만, NAS+엑셀보다 나은가?

**3개 트랙 병행 중**:
- **S1** — 4주 업그레이드 (W4-T1 완료, W4-T2 대기) → `docs/upgrade-plan/STATUS.md`
- **S2** — Insight Lab Phase 1 → `src/app/(s2)/insight/`
- **S3** — Foundation UX 14원칙 반영 완료 (목업 종결) → `docs/search-saas-study/`

`docs-시스템분석`의 페르소나 4분할·임팩트 그래프·챗 UI·AI 메타추출은 **의식적으로 배제**. Layer 0 가설과 무관.

---

## 실행

```bash
npm run dev   # http://localhost:3000
```

검증 시나리오:
- **A (검색)**: "냉동기" 검색 → doc-003/doc-004 → 클릭 → 뷰어 렌더
- **B (주석)**: 뷰어 클릭 → 메모 저장 → 새로고침 → 핀 유지
- **C (역추적)**: 우측 "설비 역추적" 탭 → `CH-001` → doc-003/doc-004 → 클릭 시 페이지 점프

---

## 핵심 quirk

| # | 항목 | 내용 |
|---|---|---|
| 1 | PdfViewer 모드 | 이미지 우선 (`pickMode`). 실 PDF 확보 시 `src/components/PdfViewer.tsx` 수정 필요 |
| 2 | react-pdf | `dynamic({ssr:false})` — 서버 렌더 시 뷰어 자리 비어 있음, 클라이언트 hydrate 후 채워짐 |
| 3 | 주석 영속 | localStorage `mvp-annotations-v1`. 시드 `data/annotations.json`은 빈 배열 |
| 4 | PDF 더미 | `public/drawings/*.pdf` 전부 16~18 bytes 더미 — 실 PDF 아님 |
| 5 | 온톨로지 | `dwg/온톨로지/` 아래 폴더 추가 시 자동 인식. 기계 94개·전기 283개 엔티티 인덱싱 중 |
| 6 | package name | `"prototype-dwgkb-mvp"` — npm ASCII 제약, 의도적 |

---

## 참조 문서

| 목적 | 경로 |
|---|---|
| **S1 작업 트래커** | `docs/upgrade-plan/STATUS.md` |
| **S3 핸드오프** | `docs/search-saas-study/15-next-session-handoff.md` |
| 의사결정 로그 | `docs/upgrade-plan/00-decisions.md` |
| 보존 6항목 | `docs/baseline-mvp/07-quirks-and-todo.md §4` |
| 서비스 1 스펙 | `docs-표준레이어/07-서비스1-도면관리-상세설계.md §14` |
| 서비스 2 스펙 | `docs-표준레이어/08-서비스2-AI인사이트-상세설계.md §15` |
| DKS 정체성 | `docs-표준레이어/05-서비스-정의.md` |
| 페르소나 | `docs-표준레이어/04-사용자-정의-페르소나.md` |
| Layer 0 아키텍처 | `docs/baseline-mvp/01-architecture.md` |
| 상위 plan | `C:\Users\cruel\.claude\plans\rippling-frolicking-lynx.md` |
