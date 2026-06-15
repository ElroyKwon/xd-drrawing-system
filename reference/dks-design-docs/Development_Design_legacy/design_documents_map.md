---
tags:
  - 데이터지식스튜디오
  - 도면지식화
  - 개발설계
  - 마스터목차
  - 웹CAD
aliases:
  - 개발 설계 문서 맵
  - 자체 웹 CAD 설계 마스터 플랜
created: 2026-06-11
related:
  - "[[README]]"
  - "[[dwg_parsing_and_web_cad_strategy]]"
  - "[[01_Requirements/README]]"
  - "[[02_System_Architecture/README]]"
  - "[[03_Database_Design/README]]"
  - "[[04_API_Pipeline/README]]"
  - "[[05_Web_CAD_Viewer/README]]"
  - "[[06_AI_Ontology/README]]"
  - "[[07_Deployment/README]]"
---

# 자체 웹 CAD 도면관리 플랫폼 개발 설계 문서 맵 (Master Index)

> **종합 요약**: 본 문서는 Autodesk [[클라우드]] API(APS)에 의존하지 않고, 독자 기술 노선(백엔드 [[DWG]] 파서 + [[WebGL]]/Three.js 프론트엔드 뷰어)을 통해 [[데이터 지식 스튜디오]] (DKS)와 연동되는 **'자체 웹 CAD 도면관리 및 AI 서비스 플랫폼'**을 개발하기 위해 작성되어야 할 전체 기술 설계 문서의 로드맵과 각 문서별 상세 목차 정의서입니다.

---

## 1. 개발 설계 문서 체계도

이후 개발 과정에서 작성 및 갱신해 나갈 설계 문서 목록입니다. 본 맵을 기준으로 하여 각 문서를 단계별로 구체화합니다.

```
[Master] design_documents_map.md (본 문서)
   │
   ├─ [설계 01] [[01_Requirements/README]] (요구사항 정의서)
   ├─ [설계 02] [[02_System_Architecture/README]] (시스템 아키텍처 설계서)
   ├─ [설계 03] [[03_Database_Design/README]] (데이터베이스 설계서 - RDB & Graph DB)
   ├─ [설계 04] [[04_API_Pipeline/README]] (백엔드 파싱 파이프라인 & API 명세서)
   ├─ [설계 05] [[05_Web_CAD_Viewer/README]] (웹 CAD 뷰어 상세 설계서)
   ├─ [설계 06] [[06_AI_Ontology/README]] (AI 에이전트 & 온톨로지 연동 설계서)
   └─ [설계 07] [[07_Deployment/README]] (배포 및 인프라 설계서)
```

---

## 2. 문서별 상세 설계 목차 및 템플릿 정의

---

### [설계 01] 요구사항 정의서 (SRS) — [[01_Requirements/README]]
* **목적**: 시스템이 제공해야 하는 비즈니스 기능적/비기능적 요구사항을 엄격하게 정의합니다.
* **상세 목차**:
    1. **개요 및 비즈니스 목표** (도면 관리의 독립 및 지식 RAG 융합)
    2. **사용자 페르소나 및 유스케이스 정의** (도면 운영자, 지식 엔지니어, 최종 고객 등)
    3. **기능 요구사항 (Functional Requirements)**:
        * 도면 수집 및 업로드/버전 관리
        * 백엔드 도면 속성 및 블록 자동 파싱
        * 웹 브라우저 벡터 뷰잉 및 기본 조작 (줌/팬/레이어)
        * 도면 내 객체 자석 스냅(Osnap) 및 치수/면적 측정
        * AI 대화창 인터페이스 및 도면 연동 제어
    4. **비기능 요구사항 (Non-functional Requirements)**:
        * 성능 (대용량 도면 로딩 및 뷰어 렌더링 프레임 레이트 60fps 보장)
        * 보안 (도면 바이너리 데이터 유출 방지 및 권한 제어)
        * 호환성 (AutoCAD 2013~2018+ DWG/DXF 파일 지원 범위)

---

### [설계 02] 시스템 아키텍처 설계서 (SAD) — [[02_System_Architecture/README]]
* **목적**: 시스템의 전체적인 논리/물리적 구성과 데이터 흐름, 컴포넌트 간의 통신 방식을 설계합니다.
* **상세 목차**:
    1. **아키텍처 설계 원칙** (데이터 주권 확보, MSA 지향, 뷰어 컴포넌트 격리)
    2. **논리 아키텍처 (Logical Architecture)**:
        * 웹 클라이언트 레이어 (React, Three.js)
        * API 게이트웨이 및 인증/인가 서버
        * 도면 변환 마이크로서비스 (DWG Parser Worker)
        * 지식 추론 및 [[AI]] 대화 서버
    3. **데이터 흐름도 (Data Flow Diagram - DFD)**:
        * 도면 업로드 → JSON 기하 구조 변환 → TypeDB 온톨로지 적재 흐름
        * AI 챗봇 질문 → 온톨로지 쿼리 → 뷰어 하이라이트 이벤트 흐름
    4. **물리 아키텍처 (Physical Architecture)**:
        * 웹 서버, 백엔드 컨테이너, 데이터베이스 서버, 파일 스토리지 인프라 구성

---

### [설계 03] 데이터베이스 설계서 (DBD) — [[03_Database_Design/README]]
* **목적**: 서비스 운영을 위한 관계형 DB 구조와 지식 추론을 위한 그래프 DB 온톨로지 모델을 정의합니다.
* **상세 목차**:
    1. **관계형 데이터베이스 (RDB) 설계**:
        * 회원, 권한, 프로젝트, 도면 메타데이터, 버전 이력 테이블 ERD 및 스키마
        * 도면 내 객체 식별자(Handle/ExternalId)와 온톨로지 엔티티 간의 매핑 테이블 설계
    2. **그래프 데이터베이스 (TypeDB) 설계**:
        * 도면 기하 구조 및 장비 계통(P&ID, 단선도) 관계 표현을 위한 V3.2 스키마 구조
        * 계통적 인과관계 추론을 위한 Rule 및 Axioms 명세
    3. **데이터 보존 및 동기화 전략**:
        * 도면 재업로드 시 기존 온톨로지 인스턴스와의 변경사항 병합(Upsert) 규칙

---

### [설계 04] 백엔드 API 및 파이프라인 설계서 (API) — [[04_API_Pipeline/README]]
* **목적**: 도면 파일을 JSON 기하 정보로 파싱하는 배치 엔진 구조와 프론트엔드가 호출할 API 규격을 정의합니다.
* **상세 목차**:
    1. **ACadSharp 기반 변환 파이프라인 엔진 설계**:
        * `DwgReader`를 통한 바이너리 해독 및 객체 순회(Traversal) 흐름
        * `BLOCK` 정의 테이블 및 `INSERT` 참조 좌표 추출기 사양
        * 텍스트(MTEXT/TEXT) 및 선형(LINE/ARC/SPLINE) 엔티티 필터링 필터링 규칙
    2. **변환 산출물 JSON 스키마 규격 정의**:
        * `metadata`: 도면명, 축척, 경계 상자(Bounding Box) 중심점
        * `layers`: 레이어 목록 및 활성 상태
        * `geometry`: 선분, 원호, 텍스트의 로컬 상대 좌표(RTC 적용) 및 Handle ID 배열
    3. **RESTful API Endpoint 명세**:
        * 도면 업로드, 변환 상태 조회, 메타데이터 반환, RAG 검색 API 명세
    4. **WebSocket/Event API 명세**:
        * 도면 변환 실시간 상태 피드, 웹 뷰어 동기화 이벤트 규격

---

### [설계 05] 웹 CAD 뷰어 상세 설계서 (CCD) — [[05_Web_CAD_Viewer/README]]
* **목적**: 웹 브라우저에서 대용량 벡터 도면을 그리는 렌더링 엔진과 측정/스냅 연산 로직을 상세 설계합니다.
* **상세 목차**:
    1. **렌더링 파이프라인 설계**:
        * HTML5 Canvas 2D 컨텍스트 초기화 및 Three.js WebGL WebGL 바인딩
        * 폰트 렌더러 설계 (AutoCAD SHX의 벡터 패스 변환 및 웹 폰트 매핑)
        * 해치(Hatch) 패턴 및 선종류(Linetype)의 실시간 셰이더 패턴 드로잉 설계
    2. **카메라 매트릭스 변환 설계 (Zoom / Pan / Orbit)**:
        * 2D/3D 공간 상의 마우스 좌표와 뷰포트 좌표 간의 행렬 변환 수학적 모델
    3. **자석 스냅 (Osnap) 엔진 설계**:
        * 정점 데이터의 KD-Tree 인덱스 구성 및 Nearest Neighbor 탐색 알고리즘
        * 선분 데이터 교점 및 수선 탐색용 R-Tree 인덱스 구성
    4. **실시간 치수 측정 모듈 설계**:
        * 거리(Distance) 및 면적(Area) 연산 로직 및 치수선 그래픽 렌더링 처리

---

### [설계 06] AI 에이전트 & 온톨로지 연동 설계서 (AID) — [[06_AI_Ontology/README]]
* **목적**: 챗봇 UI와 웹 CAD 뷰어를 결합하는 이벤트 버스 아키텍처와 LLM RAG 파이프라인의 연계 구조를 설계합니다.
* **상세 목차**:
    1. **지식 융합 RAG 파이프라인 아키텍처**:
        * 사용자 질문 → LLM Intent 분석 → TypeDB TQL 쿼리 변환기 구성
        * TypeDB 추론 경로(Multi-hop)의 텍스트 자연어 생성(NLG) 규칙
    2. **챗봇-뷰어 양방향 이벤트 버스(Event Bus) 명세**:
        * 대화 응답 내에 하이라이트할 장비의 `Handle ID`(ExternalId) 전달 포맷
        * 프론트엔드 이벤트 리스너: 장비 ID 수신 시 `viewer.select(Handle)` 및 `viewer.fitToView(Handle)` 트리거 흐름
    3. **LLM 프롬프트 및 인텍스트 예제(Few-shot) 가이드라인**:
        * 도면 분석과 계통 질문 처리를 위한 프롬프트 supplement 규칙 정의

---

### [설계 07] 배포 및 인프라 설계서 (DEP) — [[07_Deployment/README]]
* **목적**: 작성된 모든 애플리케이션의 패키징, CI/CD, 보안 정책 및 클라우드 배포 전략을 정의합니다.
* **상세 목차**:
    1. **도커 라이징(Dockerizing) 전략**:
        * C# .NET 백엔드 파서 및 Python AI 오케스트레이션 컨테이너 빌드 가이드
    2. **인프라 구성도 (AWS / Private Cloud)**:
        * 로드 밸런서, ECS/EKS 클러스터, S3 스토리지, TypeDB 전용 데이터베이스 인스턴스 구성
    3. **CI/CD 파이프라인 설계**:
        * GitHub Actions / GitLab CI를 통한 빌드, 테스트(HermiT consistent 검증), 자동 배포 프로세스
    4. **보안 및 규정 준수**:
        * 데이터 암호화(SSL/TLS, AWS KMS), 도면 원본 파일 노출 방지를 위한 서명된 URL 유효시간 제어
