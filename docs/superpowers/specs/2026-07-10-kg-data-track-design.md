# 지식그래프 데이터 트랙 (Stage 1) — 설비 공존 relates_to 설계 스펙 (FROZEN · 2026-07-10)

> **STATUS: FROZEN.** 세션31 브레인스토밍 Q1·Q2 + §11 열린 결정(O1=1·O2=12·O3=보존) 사용자 확정 완료. writing-plans 착수.
> 이 스펙 = **데이터 트랙 Stage 1**(설비 공존 우회로 `relates_to(track=llm)` 후보 실공급). Stage 2(GATE-7 실 LLM 의미해석)는 **후속 스펙**.
> 계승: 읽기 ①②③④(세션28 `ff020a5`) · ⑥ write-back(세션30 `4b0beba`). 이 트랙이 ⑥의 승격 대상 데이터를 처음 실공급한다.
> HARD 불변식: TypeDB 물리분리 · AI 사이드카(8002) 격리 · 8000 egress 0 · 빌드 멱등 · 회귀 0 (§9).

---

## 0. 왜 이 트랙인가 — 모든 문제의 뿌리 (세션30 코드 실증)

세션30 후반, "가장 근본적이고 모든 문제가 연결되는 것"을 코드로 실증한 결론 = **데이터 트랙이 근본**이다. ⑤ 라우팅·canvas e2e 육안·⑥ write-back 실데이터 육안이 전부 여기에 매달린다.

### 근본원인 — 어휘 벽 (relates_to(llm) = 0)

```
provider.analyze (관계 생성)        build_knowledge_graph.py (매핑)
  시트 추출태그 공출현             tag_to_eq = {설비 큐레이트태그 → eq:id}
  → src_tag / dst_tag       ✗교집합0✗   → 매핑 실패 → 전량 drop
  (LV-6, TR-1201 …)                     (MTR-1, VCB-22.9KV …)
```

관계 생성기는 **시트 추출태그**의 공출현으로 관계를 만드는데, 빌드 매핑은 **설비 큐레이트태그**로만 설비 노드를 찾는다. 두 어휘의 교집합이 0이라 mock이 반환한 관계가 전량 드롭된다(날조 방지 = 설계대로). 그 결과 `relates_to(llm) = 0` — 세션30 ⑥ write-back은 승격할 데이터가 없어 시연 시드로만 검증됐다.

### 이 트랙의 해법 — 어휘 벽 우회 (Stage 1)

관계 생성의 **입력을 바꾼다**: 시트 추출태그 공출현 → **설비 `appears_on` 공존**. 두 설비가 같은 시트에 등장하면(이미 curated `appears_on` 엣지로 존재) 그 설비쌍을 `relates_to(track=llm)` 후보로 만든다.

- **어휘 벽 우회**: 설비→설비 직결. 반환 식별자를 **설비 tag**(= `tag_to_eq`와 동일 어휘)로 하면 매핑 성공.
- **오프라인·무료**: 실 LLM egress 0. 기존 mock 경로(8002, egress 0) 유지.
- **약한 관계**: "같은 도면에 함께 나옴"은 진짜 전원계통 관계가 아니라 **후보**다. 그래서 track=llm(미검증)으로 두고, ⑥ write-back으로 사람이 confirm(실관계)/reject(노이즈)한다.

### 단계적 접근 (Q1 확정)

- **Stage 1 (이 스펙)**: 설비 공존 우회로 파이프라인을 실데이터로 굳힌다(오프라인·무료). ⑥ write-back·⑤ 라우팅·canvas 육안이 이 데이터 위에서 돈다.
- **Stage 2 (후속 스펙)**: GATE-7 실 LLM이 도면을 의미해석해 진짜 전원계통 관계를 공급. 공존 우회가 그 발판이자 fallback.

---

## 1. 공동설계 확정 사항 (세션31 Q1·Q2)

| # | 결정 | 확정 |
|---|---|---|
| D1 | 목적 (Q1) | **단계적** — Stage 1(공존 우회) 먼저 실데이터로 굳히고, Stage 2(실 LLM) 후속 |
| D2 | 노이즈 처리 (Q2-1) | **필터 + 큐레이트 둘 다** — 휴리스틱으로 1차 축소 → 나머지를 track=llm 후보로 ⑥ write-back 큐레이션 |
| D3 | 스펙 스코프 (Q2-2) | **Stage 1만** — Stage 2 실 LLM은 별도 후속 스펙 |
| D4 | 생성 위치 (Q2-3) | **`provider.analyze` 수정** — 공존 스켈레톤 이미 있음, 입력을 시트태그→설비 공존으로 교체 |
| D5 | 반환 식별자 | **설비 tag** — `tag_to_eq`와 동일 어휘라 매핑 성공(어휘 벽 우회의 핵심). build 매핑 로직 무변경 |
| D6 | track | 공존 관계 = **track=llm 후보** — ⑥ write-back의 confirm/reject 큐레이션 루프에 자연 결합(D2) |

---

## 2. 아키텍처 — 기존 파이프라인 재사용, 입력만 교체

```
build_knowledge_graph.py
  _fetch_equipment → equipment[].sheet_ids (curated, appears_on 소스)
  _call_analyze(equipment, sheets)  ← slim_eq 에 sheet_ids 추가 (변경점 1)
        │
        ▼ 8002 /analyze (egress 0)
  provider.analyze(equipment, sheets)  ← 공존 소스를 설비 sheet_ids 로 (변경점 2)
        │  두 설비가 공유 시트 ≥ 임계 → relates_to, src_tag/dst_tag = 설비.tag
        ▼
  build: tag_to_eq[설비 tag] 로 매핑 (무변경 — 어휘 일치)
        → edges += {relates_to, track:"llm"}
        ▼
  uploads/_knowledge_graph.json (멱등)  →  ⑥ write-back 오버레이가 승격/거부
```

- **최소 변경 2점**: (1) `_call_analyze` slim_eq에 `sheet_ids` 추가, (2) `MockExtractProvider.analyze` 공존 소스 교체. build 매핑·저장·⑥ write-back·읽기 API 전부 무변경.
- **격리 유지**: provider는 8002 사이드카(backend import 0). egress 0(mock). GATE-7(실 LLM)은 이 스펙 밖.
- **멱등 유지**: build는 여전히 오버레이를 모른다. 공존 관계는 매 재빌드 재생성되고, 사람 승격은 오버레이(⑥)에 영속.

---

## 3. 알고리즘 — 설비 공존 관계 생성 (`MockExtractProvider.analyze`)

### 3.1 입력

- `equipment`: `[{tag, type, sheet_ids: [sid…]}, …]` (slim_eq에 sheet_ids 추가)
- `sheets`: 기존대로(text_excerpt·tags) — Stage 1에서는 공존 소스로 **쓰지 않음**(설비 sheet_ids가 소스). 계약 유지용으로 시그니처는 보존.

### 3.2 절차

```
1. sheet_to_eqs: 각 시트 → 그 시트에 appears_on 하는 설비 tag 집합 (equipment[].sheet_ids 역인덱스)
2. 시트당 설비 수 상한(MAX_EQ_PER_SHEET) 초과 시트는 스킵      ← 필터 A (폭발 억제)
3. 각 시트에서 설비쌍(i<j) 조합 → pair_shared[(tagA,tagB)] += 1  (공유 시트 수 누적)
4. 공유 시트 수 ≥ MIN_SHARED_SHEETS 인 쌍만 채택              ← 필터 B
5. relations += {src_tag:A, dst_tag:B, relation:"relates_to",
                 confidence: clamp(BASE + STEP*shared, ..CAP),  ← 공유 수로 신뢰 스케일
                 evidence: f"공존 시트 {shared}개: {sids[:3]}"}
```

- **무방향 정규화**: `A, B = sorted([tagA, tagB])` — ⑥ write-back `edge_key`(무방향)와 정합.
- **결정적**: 정렬·집합 연산만, 난수·시계 없음(빌드 규약 계승). 재빌드 동일 결과.
- **egress 0**: 순수 로컬 계산.

### 3.3 confidence

- `< 0.7` = 미검증(O9 정직성 임계값 정합). 공존은 약한 신호이므로 CAP를 0.7 미만으로 두어 **항상 점선(미검증)**으로 표기 → 사람 확인 전엔 절대 권위처럼 안 보이게.

---

## 4. 노이즈 필터 (D2 — 필터 축) — §11 파라미터 승인 대상

한 시트에 N개 설비 → N(N-1)/2 쌍 폭발. 두 휴리스틱으로 1차 축소(나머지는 큐레이트 축):

| 필터 | 파라미터 | 역할 | 기본안(승인 대상) |
|---|---|---|---|
| A. 시트당 설비 상한 | `MAX_EQ_PER_SHEET` | 설비가 과다한 시트(예 계통 총괄도)는 공존 신호가 약함 → 스킵 | **12** (확정 · 현 데이터 max 4로 무발동, 미래 규모 가드) |
| B. 최소 공유 시트 | `MIN_SHARED_SHEETS` | 1개 시트 우연 공존 배제, 여러 도면 반복 공존만 채택 | **1** (확정 · 후보 16쌍, 큐레이트 주도) |
| C. confidence 스케일 | `BASE=0.3, STEP=0.1, CAP=0.65` | 공유 수로 신뢰 차등, CAP<0.7로 항상 미검증 표기 | 위 값 (확정) |

> **필터 vs 큐레이트 균형(D2) — 확정**: MIN_SHARED_SHEETS=**1**. 실 데이터(설비 15·공존 후보 16쌍, 시트당 설비 max 4)에서 폭발 없고 16쌍은 ⑥ write-back으로 관리 가능 → 큐레이트 축 주도. MAX_EQ=12는 현 데이터 무발동이나 미래 도면 반입 대비 가드로 유지.

---

## 5. 규모 가드 (silent-cap 금지)

- 생성 후 `log`로 **후보 수 / 스킵된 시트 수 / 드롭된 쌍 수**를 명시(무음 절단 금지 원칙).
- 상한 초과 시 조용히 자르지 않고, 임계와 실제 수를 리포트해 파라미터 재조정 근거로 남긴다.

---

## 6. build 연동 (변경점 1)

`_call_analyze`의 slim_eq:
```python
slim_eq = [{"tag": e.get("tag"), "type": e.get("type"),
            "sheet_ids": e.get("sheet_ids") or []} for e in equipment]  # sheet_ids 추가
```
- 반환 relations는 기존 매핑 경로(line 165~ `tag_to_eq`)를 그대로 통과 → **build 매핑 무변경**.
- `_norm` 정규화도 그대로(설비 tag 양끝 매핑).

---

## 7. ⑥ Write-back 연결 (D2·D6 큐레이션 루프)

- Stage 1 공존 관계 = `track=llm` → ⑥ write-back의 **confirm(실관계 승격)·reject(노이즈 거부)** 대상.
- 세션30 시연 시드(`seed_demo_llm_edge.py`)는 **불필요해짐** — 실 공존 데이터가 llm 엣지를 공급. 시드 스크립트는 보존(회귀·오프라인 대비)하되 기본 파이프라인은 실데이터.
- 육안: canvas 점선(공존 후보) → 사람 confirm → 실선(curated) / reject → 사라짐. 세션31 브라우저 e2e로 검증한 그 경로.

---

## 8. 데모/시각화 영향

- 지식그래프에 relates_to 점선이 **실제로 다수 출현**(공존 기반) → 세션28 canvas 육안이 실데이터로 의미를 가짐.
- ⑤ 라우팅·에이전틱 AI가 참조할 관계 레이어가 처음으로 비어있지 않게 됨.

---

## 9. HARD 불변식 (회귀 게이트)

1. **빌드 멱등 유지** — provider·slim_eq 변경은 결정적. 재빌드 동일 스냅샷. 오버레이(⑥) 무관.
2. **8002 격리·egress 0** — mock 경로만. backend import 0(AST 가드). GATE-7 실 LLM은 이 스펙 밖.
3. **build 매핑 무변경** — `tag_to_eq` 로직 그대로. 반환 식별자 설비 tag로 어휘 정합(D5).
4. **track=llm 표기** — 공존 관계는 항상 점선·미검증(confidence<0.7). 권위(curated)로 위장 금지.
5. **⑥ write-back·읽기 API 표면 불변** — 이 트랙은 데이터 공급만. 병합·라우트 계약 무변경.
6. **회귀 0** — 세션30 기준선(vitest 135 · 백엔드 kg 43 green · AI 50 · 8002 8) 유지 + 신규 테스트 추가.

---

## 10. 스코프 밖 (명시적 이연)

- **Stage 2 (GATE-7 실 LLM 의미해석)** — 진짜 전원계통 관계(feeds·protects…). 별도 후속 스펙. egress 승인 필요.
- **관계 타입 세분화** — Stage 1은 `relates_to` 단일. feeds/protects 등 방향·의미 타입은 Stage 2.
- **자동 confirm/승격** — 공존은 항상 사람 확인 대상. 자동 승격 없음.
- **⑤ 서비스·툴 라우팅 인덱스** — 별도 스펙(이 데이터 위에서 돎).
- **note/wiki 지식** — describes(llm) note 생성은 Stage 2 LLM 몫.

---

## 11. 열린 결정 — 확정 완료 (세션31)

| # | 결정 | 확정 | 근거 |
|---|---|---|---|
| O1 | `MIN_SHARED_SHEETS` | **1** | 실 데이터 공존 후보 16쌍(≥2면 8쌍). 폭발 없고 16쌍은 ⑥ write-back 큐레이트 가능 → 큐레이트 주도(D2) |
| O2 | `MAX_EQ_PER_SHEET` | **12** | 현 데이터 시트당 설비 max 4로 무발동. 미래 도면 반입 대비 폭발 가드로 유지 |
| O3 | 시드 스크립트 | **보존** | 회귀·오프라인 대비. 기본 파이프라인은 실 공존 데이터 |

> 3건 확정 → STATUS FROZEN. 다음 = writing-plans(세션29 `2026-07-09-kg-writeback.md` 동형 구조) → subagent-driven 구현.

---

## 12. 테스트 전략 (구현계획 Done-When 소스)

**provider (`MockExtractProvider.analyze` · 8002)**
- 공존 계산: 두 설비 공유 시트 1개 → 쌍 1개, 공유 2개 → confidence 상승.
- 필터 A: 시트당 설비 > MAX → 스킵(그 시트발 쌍 0).
- 필터 B: 공유 < MIN → 드롭.
- 무방향 정규화(sorted) · 결정적(재실행 동일) · egress 0.
- 반환 src_tag/dst_tag = 설비 tag(매핑 어휘 정합).

**build 연동**
- slim_eq에 sheet_ids 포함 → provider 반환 relations가 `tag_to_eq`로 매핑돼 relates_to 엣지 생성(0이 아님).
- 실 청주 데이터 빌드: relates_to(llm) **> 0** (근본 지표 해소 확인).

**통합/회귀**
- 세션30 기준선 유지 + 신규.
- ⑥ write-back: 실 공존 llm 엣지 confirm → curated 승격(시드 없이 실데이터로).

---

*작성: 세션31(2026-07-10). 진입점 = 이 스펙 §11 승인 → FROZEN → writing-plans → subagent-driven. HARD-GATE: 설계 승인 전 구현 착수 금지.*
