# AI 3D Builder — 타당성 리서치 (Evidence-Based)

> **상태**: 2026-04-21 실측 실험(B/C/D/A 4 treatment × 2시트) 완료. **Agentic 재설계 관점 확립 — 04 문서부터 읽을 것**.
> **이전 버전 폐기**: 2026-04-21 오전에 작성했던 7개 문서는 Gemini 대화 받아쓰기 + 임의 스키마에 의존한 추측이었음. 전량 삭제 후 실증 기반으로 재작성.

---

## 1분 요약 (결론부터)

**사용자의 질문**: "건물 도면 15~20장(정면·측면·평면·단면 등 다중 뷰)을 Claude API에 순차로 주면 3D HTML을 누적 생성할 수 있는가?"

**근거 기반 답**: **가능은 하지만, 지금 그대로 실행하면 실패 확률이 높다.**

리서치로 확인된 3가지 핵심 제약:

1. **Claude Vision의 도면 치수 추출 정확도 약 40%** (엔지니어링 도면 벤치마크, 10장/17~58 dim 조건). Gemini Pro는 같은 조건에서 약 80%. Claude는 "뷰 간 치수 오배정"이 주 실패 모드 — 정면/측면/평면을 넘나드는 다중 뷰 추론이 특히 약함. → **[출처](https://www.businesswaretech.com/blog/benchmark-testing-ai-models-on-engineering-drawings)**

2. **2D 정투영(평면·입면·단면) → 3D 복원은 1970년대부터 연구된 고전 CAD 문제**. 깨끗한 데이터면 알고리즘으로 풀리지만, 실세계 도면에선 여전히 난제. 최신 연구(ICCV 2023 PlankAssembly, 2024 arxiv 2412.11892)도 **"정확히 3개 축정렬 뷰"**를 전제. → **[리뷰 논문](https://www.mdpi.com/2673-4117/5/2/42)**

3. **상용 AI 도면→BIM 도구는 이미 존재**(Plans2BIM, WiseBIM, Higharc, archBIM.cloud). 업계 현실은 **"AI 60~80% + 사람 검수"**. 그리고 대부분 **평면도만** 지원, 다중 뷰 통합은 아직 상용화 초기.

**함의**: Claude 단일 LLM이 20장 다중 뷰를 읽어 일관된 3D를 누적하는 것은 현재 기술로 **매우 어려움**. 대안 아키텍처 3개 중 선택 필요 (02 문서).

---

## 문서 지도 (신판)

| # | 파일 | 내용 | 길이 |
|---|---|---|---|
| 1 | [01-evidence.md](01-evidence.md) | 리서치로 확인된 사실 + 출처 링크 | 중 |
| 2 | [02-options.md](02-options.md) | 실행 가능한 3개 아키텍처와 trade-off | 중 |
| 3 | [03-smallest-experiment.md](03-smallest-experiment.md) | 타당성 실측을 위한 최소 실험 설계 | 짧음 |
| **4** | **[04-session-2026-04-21-ultrathink.md](04-session-2026-04-21-ultrathink.md)** | 오늘 세션 실측 + agentic 재설계. 2D vs 3D 정보 분리, 다중 시트 종합 전략. | 김 |
| 5 | [05-claude-api-roadmap.md](05-claude-api-roadmap.md) | Claude API Agent SDK 이식 전략 (tool mapping·비용·go/no-go 조건) | 중 |
| **6** | **[06-agent-implementation-phases.md](06-agent-implementation-phases.md)** | **Phase × Step 실행 계획 (MVP 성공 후 착수용). ⭐ 다음 세션 시작 문서.** | **김** |
| MVP | [threejs-scene/p062/decisions.md](threejs-scene/p062/decisions.md) | **MVP 실측 버그 3종 + Gate 판정 + 재사용 교훈**. 다음 세션 필독. | 중 |

---

## 차기 세션 권장 흐름 (2026-04-21 이후 업데이트)

**먼저 읽을 것**: `06-agent-implementation-phases.md` 의 "전체 체크리스트". MVP(Phase 0) 완료, 다음은 Phase 1 (Tool Surface 구현).

그 전에 context 필요하면:
- `threejs-scene/p062/decisions.md` — MVP 버그 3종·Gate 판정 (필독)
- `05-claude-api-roadmap.md` — tool mapping 및 예상 비용
- `04-session-2026-04-21-ultrathink.md` §7 — 에이전틱 재설계 배경

짧게:
1. `_png_dpi400/` 시트 전수조사 → 입면도·단면도 유무 확인
2. Knowledge Base Phase 1 착수 (시트별 YAML + 교차 인덱스)
3. 3D용 좁은 프롬프트 추가 (11-grid / 12-slab / 13-cores)
4. 에이전트 런타임 시범 (Claude Code 내에서 수동 orchestrate)

**이전 경로 (아직 유효)**:
1. `01-evidence.md` 읽고 가정 맞춤
2. `02-options.md`에서 A/B/C 중 하나 합의 (단, 04에서 agentic 관점 추가됨을 반영)
3. `03-smallest-experiment.md` — 이미 실행 완료. 결과는 `04` §1 참조.

---

## 이 리서치가 뒤엎은 이전 가정

| 이전 문서의 추측 | 실증 결과 |
|---|---|
| "Claude Vision이 도면을 읽어 Three.js 코드를 생성한다" | 정확도 ~40%. 단순 누적 가정 불가 |
| "15장이면 200k 컨텍스트 여유" | 토큰은 맞음. 하지만 컨텍스트가 커도 **정확도가 낮아** 무의미 |
| "Sonnet 4.6으로 $3~6" | 비용 추정은 근접. 다만 정확도가 낮으면 비용은 관심사가 아님 |
| "중간 리팩터 턴으로 코드 압축" | 리팩터 이전에 정확도 자체가 문제 |
| "Three.js 우선" | 엔진 선택은 지엽. 병목은 **AI의 도면 읽기 정확도** |

**교훈**: 엔진·비용·프롬프트 설계는 실제 벤치마크 근거 없이 미리 설계하면 무의미하다. **정확도 실측이 먼저**.
