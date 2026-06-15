# 도면지식관리 시스템 (DKS) — 문서 인덱스

> Phase 0 Prototype · BESS PJT 기반 · 2026-04-16 기준

---

## 문서 목록

| 파일 | 내용 |
|------|------|
| [01-overview.md](./01-overview.md) | 프로젝트 개요, 목적, 기술 스택 |
| [02-architecture.md](./02-architecture.md) | 시스템 구조, 디렉터리 트리, 데이터 흐름 |
| [03-screens.md](./03-screens.md) | 전체 화면 목록, URL 구조, 진입 흐름 |
| [04-components.md](./04-components.md) | 컴포넌트 레퍼런스 (Props, 동작, 의존성) |
| [05-data-model.md](./05-data-model.md) | 타입 정의, JSON 스키마, 관계 구조 |
| [06-logic.md](./06-logic.md) | 핵심 로직 (검색, 영향도 엔진, mock API) |
| [07-expert-review.md](./07-expert-review.md) | 현장 전문가 6인 평가 (긍정/객관/비관/불안전성) |
| [08-issues-roadmap.md](./08-issues-roadmap.md) | 발견된 이슈 목록 및 개선 로드맵 |
| [09-user-interviews.md](./09-user-interviews.md) | 사용자 인터뷰 원문·요구사항 기록 (회차 누적) |

---

## 빠른 참조

- **로컬 실행**: `npm install` → `npm run dev` → http://localhost:3000
- **페르소나 URL**:
  - 기계: `/p1-mechanical`
  - 전기: `/p2-electrical`
  - 소방: `/p3-fire`
  - 안전: `/p4-safety`
- **데이터 위치**: `/data/*.json` (entities 125건, relations, documents, wiki, floor-plans, maintenance-logs)
- **핵심 긴급 이슈**: [08-issues-roadmap.md #P0](./08-issues-roadmap.md) — HitlFlag 로직 버그, 공문 초안 면책 경고 누락, 소방 정비이력 미표시
