---
tags:
  - 데이터지식스튜디오
  - 도면지식화
  - 온톨로지
  - 프로젝트맵
aliases:
  - 지식 스튜디오
  - DKS
created: 2026-03-20
updated: 2026-06-11
related:
  - "[[00-비전과-전략적-선택]]"
  - "[[RFP-데이터지식스튜디오]]"
  - "[[01-프로젝트_인계_가이드]]"
---

# 데이터 지식 스튜디오 (DKS)

> **한줄 정의**: 산업 설비 도면(DWG/PDF)에 갇힌 설비 지식을, 누구든(사람이든 AI든) 질문하면 답을 얻을 수 있는 시스템으로 바꾸는 플랫폼

---

## AI 온보딩 가이드

### 읽기 순서

| 순서 | 목적 | 읽을 파일 |
|:----:|------|----------|
| 1 | 프로젝트 전체 지도 | **이 파일 (README.md)** |
| 2 | 개발 컨텍스트 + 아키텍처 | `CLAUDE.md` |
| 3 | 전략/비전/기술 비교 | `00-비전과-전략적-선택.md` |
| 4 | 9단계 온톨로지 구축 | `docs-표준-typedb-v1/README.md` |
| 5 | Phase 1 실행 블루프린트 | `docs-표준-typedb-v1/실행결과/_누적/마스터-블루프린트.md` |
| 6 | 시나리오/PRD 작업 현황 | `docs-시나리오/README.md` |

### 작업별 바로가기

| 작업 | 진입점 |
|------|--------|
| **Phase 1 실행 결과 + 블루프린트** | `docs-표준-typedb-v1/실행결과/` |
| 청주사업장신축 Phase 0/1 결과 | `docs-표준-typedb-v1/실행결과/청주사업장신축/01_건축/` |
| 9단계 온톨로지 구축 프로세스 | `docs-표준-typedb-v1/README.md` |
| V3.2 온톨로지 스키마 | `docs-표준-typedb/schema_yaml_v3/` (7개 YAML) |
| Phase 0 코드 (도면 분석) | `_Python_code/phase0/` |
| Phase 0 에이전틱 파이프라인 | `_Python_code/phase0/agentic_pipeline.py` |
| 에이전틱 작업 지시서 | `_Python_code/WORK_ORDER-에이전틱-Phase0.md` |
| AI 프롬프트 수정 | `_Python_code/prompts/` |
| 실제 프로젝트 데이터 | `_Python_code/projects/청주사업장신축/` |
| 시나리오 작성/편집 | `docs-시나리오/README.md` |
| 비즈니스 모델 | `docs-마일스톤메모들/DKS-비즈니스모델-상세설계.md` |
| 에이전틱 아키텍처 설계 | `docs-마일스톤메모들/에이전틱-아키텍처-설계-메모.md` |
| AI API 가격/조사 | `AI-API-가격비교-2026-03.md`, `AI-에이전트-API-조사-2026-04.md`, `수집자료/Autodesk_Cloud/autodesk_cloud_research.md` |

### 하위 README 인덱스

| 위치 | 내용 |
|------|------|
| `_Python_code/README.md` | 파이프라인 코드 (phase0/phase1/_archive) |
| `docs-표준-typedb/README.md` | V3.2 스키마, YAML=SSoT 원칙 |
| `docs-표준-typedb-v1/README.md` | 9단계 프로세스 + Phase 1 세션 핸드오버 |
| `docs-표준-typedb-v1/실행결과/README.md` | **Phase 1 실행 누적 인덱스** |
| `docs-시나리오/README.md` | 시나리오 작성 가이드, 페르소나 |
| `수집자료/README.md` | **기술조사 및 대외 수집자료 인덱스** |

---

## 풀려는 문제

```
[현재]                              [목표]
도면 (DWG/PDF)                     "항온항습기 냉수공급은 누가 해줘?"
  → AutoCAD 열기                    → "CH-01 냉동기 → P-101 펌프 → 항온항습기"
  → 한 장씩 찾기                    → 즉시 응답
  → 김 과장한테 물어보기
```

---

## 현재 상태 (2026-04-16)

| 구분 | 상태 | 비고 |
|------|:----:|------|
| **Phase 0 원샷 파이프라인** | ✅ 완료 | PDF 파싱 + 3-Phase AI + 4모델 교차 검수 |
| **Phase 0 v2.0 파이프라인** | 🔄 진행중 | 18→13 Step, supplement 주입, 병렬화 구현 완료 |
| **Phase 0 v2.0 전기 실행** | ✅ 완료 | 06_전기(청주) qualified 38.5%, 0-8A/B 신규 구현 |
| **Phase 0 v2.0 기계 실행** | ⏳ 다음 | 기계 테스트 착수 예정 |
| **discipline supplement 체계** | 🔄 진행중 | P-4.5 주입 구현 완료 / 전기(7 genre) 완비, 타분야 확장 중 |
| **V3.2 온톨로지 스키마** | ✅ 확정 | 엔티티 31, 관계 10, 속성 27, 공리 22+가드레일 14 |
| **Phase 1 9단계 프로세스 설계** | ✅ 완료 | D1~D48 전체 설계 확정 |
| **Phase 1 건축 1~6단계 실행** | ✅ 완료 | 38클래스, 58인스턴스, HermiT PASS |
| **Phase 1 누적 시스템** | ✅ 구축 | 분야별 실행 → _누적/ 자동 갱신 구조 |
| **에이전틱 아키텍처 설계** | ✅ 완료 | 3사 API 조사, Native Tool Use, 도구 7+5개 |
| **시나리오 6건** | ✅ 대부분 | S2~S6 완료, S1(운영자) 미작성 |
| **비즈니스 플랜** | ✅ 제출 | 3단계 과금, 경영 보고 PDF 제출 완료 |
| **DB 전략 재평가** | ✅ 완료 | TypeDB 유지 + RAG 이원 구조 |

---

## 핵심 파이프라인

### Phase 0: 도면 → 초벌 분석 (완료)

```
PDF 도면 → parse_pdf.py → 텍스트 + 400DPI PNG
  → 에이전틱 파이프라인 (7개 도구, GPT-mini + Gemini Flash)
  → entity_list + legend + entity_details + page_context
  → review_pipeline (대형 4모델 교차 검수)
```

### Phase 1: 초벌 분석 → 온톨로지 (진행중)

```
Phase 0 산출물
  → [1단계] 도메인 정의      (Sonnet)
  → [2단계] 개념 수집        (Sonnet)
  → [3A/3B] 개념+관계 정의   (Sonnet)
  → [4단계] 계층 구조 개발    (4-Tier: 소형→중형→Sonnet→Opus)
  → [5~9단계] OWL→검증→배포  (미착수)
```

> 상세: `docs-표준-typedb-v1/실행결과/_누적/마스터-블루프린트.md`

### AI 모델 역할 분담

```
[소형] GPT-5.4-mini + Gemini Flash  → Phase 0 초벌, Phase 1 4-A 초안
[중형] GPT-5.4 + Gemini Pro         → Phase 1 4-B 검증
[대형] Sonnet 4.6                    → Phase 1 1~3단계, 4-C 교차비교
[최대] Opus 4.6                      → Phase 1 4-D 최종 판단
```

---

## 전략적 접근

```
Phase A: 문서 RAG → 자연어 검색
Phase B: 도면 파이프라인 → 설비/관계 추출 ← 현재 여기
Phase C: 그래프 DB + 영향도 분석
```

---

## 폴더 구조 요약

| 폴더 | 역할 | README |
|------|------|:------:|
| `_Python_code/` | AI 파이프라인 코드 (phase0/phase1/_archive) | ✅ |
| `_Python_code/projects/` | 실제 프로젝트 데이터 (청주사업장신축 등) | ✅ |
| `_Python_code/prompts/` | Phase 0 에이전틱 프롬프트 YAML (13개+) | ✅ |
| `docs-표준-typedb/` | V3.2 온톨로지 표준 + TypeDB 조사 | ✅ |
| `docs-표준-typedb-v1/` | 9단계 온톨로지 구축 프로세스 | ✅ |
| `docs-표준-typedb-v1/실행결과/` | **Phase 1 실행 결과 + 누적 학습** | ✅ |
| `docs-시나리오/` | 시나리오 기반 PRD 준비 | ✅ |
| `docs-마일스톤메모들/` | 비즈니스 모델 + 경영 보고 + 에이전틱 설계 | — |
| `docs-대화기록/` | AI 세션 로그 + 초기화 프롬프트 | — |
| `docs-표준제안서/` | 사업 설계 및 고객 제안 문서 (CEO/CTO/영업/고객 관점) | ✅ |
| `이전작성/` | V1~V2 아카이브 (온톨로지-산업화표준 조사, 1차 최소 POC 포함) | — |
| `청주사업장-FMS고도화/` | 첫 고객 적용 사례 참고 문서 | — |

> 상세 폴더/파일 인벤토리: `README_v20260406.md` §폴더/파일 전수 인벤토리

---

## 다음 단계

```
[완료] Phase 0 v2.0 파이프라인 구현 (병렬화, supplement 주입, 0-8A/B)
[완료] Phase 0 전기(06_전기 청주) 전체 실행 (qualified 38.5%)
[다음] Phase 0 기계 테스트 실행
  → discipline/mechanical supplement 검증
  → 전기 대비 qualified 비율 비교
  → 나머지 분야 순차 실행 (건축/통신/소방/구조...)
[병행] Phase 1 분야별 실행 → 누적 블루프린트 갱신
  → 01-운영자-시나리오 작성
    → PRD 전환 → 기술 스택 확정 → 개발 로드맵 → 구현
    → 도면정보관리 서비스 프론트엔드 개발
    → RAGflow 연동 (비정형 지식 파이프라인)
```

---

## 미결정 사항

- 서비스 방식 (B2B API vs B2B SaaS) 미결정
- 첫 번째 고객 도메인 (데이터센터/빌딩/공장) 미결정
- DWG 변환 방식 (ODA / LibreDWG) 미결정
- Graph DB 최종 선택 (TypeDB 유지, AGE 대안) → PoC 후 확정

---

## 이전 README

| 파일 | 시점 | 비고 |
|------|------|------|
| `README_v20260406.md` | 2026-04-06 | 전수 폴더/파일 인벤토리 포함 |
