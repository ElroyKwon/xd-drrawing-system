---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - 시스템아키텍처
  - 아키텍처
  - Mermaid
  - 하이브리드검색
  - Git_like
aliases:
  - 시스템 아키텍처 설계 명세
  - SAD 상세 지침
created: 2026-06-11
updated: 2026-06-11
related:
  - "[[design_documents_map]]"
  - "[[01_Requirements/README]]"
  - "[[01_Requirements/03_functional_requirements]]"
---

# 02. 시스템 아키텍처 설계서 (SAD)

## 1. 하이브리드 도면 지식 플랫폼 아키텍처
본 플랫폼은 사용자가 도면을 띄운 상태에서의 내부 질의(내부 검색)와 도면 밖 글로벌 검색창에서의 질의(글로벌 검색)를 모두 수용하며, 도면의 버전과 마크업을 Git 스타일로 제어하는 하이브리드 토폴로지를 가집니다.

```mermaid
graph TD
    %% 클라이언트 영역
    subgraph Client_App["React 클라이언트 웹앱"]
        ChatUI[AI 챗봇 인터페이스]
        Route[React Router: 세션 파라미터 제어]
        Viewer[자체 웹 CAD 뷰어]
        MarkupLayer[SVG 마크업 커밋 오버레이]
        EvtBus[프론트엔드 이벤트 버스]
    end

    %% API 게이트웨이 및 오케스트레이터
    subgraph Service_App["서버 백엔드 (FastAPI)"]
        API[API 게이트웨이 / 인증]
        RAG[LLM RAG & 검색 인덱서]
        DiffEngine[도면 기하 Diff 엔진]
        DwgParser[ACadSharp 기반 파서 워커]
    end

    %% 데이터 보존 영역
    subgraph Storage_DB["데이터베이스 및 파일 스토리지"]
        RDB[(PostgreSQL: Git-like 이력 테이블)]
        S3[(AWS S3: 도면 버킷 & 마크업 커밋 캐시)]
        DKS_Base[(DKS 백엔드: DXF 기반 TypeDB 지식망)]
    end

    %% 1. 내부 검색 흐름 (도면 오픈 상태)
    Viewer -->|1. 도면 활성화 세션| EvtBus
    ChatUI -->|2. 도면 내부 설비 질의| RAG
    RAG -->|3. TypeDB 추론 결과 및 Handle 반환| ChatUI
    ChatUI -->|4. HIGHLIGHT_OBJECTS 이벤트 발행| EvtBus
    EvtBus -->|5. 특정 개체 줌인 & 점멸| Viewer

    %% 2. 글로벌 검색 및 세션 전이 흐름 (도면 밖 상태)
    ChatUI -->|6. 글로벌 설비 검색| RAG
    RAG -->|7. 대상 도면 리스트 검색| DKS_Base
    RAG -->|8. 도면 목록 반환| ChatUI
    ChatUI -->|9. 도면 클릭 / 세션 전이| Route
    Route -->|10. 쿼리 스트링 매개변수 전달| Viewer
    Viewer -->|11. 로딩 즉시 타겟 장비 하이라이트| Viewer

    %% 3. Git-like 버전 및 마크업 이력 흐름
    DwgParser -->|12. 버전별 기하 추출| DiffEngine
    DiffEngine -->|13. 추가/삭제 데이터 연산| RDB
    MarkupLayer -->|14. 마크업 커밋 푸시| S3
    RDB -->|15. Commit/Branch 관계 바인딩| S3
```

---

## 2. 하이브리드 연동 핵심 컴포넌트 설계 명세

### ① 세션 라우팅 & 파라미터 바인딩 (Route & Viewer Context)
* **글로벌 검색 전이 메커니즘**:
    * 사용자가 도면 외부에서 특정 설비(예: `VLV-101`)를 질문하여 도면 리스트 중 하나를 클릭하면, 라우터는 다음과 같은 규격의 URL로 뷰어를 트리거합니다.
      `https://dks.platform/project/청주/viewer?drawing_id=4a5b6c&highlight=1A2D&focus=true`
    * 웹 CAD 뷰어는 로딩 프로세스 완료 시점에 URL의 `highlight` 파라미터(Handle ID)를 파싱하여, PostgreSQL의 `entity_mappings`를 대조해 런타임 `db_id`를 획득하고 즉각 포커싱 액션을 자체 구동합니다.
* **도면 내 실시간 연동**:
    * 뷰어가 활성화되어 있을 때 챗봇 대화창에서 이벤트가 수신되면, 뷰어를 리로드하지 않고 **프론트엔드 이벤트 버스**를 통해 런타임 메모리 내에서 즉각 객체를 제어합니다.

### ② Git-like 버전 제어 & Diff 컴포넌트 (Git-like Versioning)
* **도면 커밋 관리**:
    * 도면이 업데이트되면 백엔드 파서는 새로운 도면 레코드를 생성하고 이를 이전 도면 레코드의 하위 노드(Commit Parent 관계)로 PostgreSQL에 기록합니다.
* **도면 기하 Diff 엔진**:
    * 새로운 버전이 등록되는 시점에 백엔드 `DiffEngine`이 작동하여 구버전 기하 JSON과 신버전 기하 JSON을 배치 비교합니다.
    * 좌표가 정확히 일치하나 속성이 변한 것(수정), 새로운 좌표에 생성된 것(추가), 기존 좌표에서 없어진 것(삭제)을 판별하여 `drawings_diff` 캐시 테이블에 저장해 둡니다.
    * 사용자가 뷰어에서 '비교 토글'을 켜면, 뷰어는 서버로부터 이 Diff 데이터를 가져와 기존 도면 위에 오버랩 드로잉합니다.

### ③ Git-like 마크업 이력 (Markup Commit Layer)
* **마크업 레이어링**:
    * 사용자가 뷰어 화면 위에 펜으로 지시선을 그리고 저장하면, 도면의 원본 파일을 수정하는 것이 아니라, 해당 도면의 특정 버전(Commit ID)을 부모로 두는 **'마크업 커밋(Markup Commit)'** 객체를 생성합니다.
    * 이 마크업 데이터는 [[JSON]] 벡터 패스 구조로 S3 스토리지에 업로드되며, PostgreSQL에는 `markup_commits` 테이블에 작성자, 작성일, 내용, 부모 도면 버전 정보가 기록됩니다.
    * 뷰어는 도면 로딩 시 활성화된 마크업 커밋 레이어들의 JSON을 병렬 다운로드하여 뷰어 씬 위에 투명 오버레이로 덧그려줍니다.
