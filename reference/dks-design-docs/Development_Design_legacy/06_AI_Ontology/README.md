---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - AI에이전트
  - 온톨로지
  - TypeDB
  - RAGflow
  - 이벤트버스
aliases:
  - AI 에이전트 및 온톨로지 연동 규격
  - AID 상세 지침
created: 2026-06-11
updated: 2026-06-11
related:
  - "[[design_documents_map]]"
  - "[[05_Web_CAD_Viewer/README]]"
---

# 06. AI 에이전트 & 온톨로지 연동 설계서 (AID)

## 1. AI RAG 및 TypeDB 지식 추론 파이프라인
사용자의 질문을 수신하여 자연어로 대답하고 도면을 원격 제어하기 위한 전체 AI 오케스트레이션 인터페이스 흐름 설계입니다.

```
[사용자 자연어 질의] ──► [LLM Intent 분류기]
                              │
                              ├─► [비정형 정보]: RAGflow 검색 연동 (벡터 DB 매뉴얼 검색)
                              └─► [구조화 정보]: TQL (TypeDB Query) 생성기
                                       │
                                       ▼ (TypeDB 실행)
                               [장비 연계망 추론] ──► [결과 JSON 매핑]
                                                             │
                                                             ▼
                                     [AI 답변 출력 및 뷰어 이벤트 발행]
```

---

## 2. 양방향 이벤트 버스(Event Bus) 및 메시지 규격
챗봇 컴포넌트와 자체 웹 CAD 뷰어 컴포넌트 간의 결합도를 낮추기 위해 **Window Custom Event** 기반의 프론트엔드 이벤트 버스를 설계합니다.

### ① AI 응답 JSON 스키마 (FastAPI ──► Chat UI)
AI가 설비 계통의 관계를 추론하여 웹 프론트엔드로 전달할 때의 규격화된 API 응답 스펙입니다.
```json
{
  "query": "AHU-01의 냉수 공급 냉동기는?",
  "answer": "AHU-01 항온항습기는 Cold_Pipe라인을 거쳐 CH-01 냉동기 및 P-101 펌프로부터 냉수를 공급받습니다.",
  "visualActions": [
    {
      "actionType": "HIGHLIGHT_OBJECTS",
      "payload": {
        "targetIds": ["2F1A", "3C2B", "4D5E"],     -- 하이라이트할 설비의 External Handle ID 목록
        "color": "#00ff00",
        "flash": true
      }
    },
    {
      "actionType": "ZOOM_TO_FIT",
      "payload": {
        "targetIds": ["2F1A", "3C2B", "4D5E"],
        "padding": 50
      }
    }
  ]
}
```

### ② 프론트엔드 이벤트 리스너 바인딩 코드
챗봇 UI가 상기 `visualActions`를 수신했을 때 프론트엔드 이벤트 버스를 통해 웹 CAD 뷰어를 원격 구동하는 구현 명세입니다.
```javascript
// 1. 이벤트 버스 클래스 정의
class CADEventBus {
  static publish(eventType, detail) {
    const event = new CustomEvent(`cad-event:${eventType}`, { detail });
    window.dispatchEvent(event);
  }

  static subscribe(eventType, callback) {
    window.addEventListener(`cad-event:${eventType}`, callback);
  }
}

// 2. 챗봇 컴포넌트에서 이벤트 발행 (AI 응답 수신 시)
function handleAIResponse(response) {
  if (response.visualActions) {
    response.visualActions.forEach(action => {
      CADEventBus.publish(action.actionType, action.payload);
    });
  }
}

// 3. 웹 CAD 뷰어 컴포넌트에서 이벤트 수신 및 조작 실행
CADEventBus.subscribe('HIGHLIGHT_OBJECTS', (event) => {
  const { targetIds, color } = event.detail;
  
  // PostgreSQL 매핑 API 혹은 뷰어 사전 로딩 Map을 통해 ExternalId를 dbId로 변환
  const dbIds = targetIds.map(handle => viewer.getDbIdByHandle(handle)).filter(Boolean);
  
  if (dbIds.length > 0) {
    viewer.setObjectsColor(dbIds, color); // 뷰어 색상 변경 하이라이트
  }
});

CADEventBus.subscribe('ZOOM_TO_FIT', (event) => {
  const { targetIds } = event.detail;
  const dbIds = targetIds.map(handle => viewer.getDbIdByHandle(handle)).filter(Boolean);
  
  if (dbIds.length > 0) {
    viewer.fitToView(dbIds); // 카메라 뷰 포커싱
  }
});
```

---

## 3. LLM Intent 분류 및 TQL 생성 템플릿
* **기반 프롬프트 철학**: LLM이 직접 데이터베이스를 핸들링할 때의 신뢰성 확보를 위해, 사전에 온톨로지 스키마(entities, relations)를 Context에 주입하고, 질의에 부합하는 TypeDB Read-only 템플릿 쿼리만 한정적으로 작성하도록 가이드라인을 부여합니다.
* **TQL 변환 Few-shot 예시**:
  ```
  [User Question]: "P-101 펌프가 급수해주는 장비들의 태그를 알려줘."
  [Target TQL]:
  match
    $p isa PumpingUnit, has tag "P-101";
    $target isa AirHandlingUnit, has tag $tag;
    (source: $p, destination: $target) isa connection;
  get $tag;
  ```
* **할루시네이션 가드레일**: 생성된 TQL 쿼리는 백엔드 TQL 파서(TQL Validator)를 통해 문법적 정합성이 100% 검증된 후에만 TypeDB 트랜잭션 세션으로 전송되어 예기치 못한 DB 오류를 사전에 차단합니다.
