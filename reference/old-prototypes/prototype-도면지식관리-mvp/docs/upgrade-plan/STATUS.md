# 진행 상태

> 마지막 갱신: 2026-04-20 세션 (2차)
> 현재 위치: **W4-T1 완료 + 채팅 UI·YAML 온톨로지 연동 추가 완료**
> 다음 세션 첫 행위: 이 파일 읽고 → W4-T2 통합 회귀 또는 PDF 추가 작업 확인

## 범례
- `[ ]` 대기
- `[🚧]` 진행 중
- `[✅]` 완료
- `[⏸]` 보류 (사용자 결정 대기)
- `[❌]` 차단

---

## Step 0 — 사전 인프라

- [✅] Step 0-A : `docs/` 9개 → `docs/baseline-mvp/` 이동 (2026-04-17)
- [✅] Step 0-B : `docs/upgrade-plan/` 9 .md 작성 (2026-04-17)
- [✅] Step 0-C : CLAUDE.md 참조 경로·진입 안내 갱신 (2026-04-17)

## W1 — 인프라·시드·앱 쉘 (~30h)

- [✅] **W1-T1** 의존성·환경 세팅 (2026-04-20)
- [✅] **W1-T2** 시드 변환 골격 (옵션 B/A) (2026-04-20)
- [✅] **W1-T3** 18 PDF 복사 + 수동 entity 매핑 (2026-04-20)
- [✅] **W1-T4** disciplineKo + Fuse 키 (2026-04-20)
- [✅] **W1-T5** 라우트 그룹 + AppShell 골격 (2026-04-20, 브라우저 전수 검증)
- [⏸] **W1-T6** 인터뷰 일정 4명 × 90분 확정 (~4h, 사용자 작업)

## W2 — 라우트 분해 + AnswerCard (~36h)

- [✅] **W2-T1** `/search` `/drawings/[id]` 분해 + URL 규약 (2026-04-20, 브라우저 검증)
- [✅] **W2-T2** Insight 라우트 + 알람 패널 (2026-04-20, 브라우저 검증)
- [✅] **W2-T3** AnswerCard + LLM 모킹 + SSE (2026-04-20, 브라우저 검증)
- [✅] **W2-T4** LLM 게이트 + Sonnet/Haiku 1차 (2026-04-20, live 분기 구현)

## W3 — 모바일·근본원인·보고서 (~36h)

- [✅] **W3-T1** 모바일 브레이크포인트 + 탭 뷰 (2026-04-20)
- [✅] **W3-T2** 근본원인 그래프 (Cytoscape, 1 시나리오) (2026-04-20)
- [✅] **W3-T3** 일일 보고서 좌우분할 UI (2026-04-20)
- [✅] **W3-T4** 주석 회귀 점검 — vitest 5케이스 통과 (2026-04-20)
- [✅] **W3-T5** Insight Home + Bell 카운트 (2026-04-20)

## W4 — 통합·시연·인터뷰 (~32h)

- [✅] **W4-T1** 시연 대본 3종 + 브라우저 전수 검증 (2026-04-20)
- [ ] **W4-T2** 통합 회귀 (~8h)
- [ ] **W4-T3** 인터뷰 4세션 (~12h)
- [ ] **W4-T4** 결과 종합 + 8주 백로그 (~6h)

---

## 작업 노트

### Step 0-A (2026-04-17)
- 9개 파일 무손실 이동, 본문 0 변경. baseline-mvp/는 향후 회귀 진실 출처.

### Step 0-B (2026-04-17)
- 9개 .md (README, STATUS, 00-decisions, W1~W4, verification, interview-guide) 작성 완료.
- 각 .md는 cold-start 가능 수준 — 전제·선행·완료 기준 모두 포함.

### Step 0-C (2026-04-17)
- CLAUDE.md 헤더에 4주 업그레이드 진행 상태 명시.
- §4 파일 지도에 docs/baseline-mvp + docs/upgrade-plan 추가.
- §7 참조에 plan 파일 + STATUS.md + 스펙 §14·§15 절대경로 추가.
- §8 시작 멘트 갱신 ("STATUS.md 보고 다음 작업").
- 외부 참조(`docs-시스템분석/...`)는 sibling 폴더라 영향 없음 (변경 0).

### 2026-04-20 세션 (2차) 종료 노트
- **채팅 UI 신규 구현** (`/insight/chat`): 말풍선·스트리밍·근거 카드·후속 질문 칩
- **LLM 교체**: Claude Haiku → Gemini 3.1 Flash Lite Preview (`GOOGLE_API_KEY` `.env.local`)
- **YAML 온톨로지 연동**: `dwg/온톨로지/*/entity_details/*.yaml` 전체 로드 → 질문 키워드 검색 → Gemini 컨텍스트 주입
  - 기계 분야 94개, 전기 분야 283개 엔티티 현재 인덱싱됨
  - 새 분야 추가 시 `dwg/온톨로지/` 아래 폴더 추가하면 자동 인식
- **신규 파일**:
  - `src/lib/ontology/loader.ts` — YAML → 메모리 캐시 로더
  - `src/lib/ontology/search.ts` — 키워드 기반 엔티티 검색 + 컨텍스트 빌더
  - `src/lib/insight/chat-mock.ts` — 도메인별 mock (폴백용)
  - `src/app/api/chat/stream/route.ts` — live/mock 분기 SSE 엔드포인트
  - `src/app/(s2)/insight/chat/page.tsx` — 풀 채팅 UI
- **대기 사항**: 사용자가 `dwg/` 폴더에 실 PDF 복사 → doc_id 매핑 업데이트 필요
- **W4-T2 통합 회귀** 아직 미착수

### 2026-04-17 세션 종료 노트
- Plan 파일: `C:\Users\cruel\.claude\plans\rippling-frolicking-lynx.md`
- 4가지 결정 (D-1~D-4) + 청주 yaml 부재 → 옵션 B default + 보존 6항목 정책 모두 `00-decisions.md` 기록
- 사용자 결정 대기 사항: W1-T1 착수 승인 (npm install ~수십 패키지)
- 청주 yaml 별도 도착 시 옵션 A 전환 가능 (전환 비용 2~4h, UI 코드 0 변경)
