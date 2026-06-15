# 01 · 정보검색 SaaS의 필수 기능·평가 기준 (일반론)

> **문서 성격**: 특정 도메인(도면/BIM)을 배제하고, "정보를 찾아주는 SaaS"가 2026년 기준으로 어떤 기능 블록·평가 지표를 **공통적으로** 갖춰야 하는지 정리. 다음 문서(02)에서 도면으로 좁힌다.

---

## 1. 기능 블록 6개 (필수)

| 블록 | 역할 | 최소 기준 (MVP) | 베스트 프랙티스 (엔터프라이즈) |
|---|---|---|---|
| **B1. 통합 인덱싱** | 흩어진 소스를 하나의 인덱스로 | JSON 시드 + 단일 필드 `snippet` | 100+ 커넥터(Drive/Slack/Confluence/DB), 증분 동기화, ACL 보존 |
| **B2. 하이브리드 검색** | 키워드 정확도 + 의미 재현율 | Fuse.js 퍼지 매칭 | BM25 + dense vector(임베딩) + learned re-rank |
| **B3. 패싯/필터** | 결과 정제 | 학제·종류 칩 2종 | 다중 패싯 AND/OR, 범위 필터(날짜·버전), 저장된 필터 |
| **B4. 권한/개인화** | 사용자마다 다른 결과 | 없음 (단일 사용자) | RBAC + ABAC, role 가중치, 이력 기반 re-rank |
| **B5. 응답 합성** | 결과를 "답"으로 | 제목+스니펫 하이라이트 | RAG 답변 카드 + 인용 핀(citation pin) + 근거 하이라이트 |
| **B6. 피드백/분석** | 학습·품질개선 | 클릭 집계 | thumbs/좋아요 + zero-result·abandon 지표 + A/B |

**현재 프로젝트 진단** (기존 `(s1)` 홈 화면 기준):
- ✅ B1(JSON 시드), ✅ B2(Fuse), ✅ B3(학제·종류 칩), ❌ B4, ❌ B5, ❌ B6
- Insight Lab `(s2)/insight/lab`은 B5(답변 합성)를 별도 트랙에서 실험 중

---

## 2. 하이브리드 검색 — 왜 키워드만으로는 부족한가

2026년 엔터프라이즈 서치의 공통 결론: **"의미 이해와 필터의 결합이 새 기본값"**. 벡터 검색만으로는 고유 태그(`CH-001`, `VCB-001`)를 못 찾고, 키워드만으로는 "냉동기 고장" 같은 맥락을 못 잡는다.

| 전략 | 강점 | 약점 | 쓰기 좋은 곳 |
|---|---|---|---|
| 키워드(BM25/Fuse) | 고유 식별자·약어 정확 매칭 | 동의어·오타 약함 | 설비 태그, 문서번호, 규격 코드 |
| 시맨틱(임베딩) | 의도·맥락 포착, 언어 독립 | 고유 태그 희석, 느림 | "비슷한 사례", "이 증상과 관련" |
| 하이브리드(RRF/가중합) | 두 장점 병합 | 튜닝 난이도 | 엔터프라이즈 검색 일반 |
| 학습 재랭크 | 클릭 피드백 반영 | 로그 축적 필요 | 스테이블 운영 단계 |

**적용 포인트**: "냉동기" 같은 일반 키워드는 시맨틱 확장 + 동의어(냉각기·칠러·Chiller), `CH-001`은 키워드 필터로 정확 매칭. 두 경로의 결과를 RRF(Reciprocal Rank Fusion)로 섞는 게 표준.

---

## 3. "좋은 검색 UX"를 판단하는 5축

Gemini 가이드의 정리 + 업계 벤치마크를 병합한 5축. 각 축을 **측정 가능한 지표**로 환산하는 것이 핵심.

| 축 | 측정 지표 | 관측 방법 |
|---|---|---|
| **정확도·재현율** | Top-3 클릭률, zero-result 비율, 사용자 평균 스크롤 깊이 | 이벤트 로그 집계 |
| **속도·반응성** | 첫 결과 p50/p95 지연, 타이핑-to-결과 유휴 시간 | 브라우저 perf marks |
| **가독성** | 하이라이트 피복률, 요약 대비 본문 클릭률 | UX 헤아림 + 사용성 테스트 |
| **출처 투명성** | 인용 클릭률, "출처 불명" 피드백 빈도 | 인용 클릭 이벤트 |
| **피드백 루프** | 👍/👎 응답률, re-query 감소율 | A/B 전후 비교 |

**빠른 체크포인트**: "사용자가 원하는 정답까지 도달하는 비용(**Effort-to-Answer**)"이 1회 검색에서 몇 초·몇 클릭인지가 단일 북극성 지표로 잘 먹힌다.

---

## 4. UI/UX 장치 — 인지 부하를 줄이는 7가지

1. **점진적 공개(Progressive Disclosure)** — 요약 → 상세 확장. 한 번에 다 보여주지 않는다.
2. **자동완성 + 추천어** — 타이핑 중 의도 추정, zero-result 방지.
3. **검색 문맥 유지** — "앞 질문과 연결된 질문" 후속(follow-up) 지원. Chat UI가 대표 사례.
4. **결과 내 하이라이트** — 매칭 토큰·요약 문장 강조. snippet만 줄 때와 비교해 체감 속도 차이 큼.
5. **출처 핀(Citation pin)** — AI 요약 옆에 원문 링크 + 해당 페이지/좌표. 신뢰의 기본값.
6. **저장·공유·알림** — 자주 쓰는 쿼리 저장, 결과 변화 알림(saved search).
7. **Next-Action 연결** — "이 정보 다음에 할 것"(예: 티켓 만들기, 담당자에게 공유)을 결과에 붙이면 UX 수준이 한 단계 올라간다.

---

## 5. 벤치마크 — 대표 4개 플랫폼 비교

| 플랫폼 | 포지션 | 특징 | 이 프로젝트에 시사점 |
|---|---|---|---|
| **Glean** | 워크플레이스 유니파이드 서치 | 100+ 커넥터, 조직 그래프, 개인화 | B1+B4+B5의 "표준형". 우리는 도면 도메인 특화로 차별화. |
| **Coveo** | 엔터프라이즈/커머스 AI 검색 | 추천 엔진, 분석, re-rank ML | B6(피드백/분석)의 레퍼런스. |
| **Algolia** | API-first 검색 (커머스 중심) | NeuralSearch, 동의어 자동, sub-50ms | B2/B3의 속도 기준선. |
| **Elastic/OpenSearch** | 오픈 플랫폼 | BM25+ANN 벡터, 플러그인 생태계 | 자체 구축 시 백엔드 후보. |

공통 트렌드(2026):
- **Generative answering** 탭이 기본. 결과 리스트와 "답변" 카드를 상단 병치.
- **Citation with source highlighting** — RAG 답 옆에 원문 링크 + 문서 내 하이라이트 좌표까지 돌려주는 게 신뢰의 기본값.
- **Hybrid RAG**가 프로덕션 기본 아키텍처로 자리 잡음 (벡터 + 키워드 + 그래프).

---

## 6. 이 문서의 결론 (다음 문서로 연결)

"정보 검색 SaaS = 인덱싱 + 하이브리드 쿼리 + 패싯 + 합성 답변 + 피드백"의 5축이고, 각 축을 측정 지표로 묶어 **Effort-to-Answer를 최소화**하는 것이 UX의 본질이다.

도면 기반 검색은 여기에 **"공간 인지(spatial awareness)"와 "관계 탐색(graph traversal)"** 두 축이 추가된다. 다음 문서에서 다룬다 → [02-drawing-specialized-patterns.md](./02-drawing-specialized-patterns.md).

---

## 참고

- [The definitive guide to AI-based enterprise search for 2025 — Glean](https://www.glean.com/blog/the-definitive-guide-to-ai-based-enterprise-search-for-2025)
- [Top Enterprise Search Software in 2026 — 15 Best Tools — GoSearch](https://www.gosearch.ai/blog/enterprise-search-software-2026/)
- [Best Enterprise Search Tools 2026 — Onyx AI](https://onyx.app/insights/enterprise-search-tools-2026)
- [Advanced Search UX: Best Practices — UXPin](https://www.uxpin.com/studio/blog/advanced-search-ux/)
- [Create a great faceted search & navigation UX — Algolia](https://www.algolia.com/blog/ux/faceted-search-and-navigation)
- [Faceted Filtering Meets Vector Search — Google Cloud](https://medium.com/google-cloud/faceted-filtering-meets-vector-search-building-a-dynamic-hybrid-retail-experience-with-alloydb-d28434ee94ef)
- [RAG in 2026: How Retrieval-Augmented Generation Works — Techment](https://www.techment.com/blogs/rag-in-2026/)
- [Detailed review of the best RAG capabilities for enterprise search — Glean](https://www.glean.com/perspectives/best-rag-features-in-enterprise-search)
