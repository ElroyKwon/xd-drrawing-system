# Codex 작업 지침

이 파일은 Codex가 `D:\_Project\prototype-도면지식관리-mvp`를 열었을 때 먼저 참고할 프로젝트 전용 지침이다. 더 자세한 히스토리와 Claude 세션 핸드오프는 `CLAUDE.md`를 우선 읽는다.

## 응답 언어

- 기본 응답은 한국어로 한다.
- 필요한 경우 영어 용어를 그대로 쓰되, 해석과 의사결정 설명은 한국어로 한다.

## 프로젝트 요약

- 이 프로젝트는 DKS 도면지식관리 MVP 프로토타입이다.
- 비전은 단순 EDMS가 아니라 도면·문서·설비 온톨로지를 기반으로 한 의미 레이어/맥락 엔진이다.
- 현재 코드는 Next.js 14 App Router, TypeScript, Tailwind CSS 기반이다.
- 핵심 데이터는 `data/drawings.json`, `data/doc-entity-links.json`, `data/annotations.json`이다.

## 현재 트랙

- S1 Layer 0 MVP: `src/app/(s1)/**`
  - 검색, PDF/이미지 뷰어, 핀 주석, 설비 역추적의 최소 검증 트랙.
- S2 Insight Lab: `src/app/(s2)/insight/**`
  - 알람, 답변 카드, 근본원인 그래프, 보고서, LLM/RAG 시연 트랙.
- S3 Foundation: `src/app/(s3)/foundation/**`
  - 현재 핵심 시연 대상. S1을 제품형 목업으로 확장한 트랙.

## 세션 진입 순서

1. `CLAUDE.md`를 읽어 전체 상태와 핸드오프를 확인한다.
2. `docs/search-saas-study/15-next-session-handoff.md`를 읽어 최신 의제를 확인한다.
3. `docs/search-saas-study/13-presentation-by-screen.md`로 시연 동선을 확인한다.
4. `docs/search-saas-study/14-open-issues-and-roadmap.md`로 트랙 A/B/C 의사결정 맥락을 확인한다.
5. 필요 시 `docs/upgrade-plan/STATUS.md`로 S1 4주 업그레이드 상태를 확인한다.

## 작업 원칙

- 기존 sibling 프로젝트 `D:\_Project\prototype-도면지식관리\`는 비교용 원본이므로 수정하지 않는다.
- S1/S2는 보존 트랙이다. 명시 요청 없이는 수정하지 않는다.
- 특히 다음 보존 6항목은 신중히 다룬다:
  - `src/components/PdfViewer.tsx`
  - `src/components/AnnotationLayer.tsx`
  - `src/components/AnnotationPopover.tsx`
  - `src/lib/annotations-store.ts`
  - `src/lib/data-loader.ts`의 `toUpperCase()` 정규화 흐름
  - `PdfViewer`의 `TransformWrapper` doubleClick 설정
- 변경은 가능한 한 S3 Foundation 또는 명시된 대상 파일에 국소화한다.
- 사용자가 “프로젝트 파악”을 요구하면 코드 수정 전에 문서와 실제 구조를 먼저 읽고 해석한다.
- 사용자 변경 사항을 되돌리지 않는다.

## 실행과 검증

- 개발 서버: `npm run dev`
- 주요 확인 URL:
  - `/foundation`
  - `/foundation/notebook`
  - `/foundation/drawings/doc-003`
  - `/foundation/favorites`
  - `/search`
  - `/insight/lab`
- 테스트: `npm run test`
- 타입 확인: `npx tsc --noEmit`
- 린트: `npm run lint`

## 알려진 한계

- 주석은 서버가 아니라 `localStorage`의 `mvp-annotations-v1`에 저장된다.
- 일부 PDF/DWG 파일은 더미다. 시연은 문서에서 권장한 `doc-001`~`doc-008`, 특히 `doc-003` 중심으로 확인한다.
- 문서상 기존 이슈로 `src/lib/insight/llm-client.ts` 타입 문제와 일부 미사용 import lint 문제가 기록되어 있다.

## 현재 권장 다음 단계

- 현재 문서 기준 권장 의제는 트랙 A: Foundation 목업으로 페르소나 2~3인 재인터뷰를 준비하고 go/no-go를 판단하는 것이다.
- 기술 구현을 바로 늘리기 전에 `/foundation` 시연 동선과 킬러 데모 3개를 먼저 검증한다.
