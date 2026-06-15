---
tags:
  - concept-map
  - ontology
  - dks
  - typedb
  - llm-wiki
created: 2026-05-03
aliases:
  - 데이터 지식 스튜디오 개념 역인덱스
  - DKS 개념 역인덱스
---

# _CONCEPT-MAP — 데이터 지식 스튜디오 (DKS)

> 도면(DWG/PDF) + 문서 → 온톨로지(TypeDB) + RAG(RAGflow) → 도면정보관리 서비스.
> 솔루션 개요: 상위 `_CONCEPT-MAP.md` §3
> 비즈니스 검토: `온톨로지-서비스-기획/_NEXT-SESSION.md`

---

## 1. Phase 0 — 도면 분析 파이프라인

| 개념·키워드 | 파일 경로 |
|-----------|---------|
| Phase 0 에이전틱 파이프라인 (현행 v1.31) | `_Python_code/phase0_v2_0/` |
| 에이전틱 작업 지시서 | `_Python_code/WORK_ORDER-에이전틱-Phase0.md` |
| 표준 프롬프트 (P-00 ~ P-13) | `_Python_code/prompts/phase0_v2_0/` |
| 분야별 supplement | `_Python_code/prompts/phase0_v2_0/discipline/{분야}/` |
| 분야 이슈 로그 (분析 전 필독) | `_Python_code/prompts/phase0_v2_0/discipline/{분야}/README.md §5` |
| 분야 횡단 이슈 승격 테이블 | `_Python_code/prompts/phase0_v2_0/discipline/README.md §11.A` |
| 표준 프롬프트·코드 회귀 로그 | `_Python_code/prompts/phase0_v2_0/discipline/README.md §11.B` |
| **★★★ Phase 0 업그레이드 V4 계획 (Atomic Decomposition, supplement-only)** | `_Python_code/phase0_v2_0/00-Step0-9d-Promotion-평탄화-분석.md` (2026-05-06 세션 8) |
| 세션 종료 기록 (최신) | `_Python_code/SESSION-CLOSE-20260502c.md` |

---

## 2. Phase 1 — 온톨로지 구축 파이프라인

| 개념·키워드 | 파일 경로 |
|-----------|---------|
| **★ Phase 1 정본 진입점 (신규 README)** | `docs-표준-typedb-v1/README.md` (2026-05-05 갱신) |
| **★★★ 다음 세션 진입점 (Stage 8 결정 진행, G1~G4-α 10/15 완료, 미결 5건)** | `docs-표준-typedb-v1/_NEXT-SESSION-stage7-passed-next-stage8-9.md` (2026-05-06 3차 갱신) |
| Stage 7-C 토론 진입점 (Stage 8 채택으로 무효화, 본문 보존) | `docs-표준-typedb-v1/_NEXT-SESSION-stage7c-restart.md` (2026-05-06) |
| **★ Stage 8 재정의 박제 (D-P1-25, OWL 쿼리·테스트, 옛 7-C 흡수, 도면 ground-truth 대조)** | `docs-표준-typedb-v1/D-P1-25-stage8-redesigned.md` (2026-05-06 G1~G4-α 결정 반영) |
| **★ Stage 9 TypeDB 배포 박제 (D-P1-26, 모델 D 채택, TypeDB CRUD 영구 거부)** | `docs-표준-typedb-v1/D-P1-26-stage9-typedb-deployment.md` (2026-05-06) |
| **★ Backend 이주 인벤토리 Pass 1** | `_Python_code/_INVENTORY-Pass1.md` (2026-05-06) |
| 옛 v0 개념 정립 문서 (16건, history) | `docs-표준-typedb-v1/_concept_v0/` (옛 README는 `_README_v0_old.md`로 보존) |
| **★ 청주 Phase 1 산출물 매니페스트** | `_Python_code/projects/청주사업장신축/phase1/run_FINAL/_MANIFEST.md` |
| 단계별 설계 문서 (D1~D48, 옛 v0) | `docs-표준-typedb-v1/_concept_v0/0N-*.md` |
| **코딩 블루프린트 (★)** | `docs-표준-typedb-v1/실행결과/_누적/마스터-블루프린트.md` |
| Phase 1 실행 코드 | `_Python_code/phase1/` |
| Phase 1 코드 가이드 (★) | `_Python_code/phase1/README.md` |
| Phase 1 프롬프트 | `_Python_code/prompts/phase1/` |
| 모듈러 OWL 설계 (D-P1-10) | `docs-표준-typedb-v1/D-P1-10-modular-owl.md` |
| **★★★ Phase 1 헌법 (D-P1-INVARIANT)** | `docs-표준-typedb-v1/D-P1-INVARIANT-lossless-novelty.md` |
| **★★ Stage 4 모듈러 설계 (D-P1-18)** | `docs-표준-typedb-v1/D-P1-18-stage4-modular-design.md` |
| **★★ Stage 5 모듈러 설계 (D-P1-19)** | `docs-표준-typedb-v1/D-P1-19-stage5-modular-design.md` |
| **★ D-P1-16-A Stage 4 unresolved 규약** | `docs-표준-typedb-v1/D-P1-16-A-stage4-unresolved-protocol.md` |
| **★ Decision Impact Catalog (L2 살아있는)** | `_Python_code/phase1/data/decision_impact_catalog.yaml` |
| **★ Module Inverse Alias Map (Stage 5+ L2)** | `_Python_code/phase1/data/module_inverse_alias_map.yaml` |
| OWL 에러 핸들링 (★) | `docs-표준-typedb-v1/기술검토-OWL생성-에러핸들링.md` |
| 7단계 추론 검증 설계 | `docs-표준-typedb-v1/08-7단계-검증.md` |
| Phase 1 3축 풀스택 분析 박제 | `docs-표준-typedb-v1/00-Phase1-3축풀스택-분析.md` |
| **★ 풀스택 실행 계획 (A~E)** | `docs-표준-typedb-v1/00-Phase1-풀스택-실행계획.md` |
| **★ Phase 1 회귀 로그 (X-P1-NNN)** | `docs-표준-typedb-v1/X-P1-001.md`, `X-P1-002.md`, **`X-P1-003.md`** (Stage 5 stub+alias 흡수 38→6), **`X-P1-004.md`** (OWL 2 DL 자동 약화 proactive+reactive), **`X-P1-005.md`** (Stage 3B disagreement 보존), **`X-P1-006.md`** (Cross-module non-simple closure 자동 약화, 2026-05-04) |
| **★★ Stage 7-A 무손실 매트릭스 설계 (D-P1-22)** | `docs-표준-typedb-v1/D-P1-22-stage7-loss-matrix-design.md` |
| **★ Cross-module DL 가드 (rdflib 기반)** | `_Python_code/phase1/owl_dl_guard.py` (X-P1-006 본체) |
| **★★★ 솔루션 운영 가이드 (D-P1-OPERATIONS-PLAYBOOK)** | `docs-표준-typedb-v1/D-P1-OPERATIONS-PLAYBOOK.md` — 5계층 방어 / SaaS 인프라 / 다른 도면 재발 차단 |
| D-P1-16 Stage 5/6 unresolved 처리 방침 | `docs-표준-typedb-v1/D-P1-16-unresolved-stage5_6-deferred.md` |
| 04 원본 4-Tier 설계 (참고) | `docs-표준-typedb-v1/05-4단계-계층구조개발.md` |
| regression 테스트 (66 PASS) | `_Python_code/tests/phase1/regression/` |
| fingerprint 모듈 (결함/도면 지문) | `_Python_code/phase1/fingerprint/` |
| supplement 효과 측정 | `_Python_code/phase1/supplement/effect_measurer.py` |
| **★★ Stage 4 hierarchy 코드** | `_Python_code/phase1/stage4_hierarchy.py` |
| **★★ Stage 4-E OWL builder** | `_Python_code/phase1/stage4e_owl_builder.py` |
| **★★ hierarchy_skeleton (Stage 4용)** | `_Python_code/phase1/skeleton/hierarchy_skeleton.py` |
| **★★ Stage 5 properties 코드** | `_Python_code/phase1/stage5_properties.py` |
| **★★ Stage 5-E OWL builder (stub 자동 흡수)** | `_Python_code/phase1/stage5e_owl_builder.py` |
| **★★ Stage 5 blueprint (정밀 분석)** | `_Python_code/phase1/stage5_blueprint.py` |
| **★★ stage5_property_skeleton (Stage 5용)** | `_Python_code/phase1/skeleton/stage5_property_skeleton.py` |
| **★ Stage 5 프롬프트 (D-P1-19 v1.0)** | `_Python_code/prompts/phase1/stage_5_properties.yaml` |
| **★ Stage 4 invariant 3종 + Stage 5 invariant 6종 (S5-1~S5-6)** | `_Python_code/phase1/validator/invariant_checker.py` |
| Stage 4 DPP 패턴 (D-P1-S4-001~005) | `_Python_code/prompts/phase1/dpp/known_defects_v1.yaml` |
| **★★★ Phase 1 end-to-end 실행 가이드** | `_Python_code/PHASE1-END-TO-END.md` |
| **★★ dks_viewer Phase A v2 완료 (4-탭 SPA: Schema·Explorer·Disciplines·HITL)** | `_Python_code/dks_viewer/outputs/chungju/viewer.html` (1.55 MB, 1958 노드/1696 엣지/255 HITL) — Cytoscape.js + fcose/dagre + localStorage 메모 (2026-05-06) |
| **★ 최신 세션 종료 기록** | `_Python_code/SESSION-CLOSE-20260506c.md` (dks_viewer Phase A v1 헤어볼 → v2 4-탭 재설계 완료, 사용자 검토 중) / `SESSION-CLOSE-20260506b.md` (WORK_ORDER 발주) / `SESSION-CLOSE-20260506.md` (Stage 7-C 보류) |
| 직전 세션 종료 기록 | `_Python_code/SESSION-CLOSE-20260505.md` (Stage 7-A/B PASS, X-P1-007/008, v10.6 HermiT consistent) / `SESSION-CLOSE-20260504.md` (X-P1-006 + 정리) |
| 이전 세션 종료 기록 | `_Python_code/SESSION-CLOSE-20260503h.md` (Stage 6 코드 4개 + 스모크 3회 + 풀 결정 보류) / `_g.md` (Stage 5 풀 방어) / `_e.md` (Stage 5 부분완료) / `_d.md` (Stage 4) |
| **★★ Stage 6 신규 코드 (D-P1-INVARIANT + D-P1-19 모듈러×chunk 패턴)** | `_Python_code/phase1/stage6_instances.py` + `stage6e_owl_builder.py` + `skeleton/stage6_instance_skeleton.py` |
| **★★ Stage 6 신 프롬프트** | `_Python_code/prompts/phase1/stage_6_instances.yaml` (옛 6-A~F는 `.legacy_v1_20260503g` 백업) |
| **★ Stage 7 generic 골격 + 추론 검증 설계 메모** | `_Python_code/phase1/stage7_validation.py` + `docs-표준-typedb-v1/D-P1-21-stage7-validation-design-memo.md` |
| **★ 청주 스모크 3종 (Sonnet 골든 + mini A2 + mini B 손실 사례)** | `projects/청주사업장신축/phase1/run_20260503/stage6_modular_smoke_{A,A_mini2,B_mini}/` |
| 발견된 버그 (다음 세션 1순위) | invariant validate_chunk_output (chunk_skeleton 미수신) + mini self-truncation + namespace 혼동 |
| 청주 풀스택 산출물 (run_20260503) | `_Python_code/projects/청주사업장신축/phase1/run_20260503/` |
| **★ 청주 Stage 4 산출물 (10모듈)** | `projects/청주사업장신축/phase1/run_20260503/stage4_modular_F_FULL/` |
| **★ 청주 Stage 4-E OWL (HermiT 통과)** | `projects/청주사업장신축/phase1/run_20260503/stage4e_owl_v2_hermit/` |
| **★ 청주 Stage 5 산출물 (10모듈)** | `projects/청주사업장신축/phase1/run_20260503/stage5_modular_F_FULL/` |
| **★ 청주 Stage 5-E OWL v1 (HermiT False)** | `projects/청주사업장신축/phase1/run_20260503/stage5e_owl/` |
| **★★ 청주 Stage 5-E OWL v3.3 (golden, downgrade 4 + disagreement 6)** | `projects/청주사업장신축/phase1/run_20260503/stage5e_owl_v3_3/` |
| **★ Stage 5 blueprint (v1·v2·v3·v3.5 — 38→6 골든)** | `projects/청주사업장신축/phase1/run_20260503/stage5_blueprint*.md` |
| module_assigner 헬퍼 | `_Python_code/phase1/module_assigner.py` |

---

## 3. V3.2 온톨로지 스키마 (참고용)

| 개념·키워드 | 파일 경로 |
|-----------|---------|
| **V3.2 스키마 진입점** | `docs-표준-typedb/README.md` |
| 스키마 YAML (7개) | `docs-표준-typedb/schema_yaml_v3/` |
| YAML→TQL 변환 규칙 | `docs-표준-typedb/YAML-TQL-변환-표준.md` |
| V1 표준 (Phase 1 이전 참고) | `docs-표준-typedb-v1/README.md` |

---

## 4. 시나리오 / PRD

| 시나리오 | 상태 | 파일 |
|---------|:----:|------|
| S1 운영자 (장애 대응) | ❌ 미작성 | — |
| S2 지식 엔지니어 | ✅ 15개 | `docs-시나리오/` |
| S3 유지보수/KaaS | ✅ S3-01~04 | `docs-시나리오/` |
| S4~S6 온톨로지·TypeDB·RAG | ✅ | `docs-시나리오/` |
| 시나리오 진입점 | — | `docs-시나리오/README.md` |

---

## 5. 비즈니스 모델 / 마일스톤

| 개념·키워드 | 파일 경로 |
|-----------|---------|
| 비즈니스 모델 상세 (제출 완료) | `docs-마일스톤메모들/DKS-비즈니스모델-상세설계.md` |
| 에이전틱 아키텍처 설계 메모 | `docs-마일스톤메모들/에이전틱-아키텍처-설계-메모.md` |
| AI API 가격 비교 (모델 매핑 ★) | `AI-API-가격비교-2026-03.md §0` |
| 달성 상태 아카이브 | `CLAUDE-달성상태-아카이브.md` |
| 참조 인덱스 | `CLAUDE-참조-인덱스.md` |
| **사용자용 정리 노트 (Phase 0/1 간단 요약)** | `_나를위한정리/README.md` |
| **★ DKS 진행현황 보고서 (2026-05-06)** | `_나를위한정리/_보고서_2026-05-06/README.md` (7 파일: 진행현황·Phase0/1 결과·로드맵·인벤토리·결정사항) |

---

## 6. 역방향 도면 생성 (장기 비전)

| 개념 | 상태 | 참고 |
|------|:----:|------|
| 도면 → Canvas 대화형 편집 | 📋 Stage 1 PoC 미착수 | `CLAUDE.md` §장기 비전 |
| DWG/DXF 출력 (CAD 정확도) | 📋 Stage 3 (6개월+) | — |

---

## 7. 현황 (2026-05-03 기준)

| 항목 | 상태 |
|------|:----:|
| Phase 0 에이전틱 파이프라인 v1.31 | ✅ |
| Phase 1 9단계 설계 (D1~D48) | ✅ |
| **Phase 1 청주 풀스택 A~E 완료** | ✅ 결함 16→0, regression 27 PASS |
| **★ Phase 1 헌법 (D-P1-INVARIANT)** | ✅ 4대 원칙 + 4대 흐름 + Stage 0.5~7 매트릭스 |
| **★ D-P1-16-A 카탈로그 분기 규약 + L2 카탈로그** | ✅ 일반화판 (novel fallback 포함) |
| **★ Stage 4 모듈러 풀스택 (D-P1-18) 코드 + 실행** | ✅ 10모듈 완주 ($4.45/35.7분) |
| **★ Stage 4-E OWL 통합 (HermiT consistent)** | ✅ 376 cls + 58 disjoint, 모듈러 OWL 10개 |
| **★ X-P1-002 코드 회귀 박제** | ✅ AI 행동 OK, invariant_checker 보강 |
| **★ Stage 5 모듈러 풀스택 (D-P1-19) 코드 + 실행** | ✅ 10모듈 완주 ($6.22/45분, DP 229·OP 77·Rest 99) |
| **★ Stage 5-E OWL 빌드 + stub 자동 흡수** | ✅ 10/10 OWL (DP 231·OP 102·Rest 83), stub 27건 흡수 |
| **★ X-P1-003 코드 회귀 박제 (정정본)** | ✅ stub+alias 합집합 38→6건 (-84%), 회귀 12 PASS |
| **★ X-P1-004 OWL 2 DL 자동 약화 (proactive+reactive)** | ✅ 청주 4건 약화 (proactive 2 + reactive 2), 회귀 11 PASS |
| **★ X-P1-005 Stage 3B disagreement 보존** | ✅ fp_elec 6건 보존 + OWL은 Stage 3B, 회귀 7 PASS |
| **★★★ D-P1-OPERATIONS-PLAYBOOK (솔루션 운영)** | ✅ 5계층 방어 / SaaS 인프라 / 다른 도면 재발 차단 가이드 |
| **★ module_inverse_alias_map 카탈로그 (헌법 4)** | ✅ partOf/memberOf/containedIn 3종 |
| **★★ Phase 1 end-to-end 가이드** | ✅ PHASE1-END-TO-END.md |
| **★★ Phase 1 회귀 인프라** | ✅ 96 PASS (이전 66 + X-P1-003/004/005 신규 30) |
| **⚠ Stage 5-E HermiT consistent** | ⚠ 부분 — proactive+reactive 90%+ 자동 차단, 1건(struct:isContainedIn) owlready2 inverse 자동 추론 한계 |
| Stage 3A 실행 (청주 15장 샘플) | ✅ (supplement 미적용 — 400장 재실행 시 필수) |
| Stage 3B 실행 (청주 5차) | ✅ ($2.28, 13.4분, 10/10 PASS) |
| Stage 4 실행 (청주 1차 풀) | ✅ ($4.45, 35.7분, 10/10 PASS, HermiT consistent) |
| Stage 5 실행 (청주 1차 풀) | ✅ ($6.22, 45분, 10/10 self_check pass) |
| Stage 5-E 실행 (청주 v3.3) | ✅ proactive 2 + reactive 2 약화 + disagreement 6 보존 (1건 owlready 한계) |
| Stage 5 풀 방어 (작업 1~4) | ✅ X-P1-003/004/005 + 운영 가이드 박제 |
| Stage 6 신규 코드 4개 작성 | ✅ skeleton + prompt + main + OWL builder |
| Stage 6 스모크 3회 (옵션 A/A2/B) | ✅ Sonnet 무손실 / mini 부분손실 / mini-B 22건 손실 |
| Stage 6 풀 실행 모델 결정 | ⏸ 보류 (Sonnet×40 vs mini×2 재설계 vs per-entity atomic) |
| Stage 6-E OWL Individual 통합 | ⏳ 풀 실행 후 |
| Stage 7 코드 검증 + 추론 검증 (D-P1-21) | ⏳ Stage 6-E 후 |
| **Stage 6~7 실행** | ⏳ 미착수 — **Stage 6 진입 가능** (잔여 1건은 운영 흐름으로 흡수) |
| **다음 세션 진입점** | 📋 `SESSION-CLOSE-20260503g.md` + `_NEXT-SESSION.md` |
| Phase 1 회귀 인프라 (regression 96 PASS) | ✅ X-P1-001~005 |
| V3.2 온톨로지 스키마 | ✅ |
| S1 운영자 시나리오 작성 | ❌ 미작성 |
| Gate-7 재설계 | ⏸ 보류 |
| 도면정보관리 서비스 프론트엔드 | ⏳ 미착수 |
| **★★ dks_viewer (OWL→HTML+AI 채팅 PoC, 도면정보관리 첫 PoC 진입점)** | ✅ Phase A v2 완료 — 4-탭 SPA (Schema 트리뷰 / Explorer N-hop / Disciplines 카드 / HITL Triage). 사용자 검토 중. Phase B(채팅) 대기 |

---

## 9. 자체 웹 CAD 및 도면관리 개발 설계

| 개념·키워드 | 파일 경로 |
| :--- | :--- |
| **★★ 현행 상세설계 마스터 (ACC Build 재현, 13섹션 92문서)** | `수집자료/도면관리시스템_상세설계/00_개요-PMO/README.md` (2026-06-12 신규, DWG 비편집·뷰어+오버레이 전제) |
| **★ ACC(Autodesk Build) 37화면 분석 + 재현 컴포넌트 인벤토리** | `수집자료/screenshot/_ACC-Build-화면분석-재현설계.md` (2026-06-12 신규, 벤치마크 원본) |
| ★ 자체 개발설계 마스터 (초안 — 상세설계셋으로 승계) | `수집자료/Development_Design/design_documents_map.md` (2026-06-11, CAD-editor 가정 → 뷰어+오버레이로 정정) |
| 독자적 웹 CAD 구축 및 뷰어 전략 기획서 | `수집자료/Autodesk_Cloud/dwg_parsing_and_web_cad_strategy.md` (바이너리 OCF/.vs 포맷 비교 및 실용주의 노선 포함) |
| **[설계 01] 요구사항 정의서 (SRS)** | `수집자료/Development_Design/01_Requirements/README.md` (Git-like 버전/마크업 요건 및 하이브리드 검색 요건) |
| [설계 02] 시스템 아키텍처 설계서 (SAD) | `수집자료/Development_Design/02_System_Architecture/README.md` (3-Tier 토폴로지, URL 세션 전이 DFD) |
| [설계 03] 데이터베이스 설계서 (DBD) | `수집자료/Development_Design/03_Database_Design/README.md` (drawings, entity_mappings, markup_commits 스키마) |
| [설계 04] 백엔드 API & 파이프라인 명세 (API) | `수집자료/Development_Design/04_API_Pipeline/README.md` (ACadSharp DWG 파서 워커, JSON 스키마, REST/WS 명세) |
| [설계 05] 웹 CAD 뷰어 상세 설계서 (CCD) | `수집자료/Development_Design/05_Web_CAD_Viewer/README.md` (WebGL RTC 지터 방지, flatbush KD-Tree 스냅 및 측정 삼각측정) |
| [설계 06] AI 에이전트 & 온톨로지 연동 (AID) | `수집자료/Development_Design/06_AI_Ontology/README.md` (Custom Event 기반 프론트엔드 이벤트 버스 및 TQL 템플릿) |
| [설계 07] 배포 및 인프라 설계서 (DEP) | `수집자료/Development_Design/07_Deployment/README.md` (멀티 스테이지 Dockerfile, S3 보안 URL, HermiT consistent CI 가드) |

---

## 10. 동의어 / 관련 키워드

DKS, 데이터 지식 스튜디오, 온톨로지, TypeDB, 도면 AI, Phase 0, Phase 1, OWL, RAGflow, 도면정보관리, 설비 구조, 4계층, 모듈러, DPP, supplement, dks_viewer, OWL 시각화, OWL CRUD, 맥락엔진, 개발설계, 웹CAD, 자체뷰어, 하이브리드검색, Git-like 도면관리, Osnap 스냅, RTC 렌더링

---

*생성: 2026-05-03 | 업데이트: 2026-06-12 | LLM Wiki*

