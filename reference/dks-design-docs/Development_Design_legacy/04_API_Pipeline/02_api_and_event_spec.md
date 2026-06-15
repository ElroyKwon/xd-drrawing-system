---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - 파이프라인
  - API
  - WebSocket
  - 이벤트버스
created: 2026-06-12
related:
  - "[[README]]"
  - "[[01_acadsharp_parsing_engine]]"
  - "[[03_Database_Design/01_rdb_schema_design]]"
---

# 04-2. 시스템 RESTful API 및 이벤트 버스 연동 명세서

> **목적**: 클라이언트 웹앱(React/Three.js)과 백엔드(FastAPI)가 소통하는 핵심 REST API 목록과, AI 챗봇의 추론 결과를 실시간 뷰어 제어로 이어주는 WebSocket 프론트엔드 이벤트 버스(Event Bus) 페이로드 규격을 정의합니다.

---

## 1. 핵심 RESTful API Endpoints (Git-like 제어)

모든 API는 인증 헤더(Bearer Token)를 요구하며, 프로젝트 권한 기반 인가(Authorization)를 거칩니다.

### 1.1 도면 커밋 및 버전 제어 (Drawings)
* `POST /api/v1/projects/{project_id}/drawings`
  * **기능**: 도면(.dwg) 파일 멀티파트 업로드 및 파이프라인 트리거.
  * **응답**: `202 Accepted` (비동기 파싱 Job ID 반환)
* `GET /api/v1/drawings/{drawing_id}/history`
  * **기능**: 특정 도면의 과거부터 현재까지의 Git-like 커밋(버전) 이력 조회.
  * **응답**: 버전 트리 배열 (생성일, 해시값, 커밋 메시지, 작성자 포함).
* `POST /api/v1/drawings/{drawing_id}/rollback/{target_commit_hash}`
  * **기능**: 최신 도면을 과거 버전 상태로 되돌리기 (새로운 롤백 커밋 생성).

### 1.2 차분 대조 (Auto Diff Engine)
* `GET /api/v1/drawings/{target_id}/diff?source_id={source_id}`
  * **기능**: 두 도면 간의 기하학적 차이점 목록 캐시 조회.
  * **응답**: 
    ```json
    {
      "diff_id": 105,
      "added_handles": ["2A4", "3F1"],
      "deleted_handles": ["1B2"],
      "modified_handles": []
    }
    ```

### 1.3 마크업 커밋 관리 (Markups)
* `POST /api/v1/drawings/{drawing_id}/markups`
  * **기능**: 화면 위에 그린 펜선/텍스트 SVG 경로를 JSON으로 묶어 독립적 마크업 커밋 등록.
* `PATCH /api/v1/markups/{markup_id}/status`
  * **기능**: 마크업 피드백 상태 변경 (`OPEN` -> `MERGED` 또는 `CLOSED`).
* `GET /api/v1/drawings/{drawing_id}/markups?status=OPEN`
  * **기능**: 도면에 렌더링해야 할 활성 오버레이 마크업 목록과 SVG JSON 패스 조회.

---

## 2. 하이브리드 검색 및 챗봇 연동 API

* `POST /api/v1/ai/chat`
  * **기능**: 사용자의 자연어 질문 전송 (글로벌/로컬 세션 공통).
  * **요청 바디**: `{"message": "2층 기계실의 모든 소방 펌프를 찾아줘", "context_drawing_id": "uuid(optional)"}`
  * **응답 바디**:
    ```json
    {
      "answer": "2층 기계실에는 총 3대의 소방 펌프(P-101, P-102, P-103)가 연결되어 있습니다.",
      "related_drawings": ["uuid-1", "uuid-2"], // 글로벌 검색 시 전이할 도면 목록
      "target_handles": ["2B1", "2B2", "2B3"]  // 로컬 세션용 하이라이트 핸들 리스트
    }
    ```

---

## 3. 프론트엔드 실시간 이벤트 버스 (Event Bus) 명세

웹 CAD 플랫폼 내에서 React UI(챗봇, 메뉴 패널)와 Three.js WebGL 뷰어 캔버스 간의 상태를 동기화하기 위해 커스텀 이벤트 버스(Pub/Sub) 아키텍처를 가동합니다.

### 3.1 AI 타겟 하이라이트 이벤트 (`AI_TARGET_HIGHLIGHT`)
* **발송자 (Pub)**: 챗봇 UI 컴포넌트 (API 응답 수신 직후)
* **수신자 (Sub)**: WebGL 뷰어 컨트롤러
* **동작**: 수신된 `handles` 목록을 로컬 매핑 테이블(`entity_mappings`)에서 뒤져 Mesh ID를 얻고, 파란색으로 점멸시키며 카메라를 줌인합니다.
* **Payload**:
  ```javascript
  {
    type: "AI_TARGET_HIGHLIGHT",
    payload: {
      handles: ["2B1", "2B2", "2B3"],
      zoomToFit: true,
      color: 0x00A8FF,   // 하이라이트 색상 (헥스코드)
      blinkCycle: 3      // 점멸 횟수
    }
  }
  ```

### 3.2 뷰어 객체 선택 이벤트 (`VIEWER_OBJECT_SELECTED`)
* **발송자 (Pub)**: WebGL 뷰어 컨트롤러 (사용자가 도면에서 밸브 클릭 시)
* **수신자 (Sub)**: 속성 패널 UI, 챗봇 UI
* **동작**: 우측 속성 패널에 해당 객체의 메타데이터(레이어, 블록 속성)를 표시하고, 챗봇 입력창에 자동으로 "V-101(Handle:2B1)의 연결 계통은?" 이라는 프롬프트 프리픽스를 삽입합니다.
* **Payload**:
  ```javascript
  {
    type: "VIEWER_OBJECT_SELECTED",
    payload: {
      handle: "2B1",
      layerName: "M_FIRE_PUMP",
      attributes: {
        "Tag": "P-101",
        "Spec": "15HP"
      }
    }
  }
  ```

### 3.3 Diff 오버레이 토글 이벤트 (`TOGGLE_DIFF_MODE`)
* **발송자 (Pub)**: 상단 네비게이션 Diff 토글 스위치
* **수신자 (Sub)**: WebGL 뷰어 컨트롤러
* **동작**: 현재 도면에 Diff 캐시 데이터를 입히거나(ON), 뺍니다(OFF).
* **Payload**:
  ```javascript
  {
    type: "TOGGLE_DIFF_MODE",
    payload: {
      enabled: true,
      sourceDrawingId: "uuid-v1" // 대조할 과거 버전 ID
    }
  }
  ```
