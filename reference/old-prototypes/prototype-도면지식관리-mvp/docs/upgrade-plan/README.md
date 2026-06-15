# DKS 4주 목업 업그레이드 — 실행 인덱스

> **상위 플랜**: `C:\Users\cruel\.claude\plans\rippling-frolicking-lynx.md`
> **스펙 원본**: `docs-표준레이어/07-서비스1-도면관리-상세설계.md` §14, `docs-표준레이어/08-서비스2-AI인사이트-상세설계.md` §15
> **Baseline 분석**: `docs/baseline-mvp/` (이전 Layer 0 MVP의 현재 코드 분석 9건)

## 목표

기존 Layer 0 MVP(`src/app/page.tsx` 213줄 단일 페이지)를 두 서비스(도면 관리·AI 인사이트) 통합 앱으로 4주 안에 확장. 인터뷰·상부 보고용 시연 가능 완성도.

## 문서 구성

| 파일 | 용도 | 사용 시점 |
|------|------|----------|
| [README.md](README.md) | 이 인덱스 | 매 세션 진입 |
| [STATUS.md](STATUS.md) | 19개 작업 체크리스트 트래커 | 매 세션 진입 (어디까지 됐는지) |
| [00-decisions.md](00-decisions.md) | 4개 결정사항 + 옵션 A/B 분기 + 보존 6항목 | 새 작업 시작 시 |
| [W1-foundation.md](W1-foundation.md) | W1-T1~T6 상세 | 1주차 |
| [W2-routes-answer.md](W2-routes-answer.md) | W2-T1~T4 상세 | 2주차 |
| [W3-mobile-graph-report.md](W3-mobile-graph-report.md) | W3-T1~T5 상세 | 3주차 |
| [W4-demo-interview.md](W4-demo-interview.md) | W4-T1~T4 상세 | 4주차 |
| [verification.md](verification.md) | 시연 5/10/20분 + 회귀 체크리스트 | 매 작업 완료 후 |
| [interview-guide.md](interview-guide.md) | 인터뷰 가이드 (W1-T6 결과물) | 1주차 작성 → 4주차 사용 |

## 4주 작업 분해 (요약)

| 주 | 핵심 산출 | 작업 수 | 추정 시간 |
|:-:|----------|:------:|:--------:|
| W1 | 인프라·시드·앱 쉘 | 6 | ~30h |
| W2 | 라우트 분해·URL 규약·AnswerCard | 4 | ~36h |
| W3 | 모바일·근본원인·보고서 | 5 | ~36h |
| W4 | 시연·인터뷰·종합 | 4 | ~32h |
| **합계** | — | **19** | **~134h** |

## 의존성 그래프

```
W1-T1 ──┬─► W1-T2 ──► W1-T3 ──► W1-T4 ──┐
        │                                ├─► W2-T1 ──┬─► W3-T1 ──► W3-T4
        └─► W1-T5 ───────────────────────┘            │
                                                       ├─► W2-T2 ──► W2-T3 ──┬─► W2-T4 ──► W3-T3 ──┐
                                                       │                      │                      ├─► W3-T5
                                                       │                      └─► W3-T2              │
W1-T6 (병렬, 사용자 작업) ─────────────────────────────────────────────────────────────────────────┘
                                                                                                    │
                                                                                                    ▼
                                                                                          W4-T1, W4-T2 ──► W4-T3 ──► W4-T4
```

**크리티컬 패스**: W1-T1 → T2 → T3 → T4 → W2-T1 → T2 → T3 → T4 → W3-T3 → W4-T2 → T3 → T4

## 위험 매트릭스 (보존 6항목)

`docs/baseline-mvp/07-quirks-and-todo.md §4` 명시. 신규 작업이 충돌하면 즉시 정지하고 사용자 협의.

| # | 보존 항목 | 위험 작업 | 방어 |
|:-:|----------|----------|------|
| 1 | PdfViewer pickMode + key 패턴 | W2-T1 URL highlight | HighlightOverlay를 renderOverlay slot 합성 |
| 2 | AnnotationLayer pointer-events 분리 | W2-T1 HighlightOverlay | 동일 패턴 복사 |
| 3 | AnnotationPopover Escape | — | 신규 modal 없음 |
| 4 | annotations-store hydrated 플래그 | W3-T3 useReportsStore | 동일 패턴 강제 복사 |
| 5 | data-loader toUpperCase 정규화 | W1-T2 시드 변환 | 변환 출력 단계에서 toUpperCase 강제 |
| 6 | TransformWrapper doubleClick:disabled | W3-T1 모바일 | PdfViewer 0 변경 |

## 매 세션 진입 절차

1. `cat docs/upgrade-plan/STATUS.md` → 어디까지 됐는지 확인
2. 다음 작업 ID(예 W1-T2) → 해당 주차 .md 파일 열기
3. STATUS.md에서 `[ ]` → `[🚧]` 변경
4. 작업 + 완료 기준 통과 확인
5. STATUS.md에서 `[🚧]` → `[✅]` 변경 + 노트 추가
6. 보존 6항목 충돌 발견 시 즉시 정지
