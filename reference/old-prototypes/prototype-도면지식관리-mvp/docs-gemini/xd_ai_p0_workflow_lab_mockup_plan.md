# XD-AI P0 Workflow Lab Mockup Plan

## 1. 실제 데이터 확인 후 결론

기존 목업의 `PUMP-01 어디야?` 시나리오는 제품 방향을 설명하기에는 쉽지만, 현재 저장된 실제 온톨로지 분석 결과와는 맞지 않는다.

`dwg/온톨로지`의 실제 산출물은 이미 OWL 변환 직전 단계의 구조를 가지고 있다.

- `entity_list_data.yaml`: 분야별 엔티티, 페이지, confidence, 관계 수
- `entity_list_page_*.yaml`: 페이지 단위 엔티티와 관계
- `entity_details/*.yaml`: 엔티티별 스펙, relation, source attribution
- `ontology_placement/*.yaml`: OWL 배치 후보, class hint, assertion, provenance
- `ontology_rules/*.yaml`: object property, class taxonomy, data property, axiom 후보

따라서 P0 목업은 단순 위치 검색이 아니라 **도면 분석 결과를 사람이 검수하고, 근거를 따라가며 OWL 변환 가능 여부를 판단하는 워크플로우**가 되어야 한다.

## 2. 선택한 실제 시나리오

**시나리오:** `SMFD-01` 스마트 방화댐퍼 검수

선택 이유:

- `SMFD-01`은 `entity_list_data.yaml`에서 `fire_damper`로 분류됨
- source page가 `50`, `53` 두 곳으로 나뉘어 있음
- page 50에는 `SMFD-01 -> JB-A-01`, `SMFD-01 -> SMFD-02` 연결 관계가 있음
- page 53에는 `PANEL-ROOF-PLAN contains SMFD-01`, `SMFD-01 references LEGEND-CABLE` 관계가 있음
- `entity_detail_SMFD-01.yaml`에 치수, 위치 메모, 케이블 규격 참조, 구동 방식이 있음
- `placement_SMFD-01.yaml`에 `dks:FireDamper` 확정 후보와 OWL assertion 후보가 있음

## 3. 목업에서 보여줄 실제 질문

```text
SMFD-01을 OWL로 넣어도 되는지 근거를 따라 검수해줘
```

사용자가 기대하는 결과는 단순 답변이 아니다.

1. 어떤 페이지에서 발견되었는지 확인
2. 어떤 엔티티로 분류되었는지 확인
3. 어떤 스펙이 추출되었는지 확인
4. 어떤 관계 assertion이 만들어졌는지 확인
5. 어떤 근거가 시각 의미 분석, cross validation, Gemini/Sonnet/Mini 중 어디서 왔는지 확인
6. `NamedIndividual: dks:SMFD-01`, `Class: dks:FireDamper`로 OWL 변환해도 되는지 승인 또는 보류

## 4. 새 목업 화면 구조

### A. 좌측: 실제 분석 데이터 브라우저

도면 뷰어 흉내보다, 현재 단계에서는 분석 산출물의 근거를 따라가는 화면이 중요하다.

- 분야: 기계
- 대상 파일: `04_[LS ELECTRIC R-Center 구축] 4. 기계`
- 엔티티 후보: `SMFD-01`, `SMFD-02`, `JB-A-01`, `LEGEND-CABLE`, `PANEL-ROOF-PLAN`
- 페이지 근거: page 50, page 53
- 페이지별 관계 그래프

### B. 중앙: 검수 워크플로우

AI가 스스로 답하는 화면이 아니라, 검수자가 따라갈 수 있는 작업 순서를 보여준다.

1. 엔티티 발견 확인
2. 스펙 추출 확인
3. 관계 assertion 확인
4. OWL class placement 확인
5. 승인/보류 판단

### C. 우측: OWL 변환 후보와 리스크

실제 `placement_SMFD-01.yaml`의 정보를 요약한다.

- `owl_role: NamedIndividual`
- `class_hint: FireDamper`
- confirmed class: `dks:FireDamper`
- related assertions:
  - `connects_to SMFD-02`
  - `connects_to JB-A-01`
  - `references LEGEND-CABLE`
  - `PANEL-ROOF-PLAN contains SMFD-01`
- 리스크:
  - `LEGEND-CABLE`과 `LEGEND-WIRE` 병합 가능성
  - `SMFD-GRP-*`와 `SMFD-CTRL-ZONE-*` 계층 불확실
  - `UNKNOWN-DESTINATION-UP`은 아직 목적지가 미확정

## 5. 이 목업이 검증해야 하는 제품 방향

이 화면은 일반 사용자의 검색 SaaS라기보다, 현재 데이터 상태에서는 **AI 도면 분석 결과 검수 SaaS**에 가깝다.

핵심 가치는 다음이다.

- AI가 뽑은 엔티티를 사람이 빠르게 검수한다.
- 출처 페이지와 관계 근거를 한 화면에서 본다.
- OWL 변환 전에 위험한 assertion을 걸러낸다.
- 검수 승인 결과를 다음 ontology build 단계로 넘긴다.

즉, P0의 진짜 이름은 다음에 가깝다.

**Ontology Evidence Review Workflow**

또는 더 제품스럽게는:

**도면 분석 근거 검수 워크플로우**

