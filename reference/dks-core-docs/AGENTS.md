# AGENTS.md — 데이터 지식 스튜디오

> Codex가 이 폴더에서 작업할 때 참조하는 프로젝트 컨텍스트
> 완료 이력 상세: `Codex-달성상태-아카이브.md`
> 파일 경로 바로가기: `Codex-참조-인덱스.md`

---

## 프로젝트 정의

**데이터 지식 스튜디오 (DKS)** = 도면(DWG/PDF) + 문서(PDF/준공문서) → AI 분석 → 구조화 지식(온톨로지) + 비정형 지식(RAG) → 검색/API 제공

두 가지 지식 채널을 하나의 시스템으로 통합:
- **구조화 채널**: 도면 → Phase 0 분석 → Phase 1 온톨로지(TypeDB) → 설비 관계 추론
- **비정형 채널**: 문서/도면 텍스트 → RAGflow → 벡터 DB → 자연어 검색

고객 접점: **도면정보관리** 서비스 (프론트엔드) — DKS 지식을 고객이 직접 사용하는 서비스 UI

### 핵심 문제
> 도면과 문서에 갇혀 있는 설비 지식을, 누구든(사람이든 AI든) 질문하면 답을 얻을 수 있는 시스템으로 바꾸는 것

### 제품 포지셔닝: 맥락 엔진 (Context Engine)

- **본질**: 범용 AI는 산업 설비의 물리적 인과관계를 모른다. DKS는 그 인과관계를 온톨로지로 구조화하여 AI에게 "떠먹여 주는" 맥락 엔진
- **경쟁 우위**: 코어 모델은 빅테크가 만든다. DKS는 그 위에 산업 도메인 맥락을 입히는 "산업용 차체"
- **신뢰성**: 수학/물리 로직으로 1차 인과관계 → AI(SLM)가 2차 해석 (Dual Engine). 할루시네이션 구조적 통제
- **확장**: 하나의 도메인에서 성공 → 다른 도메인으로 확장. 프로젝트 늘수록 도메인 지식 축적

### 장기 비전 — 역방향 도면 생성 (Reverse Rendering) — 2026-04-20 추가

추출 정보 기반 **AI 도면 생성 + Canvas 기반 대화형 편집**. 최종 목표는 **[[CAD]] 수준 정확도** ([[DWG]]/[[DXF]] 출력).

**핵심 원리**:
- DKS 온톨로지 = 진실의 원천, Canvas = 뷰
- 보유 자원: Phase 0 파싱된 원본 page image + 추출 구조(panels/connections/groups/entity_details)
- AI 대화로 설비 추가·이동·연결 변경 → 온톨로지 업데이트 → Canvas 리렌더
- 수정 단위가 픽셀이 아닌 **온톨로지 엔티티/관계**

**3단계 로드맵**:
| 단계 | 수준 | 기간 | 내용 |
|:----:|------|:----:|------|
| 1 | Diagrammatic | 2~4주 PoC | 블록·연결·그룹 렌더 (tldraw/react-flow) |
| 2 | Schematic | 2~3개월 | 심볼 라이브러리 + 배치 알고리즘 |
| 3 | CAD 정확도 | 6개월+ | DWG/DXF 출력, 축척·좌표 보존 |

**활용 연결점**:
- 운영자 시나리오의 영향도 분석 시각화
- AI 인사이트 목업 v2 RootCauseFinder 탐정보드 확장
- 도면정보관리 서비스의 서비스화 — "검색·이해·편집" 통합 UI
- 최종 제품 차별화 포인트 — 경쟁 제품 부재 영역

---

## 아키텍처 개념

### 전체 시스템 아키텍처

```
도면(DWG/PDF) + 문서(준공/매뉴얼)
    │
    ├─ [구조화 경로] Phase 0 → Phase 1 → TypeDB
    │       도면 AI 분석 → 설비 온톨로지 → 관계 추론/영향도 분석
    │
    └─ [비정형 경로] RAGflow 자동 수집
            문서 텍스트 → 벡터 DB → 자연어 검색
    │
    ▼
도면정보관리 서비스 (프론트엔드)
    └─ 고객이 직접 사용하는 통합 서비스 UI
         ├─ 설비 검색 (Graph + Vector 하이브리드)
         ├─ AI 채팅 (자연어 질의)
         └─ 영향도 분석 (Multi-Hop 추론)
```

### 도면 분석 파이프라인 (Phase 0)

```
PDF 도면 → parse_pdf.py → 텍스트 + 400DPI PNG
→ 에이전틱 파이프라인 (7개 도구, GPT-mini + Gemini Flash)
  ├─ entity_list + legend + entity_details + page_context
  └─ HITL Gate (Opus 자동 평가, 품질 미달 시 재실행)
```

> 상세: `_Python_code/phase0_v1_31/`, 에이전틱 작업 지시서: `_Python_code/WORK_ORDER-에이전틱-Phase0.md`
> 현행 버전: v1.31 (2-Stage Vision, 데이터 손실 수정 완료)

### 온톨로지 구축 파이프라인 (Phase 1)

```
Phase 0 산출물
→ [1단계] 도메인 정의 (Sonnet)
→ [2단계] 개념 수집 (Sonnet)
→ [3A/3B] 개념+관계 정의 (Sonnet)
→ [4단계] 계층 구조 개발 (4-Tier: 소형→중형→Sonnet→Opus)
→ [5단계] 속성/관계 개발 (소형교차→중형교정→Sonnet검증→Opus코딩)
→ [6단계] 인스턴스 개발 (Phase 0 데이터 → OWL Individual)
→ [7단계] 추론 품질 검증 (코드자동+Sonnet — 소비자 3종 추론 테스트)
→ [8~9단계] 반복 조정 + TypeDB 배포 (설계 완료 — D39~D48)
```

> 상세: `docs-표준-typedb-v1/README.md`
> 실행 결과 + 블루프린트: `docs-표준-typedb-v1/실행결과/_누적/마스터-블루프린트.md`

### V3.2 온톨로지 표준 (참고용, 강제 아님)

> 현장 데이터에서 관찰된 것이 정답. V3.2는 가이드.
> 상세: `docs-표준-typedb/README.md`, 스키마: `docs-표준-typedb/schema_yaml_v3/`

- 3종 필드 아키텍처: TQL 변환 + Validator 검증 + AI 프롬프트
- 7개 YAML: enums, attributes(27), entities(31), relations(10), rules(4), axioms(22+14), _meta
- V3.2 핵심: 카테고리 계층(Main/Sub), 엔티티 상세(1tag=1file), specification 관계

---

## 현재 상태 (2026-04-20)

| 구분 | 상태 |
|------|:----:|
| Phase 0 원샷 파이프라인 | ✅ |
| Phase 0 에이전틱 파이프라인 v2.0 | ✅ |
| **Phase 0 표준 프롬프트** | ✅ P-00 v1.31 / P-0.5 v2.2 / P-4.5 v1.32 |
| **Phase 0 0-9a~e 재설계** | ✅ |
| **06_전기 Phase 0 완주** | ✅ 283 태그 |
| **04_기계 Phase 0 완주** (2026-04-20) | ✅ 94 설비 / 30 클래스 / $8.85 |
| V3.2 온톨로지 스키마 | ✅ |
| Phase 1 1~9단계 설계 | ✅ (D1~D48 확정) |
| Phase 1 건축 1~6단계 실행 | ✅ (38 클래스, 58 인스턴스, HermiT PASS) |
| Phase 1 누적 시스템 (블루프린트) | ✅ |
| **Phase 1 풀스택 5계층 (Stage A~E)** (2026-05-03) | ✅ |
| **★ Phase 1 청주 모듈러 OWL 6단계 빌드** (2026-05-04) | ✅ 1668 individuals |
| **★★ X-P1-007 IRI 정규화 자동 가드** (2026-05-05) | ✅ |
| **★★ X-P1-008 Datatype alignment 자동 가드** (2026-05-05) | ✅ |
| **★★★ 청주 v10.6 HermiT consistent=True** (2026-05-05) | ✅ 36.7s |
| **★★★ Stage 7-A 무손실 매트릭스 PASS** (2026-05-05) | ✅ 0% 손실 |
| **★★★ Stage 7-B CQ + HermiT 최종 PASS** (2026-05-05) | ✅ 90% 답변 |
| 시나리오 S2~S6 | ✅ (S1 운영자 미작성) |
| 비즈니스 플랜 | ✅ 제출 완료 |
| DB 전략 | TypeDB 유지 + RAG 이원 구조 |
| Gate-7 재설계 | ⏸ 보류 (다분야 2+ / Phase 1 0단계 확정 선결) |
| 다분야 Phase 0 (건축/통신 등) | ⏳ 대기 |

> 완료 항목 상세 → `Codex-달성상태-아카이브.md`
> 최근 세션 종료 문서 → `_Python_code/SESSION-CLOSE-20260502c.md` (Phase 1 정보 손실 0% + 모듈러 OWL 재설계 결정)

---

## 시나리오 vs 실제 코드 간극 (주의)

| 항목 | 시나리오 | 실제 코드 |
|------|---------|----------|
| 처리 단위 | 그룹별 독립 | PDF 전체 일괄 |
| 텍스트 추출 | DWG→DXF | PDF 직접 (PyMuPDF) |
| 온톨로지 생성 | 그룹별 → 통합 | 프로젝트 단위 일괄 |

---

## 기술 스택

```
온톨로지(구조화) — TypeDB (OWL→TQL 파이프라인 준비)
문서 RAG(비정형)  — RAGflow (확정) — 자동 수집 + 벡터 DB + 자연어 검색
서비스 프론트엔드  — 도면정보관리 (고객 접점 서비스 UI)
모델 라우팅: 초벌=Gemini Flash, 종합=Sonnet, 판단=Opus
```

### 비즈니스 모델 (제출 완료)

3단계 과금: 구축비(일시불) → 서버납품(선택) → AI 질의 구독(월정액 크레딧)
> 상세: `docs-마일스톤메모들/DKS-비즈니스모델-상세설계.md`

---

## AI 모델 역할 분담

> 소형 모델 결과를 사람이 직접 전수 검수하는 것은 불가능. 대형 모델이 검수, 사람은 플래그만.

```
[소형] GPT-5.4-mini + Gemini Flash   → Phase 0 초벌, Phase 1 4-A 초안
[중형] GPT-5.4 + Gemini Pro          → Phase 1 4-B 검증
[대형] Sonnet 4.6                     → Phase 1 1~3단계, 4-C 교차비교
[최대] Opus 4.6                       → Phase 1 4-D 최종 판단 (사람 대행)
```

- 코드 = 오케스트레이션 최소 용도. 비즈니스 로직은 프롬프트에, 판단은 AI에게.

---

## 다음 단계

> **현재 위치**: Phase 1 풀 통과 (HermiT consistent + Stage 7-A/B PASS, 2026-05-05)

```
[완료] Phase 1 1~7단계 상세설계 (D1~D38 확정)
[완료] Phase 1 8~9단계 상세설계 (D39~D48, 8-A/8-B/8-C + 9단계)
[완료] Step 0-9 설계 (S2-05e, 온톨로지 준비도 검증)
[완료] 건축 1~6단계 실행 → 블루프린트 누적
[완료] Phase 0 v1.31 코드 구현 + 9분야 완주
[완료] Phase 1 1~6단계 풀스택 구현 (5계층 + 모듈러 OWL)
[완료] X-P1-006/007/008 OWL 2 DL 5계층 자동 가드 (★ 2026-05-05)
[완료] 청주 v10.6 빌드 — HermiT consistent=True 첫 시도 ★
[완료] Stage 7-A 무손실 매트릭스 PASS (45/45 TRACED, 0% 손실)
[완료] Stage 7-B CQ + HermiT 최종 S7-7 PASS (90% 답변)
[다음] Stage 7-C 운영자 시나리오 multi-hop (D-P1-21 §2-A/B/C/D)
[다음] Stage 8 통합 머지 + Stage 9 TypeDB 배포 박제 + 코드
[다음] 제주 프로젝트 — 5계층 가드 자동 적용
  → 도면정보관리 서비스 프론트엔드 개발
  → RAGflow 연동 (비정형 지식 파이프라인)
```

**진입점**: `데이터 지식 스튜디오/docs-표준-typedb-v1/README.md` (2026-05-05 갱신).

---

## DKS 계층 구조 (2026-03-27 확정)

```
프로젝트 (Project) ← 모든 서비스의 진입점
  ├── 도면관리 (Drawing Management) ← Phase 0 산출물 (그룹별)
  │     └── 그룹 (Group) ← 분석의 기본 단위
  ├── 지식관리 (Knowledge Management) ← 프로젝트 단위
  │     ├── 구조화 지식: 통합 온톨로지 YAML (V3.2) → TypeDB
  │     └── 비정형 지식: 문서/텍스트 → RAGflow → 벡터 DB
  └── 서비스 레이어
        └── 도면정보관리 (프론트엔드) ← 고객 접점, DKS 지식 사용 UI
```

---

## 시나리오 기반 PRD

| # | 시나리오 | 상태 |
|:-:|---------|:----:|
| 1 | 운영자 — 장애 대응, 점검 | ❌ 미작성 |
| 2 | 지식 엔지니어 — 도면→AI→HITL | ✅ 15개 |
| 3 | 유지보수/KaaS — 설비 교체, 내보내기 | ✅ S3-01~04 |
| 4 | 온톨로지 구축 | ✅ |
| 5 | TypeDB 적용/배포 | ✅ |
| 6 | RAG 시스템 | ✅ |

> 상세: `docs-시나리오/README.md`
> 시나리오 → PRD → 기술스택 → 개발로드맵 → 구현

---

## 대상 시장

| 시장 | 설비 유형 | 도면 종류 |
|------|----------|----------|
| **데이터센터** | CRAC, UPS, PDU, 냉각탑 | P&ID, 단선도 |
| **빌딩 관리** | 공조기, 냉동기, 보일러 | 배관도, 계통도 |
| **공장/제조** | 로봇, 컨베이어, PLC | 배치도, 결선도 |
| **수처리** | 펌프, 여과기 | P&ID |

---

## 미결정 사항

- 서비스 방식 (B2B API vs B2B SaaS)
- 첫 번째 고객 도메인 (데이터센터/빌딩/공장)
- DWG 변환 방식 (ODA / LibreDWG)
- Graph DB 최종 (TypeDB 유지, AGE 대안) → PoC 후 확정

---

## 문서 작성 규칙

- 상위 AGENTS.md의 Obsidian 응답 형식 준수 (YAML 프론트매터, [[키워드]] 링크)
- 제안서/보고서는 개조식 문법 적용
- 설비 종류 첫 등장 시 [[링크]] 필수

---

## 분야별 표준 프롬프트 진화 철학 (2026-04-13 확립)

Phase 0의 `prompts/phase0_v2_0/discipline/{분야}/{_general|genre_*}/supplement_*.yaml`은
**프로젝트 중립 분야 표준**이다. 도면 분석 경험이 누적될수록 다양해지고 상세해지는 살아있는 표준.

### 4대 원칙
1. **표준 vs 전문가 supplement 분리**: 표준 프롬프트(P-00 ~ P-13)는 분야 중립. 분야·장르 전문 지식은 supplement에 분리.
2. **분야 × 장르 2축**: 같은 분야 안에서도 장르(단선도/평면도/계통도/일람표 등)별로 추출 대상이 달라지므로 분리. 표준 → `_general/` (fallback) → `genre_{X}/` (장르 매칭).
3. **본문은 분야 일반 패턴만**: supplement YAML 본문에 특정 프로젝트 태그(예: SHV-1101, EE-01-001)·도면번호·건물명·실명 사용 금지. 일반 카테고리/패턴/spec 키 정의만.
4. **evidence 메타화**: 근거 도면은 `source` 필드와 README의 "근거 도면" 표에만 명시. 본문에는 표기하지 않음.

### 진화 루프
```
새 도면 분석 → 새 패턴 발견 → supplement에 일반화 형태로 누적 → version 증가 → source에 evidence 추가
```
분석 도면 수가 많을수록 supplement는 더 다양·상세·정확한 분야 표준으로 발전.

### 위반 시 손해
- 본문에 청주 태그가 박혀 있으면 다른 프로젝트 도면 분석 시 잡음·혼동을 일으킴.
- "왜 내 도면 분석 가이드에 청주 태그가?" 같은 신뢰 손상.

> 상세: `_Python_code/prompts/phase0_v2_0/discipline/README.md` + memory `feedback_prompt_evolution_philosophy.md`

---

## Phase 1 개발 체계 (2026-05-03 Stage E 완료)

### 설계 원칙

**프로젝트 1개 = OWL 1개**. 9개 분야 Phase 0 산출물을 한 번에 취합하여 단일 통합 온톨로지를 구축.

Phase 0 Step 0-9가 분야별로 만들어낸 온톨로지 힌트들(class_taxonomy, object_properties,
data_properties, axioms, placement)을 **주 입력**으로 사용. entity_details는 검증·검색
도구로만 AI가 접근.

### Phase 1 풀스택 5계층 인프라 (Stage E 완료 — 모두 Stage 3A/3B에 내장)

| 계층 | 구성 요소 | 위치 |
|------|----------|------|
| L1 Skeleton | IRI 정규화 + 관계·클래스 뼈대 pre-fill | `phase1/skeleton/` |
| L2 표준 프롬프트 | DPP 방어 프롬프트 (4 yaml) | `prompts/phase1/dpp/` |
| L3 분야 supplement | 9분야 + core (빈 골격 → 다음 프로젝트에서 본문 채워짐) | `prompts/phase1/discipline/` |
| L4 DPP | 결함 카탈로그 + novel 수확 + defect_classifier | `phase1/defect_classifier.py` |
| L5 검증·보정 | invariant_checker + auto_corrector + fingerprint | `phase1/validator/`, `phase1/fingerprint/` |

### 문서 위치

| 역할 | 위치 |
|------|------|
| **Phase 1 설계 표준 (1~9단계)** | `docs-표준-typedb-v1/README.md` + `0N-*.md` |
| **Phase 1 시나리오** | `docs-시나리오/` (Phase 0 시나리오와 동일 폴더) |
| **Phase 1 실행 코드** | `_Python_code/phase1/` |
| **Phase 1 프롬프트** | `_Python_code/prompts/phase1/` |
| **Phase 1 산출물 (YAML/OWL)** | `_Python_code/projects/{프로젝트}/phase1/{run_id}/` |
| **누적 경험 (블루프린트)** | `docs-표준-typedb-v1/실행결과/_누적/마스터-블루프린트.md` |
| **★ Phase 1 회귀 로그** | `docs-표준-typedb-v1/X-P1-NNN.md` (현재 X-P1-001) |
| **★ regression 테스트** | `_Python_code/tests/phase1/regression/` (27 PASS) |
| **fingerprint 모듈** | `_Python_code/phase1/fingerprint/` |
| **supplement 효과 측정** | `_Python_code/phase1/supplement/effect_measurer.py` |

### Phase 1 산출물 폴더 구조

```
_Python_code/projects/{프로젝트}/phase1/{run_id}/
  ├── stage0_5/                   ← 코드 자동 (AI 없음)
  │     └── project_integrated_package.yaml  ← 9개 분야 통합 패키지
  ├── stage1/domain_definition.yaml
  ├── stage2/concept_inventory.yaml
  ├── stage3a/concept_dictionary.yaml
  ├── stage3b/relation_definitions.yaml
  ├── stage4/hierarchy.owl
  ├── stage5/properties.owl
  ├── stage6/complete.owl
  └── stage7/validation_report.yaml
```

### Phase 1 Stage별 입력 원칙

| Stage | 주 입력 (직접 투입) | 보조 (도구 조회) |
|:-----:|-------------------|----------------|
| 0.5 (코드) | 9개 분야 `ontology_rules/` + `placement/_report` | — |
| 1 | 9개 `ontology_plan` + 0.5 통합 패키지 요약 | — |
| 2 | 9개 `class_taxonomy` 통합 + stage1 | entity_details (도구) |
| 3A | stage2 + 9개 `data_properties` 통합 | entity_details (도구) |
| 3B | stage3A + 9개 `object_properties` + `axioms` 통합 | — |
| 4~6 | stage3 산출물 | entity_details (도구) |
| 7 | 완성 OWL | entity_details (역질의 검증) |

### Phase 1 모델 전략 (검토 중)

대형 2M 컨텍스트 모델 우선 사용:
- Gemini 2.0 Flash / Gemini 3.1 Pro (2M)
- GPT o3 / GPT-5.5 최신 (2M)

교차 검증 적용 단계 (안):
- Stage 2 (클래스 통합): Gemini 2M + GPT 2M 교차 → Sonnet 최종
- Stage 3B (관계 정의): Gemini 2M + GPT 2M 교차 → Sonnet 최종
- 나머지: 단일 대형 모델 (Gemini 2M 기본)

> 상세 설계: `_Python_code/phase1/README.md`

---

## 핵심 참조

> 상세 참조 인덱스: `Codex-참조-인덱스.md`

> **Phase 0 도면 분析 착수 전 / 결과 평가 시 필수 확인**:
> 해당 분야 이슈 로그를 먼저 읽을 것. 알려진 오류 패턴을 재발견하거나 해결 여부를 모른 채 평가하는 낭비를 방지.
> - 전기: `_Python_code/prompts/phase0_v2_0/discipline/electrical/README.md §5`
> - 기타 분야: `discipline/{분야}/README.md §5` / 분야 횡단 공통: `discipline/README.md §11.A`
> - **표준 프롬프트/코드 회귀**: `discipline/README.md §11.B` (X-NNN) — P-XX 또는 orchestrator 변경 시 필독

| 작업 | 진입점 |
|------|--------|
| **Phase 0 Step별 모델 매핑 (★v2.5 확정)** | `AI-API-가격비교-2026-03.md §0` 또는 `_Python_code/phase0_v2_0/README.md` |
| **분야 이슈 로그 (Phase 0 분析 전 필독 ★)** | `_Python_code/prompts/phase0_v2_0/discipline/{분야}/README.md §5` |
| **분야 횡단 이슈 승격 테이블** | `_Python_code/prompts/phase0_v2_0/discipline/README.md §11.A` |
| **표준 프롬프트/코드 회귀 로그 (★ P-XX·orchestrator 변경 시 필독)** | `_Python_code/prompts/phase0_v2_0/discipline/README.md §11.B` |
| **9단계 프로세스 진입점 (★)** | `docs-표준-typedb-v1/README.md` |
| **Phase 1 코드 가이드 (★)** | `_Python_code/phase1/README.md` |
| **Phase 1 프롬프트** | `_Python_code/prompts/phase1/` |
| Phase 1 실행 + 블루프린트 | `docs-표준-typedb-v1/실행결과/` |
| **코딩 블루프린트 (★)** | `docs-표준-typedb-v1/실행결과/_누적/마스터-블루프린트.md` |
| **OWL 에러 핸들링 (★)** | `docs-표준-typedb-v1/기술검토-OWL생성-에러핸들링.md` |
| **7단계 추론 검증 설계** | `docs-표준-typedb-v1/08-7단계-검증.md` |
| V3.2 스키마 | `docs-표준-typedb/schema_yaml_v3/` |
| 에이전틱 아키텍처 | `docs-마일스톤메모들/에이전틱-아키텍처-설계-메모.md` |
| 에이전틱 작업 지시서 | `_Python_code/WORK_ORDER-에이전틱-Phase0.md` |
| 시나리오 / PRD | `docs-시나리오/README.md` |
| 비즈니스 모델 | `docs-마일스톤메모들/DKS-비즈니스모델-상세설계.md` |
