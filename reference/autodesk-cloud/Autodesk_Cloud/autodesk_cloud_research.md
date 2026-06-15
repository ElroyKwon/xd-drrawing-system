---
tags:
  - 데이터지식스튜디오
  - 도면지식화
  - 클라우드
  - Autodesk
  - API
  - 기술조사
aliases:
  - Autodesk 클라우드 서비스 상세 조사
  - APS 딥 리서치 보고서
created: 2026-06-11
updated: 2026-06-11
related:
  - "[[00-비전과-전략적-선택]]"
  - "[[RFP-데이터지식스튜디오]]"
---

# Autodesk 클라우드 서비스 및 API 상세 조사 보고서

## 1. Autodesk 클라우드 플랫폼 개요
* **Autodesk Platform Services (APS, 구 Autodesk Forge)**: 오토데스크의 설계 데이터와 엔진을 클라우드 API 형태로 제공하는 개발자 플랫폼입니다.
* **Autodesk Construction Cloud (ACC) 및 BIM 360**: APS를 기반으로 구축된 기성 SaaS 제품군으로, 건설/설계 라이프사이클 전반의 도면 관리(Docs), 협업(Collaborate), 현장 관리(Build) 기능을 제공합니다.
* **인증 아키텍처 (OAuth 2.0)**:
    * **2-Legged OAuth**: 사용자 개입이 없는 머신간(M2M) 인증 방식입니다. [[데이터지식스튜디오]]의 백엔드 파이프라인에서 도면을 자동 수집하고 처리할 때 주로 사용됩니다. (Scope 예: `data:read`, `data:write`, `bucket:create`).
    * **3-Legged OAuth**: 사용자가 직접 자신의 Autodesk 계정으로 로그인하여 토큰을 얻는 방식입니다. 웹 클라이언트에서 보안이 적용된 도면을 직접 뷰어로 조회할 때 사용됩니다.

---

## 2. 핵심 제공 서비스 및 상세 API 기술 사양

### ① Data Management API (도면 자원 관리)
* **OSS (Object Storage Service)**: 오토데스크가 운영하는 클라우드 스토리지 버킷 시스템입니다.
    * **버킷 관리 (`/oss/v2/buckets`)**: 도면 파일을 격리 보관하기 위해 고유한 버킷(Bucket Key)을 생성하고 보관 정책(Transient, Temporary, Persistent)을 지정합니다.
    * **Direct-to-S3 아키텍처**: 대용량 [[DWG]]/[[PDF]] 업로드 시, 클라이언트가 AWS S3의 Signed URL을 발급받아 스토리지 서버를 거치지 않고 S3로 직접 업로드하는 방식을 취하여 병렬 업로드 및 안정성을 극대화합니다.
* **Hubs, Projects, Folders API**: BIM 360 Docs나 ACC 환경과 연결될 때, 클라이언트의 조직(Hubs) 구조와 프로젝트(Projects) 하위 폴더 트리를 그대로 조회하고 신규 도면 파일을 업로드 및 동기화할 수 있도록 지원합니다.

### ② Model Derivative API (도면 메타데이터 및 지식 추출)
* **SVF/SVF2 포맷 변환**: 2D [[DWG]] 도면 또는 3D Revit 모델을 웹에서 고성능으로 표현할 수 있는 경량 벡터 포맷인 SVF/SVF2(Streaming Vector Format)로 자동 변환합니다.
* **메타데이터 추출 엔드포인트**:
    * **도면 뷰 목록 조회**: `GET /designdata/{urn}/metadata` 호출을 통해 도면 내 시각화 뷰 목록(Guid)을 추출합니다.
    * **전체 객체 트리 덤프**: `GET /designdata/{urn}/metadata/{guid}`를 사용하여 도면의 레이아웃, 블록, 부품 계층 구조를 트리 구조로 획득합니다.
    * **개별 객체 속성 조회**: `GET /designdata/{urn}/metadata/{guid}/properties`를 호출하여 도면 내 모든 개체의 텍스트, 치수, 부품 번호 등의 속성 맵을 반환받습니다.
    * **대용량 SQLite 데이터베이스 Asset 다운로드**: Properties API 응답 크기가 20MB를 초과하여 API 호출 부하가 커질 경우, 번들 내부의 `Autodesk.CloudPlatform.PropertyDatabase` 파일(SQLite 포맷)을 직접 다운로드하여 로컬 백엔드에서 고속으로 쿼리 및 파싱할 수 있습니다. DKS [[온톨로지]] 파이프라인 구축 시 대용량 도면 처리에 매우 권장되는 아키텍처입니다.

### ③ Design Automation API (클라우드 기반 헤드리스 CAD 가공)
* **구동 방식**: 클라우드 가상 머신에 AutoCAD, Revit, Inventor 등의 코어 엔진을 실행하여 UI 상호작용 없이 개발자가 작성한 스크립트를 적용해 결과물을 산출합니다.
* **아키텍처 구성 요소**:
    * **AppBundles**: 오토데스크 엔진 위에서 동작할 사용자 정의 패키지(예: AutoLISP 스크립트, .NET/ObjectARX DLL 등)를 압축한 zip 파일입니다.
    * **Activities**: 실행할 AppBundle과 적용할 타겟 엔진 버전, 그리고 입력/출력 매개변수 양식을 선언적으로 정의한 명세서입니다.
    * **WorkItems**: 특정 도면 파일의 다운로드 URL과 입력 인자를 정의하여 실제로 Design Automation을 실행시키는 작업 요청 건입니다.
* **DKS 활용 시나리오**: 도면 내부의 심볼 간 기하학적 연결 정보(예: 라인 끝점과 블록 인서트 포인트의 접점 분석)를 LISP 스크립트로 오프라인 일괄 분석하여 관계성 데이터를 JSON으로 가공한 후 [[TypeDB]]에 입력합니다.

### ④ Viewer SDK (지식 연계 시각화 프론트엔드)
* **웹 렌더링 엔진**: Three.js를 기반으로 확장된 3D/2D 웹 그래픽 엔진으로, 클라이언트 브라우저에서 대용량 CAD 벡터 데이터를 빠른 화면 이동 및 줌인/아웃으로 가시화합니다.
* **주요 JavaScript API**:
    * `viewer.loadDocumentNode()`: 변환된 URN을 통해 도면 렌더링.
    * `viewer.getProperties(dbId, callback)`: 사용자가 뷰어 상의 특정 객체를 클릭했을 때 해당 객체의 속성 데이터를 획득.
    * `viewer.select(dbIdArray)`: 특정 부품/객체 목록을 그래픽적으로 하이라이트(파란색 등으로 반짝임 효과) 표시.
    * `viewer.fitToView(dbIdArray)`: 특정 장비의 위치로 줌 앤 포커싱 적용.
* **확장성(Extensions)**: 커스텀 툴바 버튼 생성, 마우스 오버 시 온톨로지 지식 그래프 툴팁 노출 등의 부가 기능 확장을 지원합니다.

### ⑤ Webhooks API (실시간 변경 이벤트 핸들링)
* **역할**: 오토데스크 클라우드 스토리지 상의 도면 업로드 완료, Model Derivative 파일 변환 완료, 워크플로 변경 등 주요 라이프사이클 이벤트 발생 시 등록된 백엔드 엔드포인트로 실시간 JSON 알림을 전달합니다.

---

## 3. 데이터 지식 스튜디오 (DKS) 통합 시나리오 및 설계안

```
[도면 업로드] ──> Data Management API (OSS 버킷)
                      │
                      ▼
               Model Derivative API (SVF2 변환 및 SQLite DB 추출)
                      │
                      ├─────────────────────────────────┐
                      ▼                                 ▼
           [지식 변환 파이프라인]                 [시각화 서비스]
           SQLite 속성 / LISP 데이터                    │
                      │                                 │
                      ▼                                 ▼
               TypeDB 온톨로지 적재                 APS Viewer SDK
                      │                                 │
                      ▼                                 │
                [AI RAG 엔진] ──────────────────────────┘
             (자연어 질의 추론 및 DbId 전송)
```

### ① 도면 식별자 및 온톨로지 엔티티 매핑
* **DbId (Document Database ID)**: Model Derivative로 변환된 도면 내 객체에 매핑되는 정수형 일회성 식별자입니다. 도면이 재변환될 때 변경될 가능성이 있습니다.
* **ExternalId (설계 고유 ID)**: AutoCAD 내부에서 부여하는 고유 객체 핸들값(Handle) 혹은 GUID입니다. 도면 버전이 올라가도 변하지 않는 불변의 식별자입니다.
* **매핑 가이드**: DKS [[온톨로지]] (TypeDB)에 엔티티를 적재할 때, **ExternalId**를 고유 키로 활용하여 관계망을 정의하고, 사용자 브라우저 상의 뷰어 제어 시에는 런타임에 ExternalId를 **DbId**로 맵 변환하여 하이라이트를 트리거하는 방식을 제안합니다.

### ② 지식 융합형 AI 대화 인터페이스 구현
1. 사용자가 웹 UI에서 질문: *"[[발전기]] GEN-01 차단기의 1차측에 연결된 [[배전반]]은 무엇인가?"*
2. DKS AI RAG 엔진이 작동하여 [[TypeDB]] 온톨로지의 추론 규칙을 실행: `GEN-01` -> `차단기` -> `1차측 케이블` -> 연결된 `배전반` 인스턴스 정보 추론.
3. 추론 결과: *"SWBD-01 배전반입니다."* 텍스트 응답 생성.
4. 동시에 AI 엔진이 `SWBD-01` 배전반 엔티티의 `ExternalId` 정보를 API 응답에 동봉하여 프론트엔드로 전달.
5. 웹 브라우저의 APS Viewer SDK가 `ExternalId`를 수신 후 `viewer.select(dbId)` 및 `viewer.fitToView(dbId)`를 트리거하여 화면에 해당 배전반 도면 영역을 강제 하이라이트하고 즉시 포커스 이동.

---

## 4. 결론 및 향후 검토 방향
* **M2M 백엔드 인증 및 파이프라인 구축**: 2-Legged 토큰 획득 및 Direct-to-S3 업로드 모듈의 파이썬 PoC 코드를 작성해야 합니다.
* **SQLite 기반 메타데이터 파서 테스트**: 대용량 도면에서 `Autodesk.CloudPlatform.PropertyDatabase`를 파싱하여 DKS 엔티티로 매핑하는 변환 속도와 데이터 무손실 수준을 벤치마킹하는 실험이 필요합니다.
