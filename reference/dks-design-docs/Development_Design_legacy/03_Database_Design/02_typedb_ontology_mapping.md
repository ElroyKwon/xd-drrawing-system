---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - 데이터베이스
  - TypeDB
  - 온톨로지
  - RAG
created: 2026-06-12
related:
  - "[[README]]"
  - "[[01_rdb_schema_design]]"
---

# 03-2. TypeDB 온톨로지 지식 매핑 및 동기화 설계

> **목적**: 복잡한 장비 계통 관계(P&ID, 단선도 등)를 지식 그래프화하여 추론하기 위한 TypeDB 스키마 설계 원칙 및 웹 뷰어와의 Handle ID 기반 동기화 전략을 정의합니다.

## 1. TypeDB 스키마 모델링 원칙 (V3.2 기반)

본 플랫폼의 온톨로지는 도면의 단순 기하 형상이 아니라 "설비의 논리적 연결성"과 "엔지니어링 메타 속성"에 집중합니다.

```typedb
define

# 1. 속성(Attributes) 정의
handle-id sub attribute, value string;
tag-name sub attribute, value string;
equipment-class sub attribute, value string;
spec-value sub attribute, value double;

# 2. 엔티티(Entities) 정의
equipment sub entity,
    owns handle-id,
    owns tag-name,
    owns equipment-class;

valve sub equipment,
    owns spec-value;

pipe sub equipment;

# 3. 관계(Relations) 정의
connected-to sub relation,
    relates source,
    relates target;

# 4. 역할 부여
equipment plays connected-to:source;
equipment plays connected-to:target;
```

## 2. DXF 파이프라인 - TypeDB 동기화 흐름

1. **지식 추출**: DKS 백엔드의 별도 DXF 파이프라인이 도면의 BLOCK 데이터나 Text 속성을 분석하여, 각 객체의 CAD 고유 `Handle ID`를 추출합니다.
2. **지식 주입**: 추출된 정보는 TypeDB 서버에 엔티티(`equipment`)로 주입되며, 해당 엔티티는 필연적으로 `handle-id` 속성을 갖게 됩니다.
3. **독자성 보장**: 웹 CAD 뷰어나 챗봇 인터페이스는 데이터베이스 부하를 고려해 TypeDB에 직접 CUD 쿼리를 수행하지 않습니다. 온톨로지 업데이트는 도면 커밋(Git-like Update) 발생 시 백엔드 스케줄러에 의해 비동기로 동기화됩니다.

## 3. RAG 챗봇 - 뷰어 가교 (Entity Mapping Strategy)

가장 중요한 것은 "AI가 추론한 결과를 사용자가 보고 있는 도면 화면에 어떻게 정확히 하이라이트할 것인가"입니다.

### 3.1 추론 및 Handle ID 획득
사용자가 챗봇에 "101번 냉각수 펌프와 직렬로 연결된 밸브를 모두 찾아줘"라고 질문합니다.
LLM은 이를 TypeDB TQL(TypeQL) 쿼리로 변환하고, TypeDB 추론 엔진은 해당 조건을 만족하는 밸브 엔티티들의 **`handle-id` 목록** (예: `['2B4', '2B7']`)을 반환합니다.

### 3.2 프론트엔드 이벤트 버스 페이로드 규격
AI 챗봇은 응답 텍스트와 함께 아래와 같은 커스텀 이벤트 페이로드를 생성하여 프론트엔드 이벤트 버스에 발송합니다.

```json
{
  "event_type": "HIGHLIGHT_KNOWLEDGE_ENTITIES",
  "payload": {
    "intent": "search_connected_valves",
    "target_handles": ["2B4", "2B7"],
    "action_params": {
      "zoom_to_fit": true,
      "blink": true,
      "color": "#ff0000"
    }
  }
}
```

### 3.3 로컬 매핑을 통한 고속 렌더링
이벤트를 수신한 웹 뷰어는 RDB에 연동된 캐시 테이블(`entity_mappings`)에서 `external_id`('2B4', '2B7')를 조회해 현재 화면의 `db_id`(Three.js Mesh ID 등)로 즉시 맵핑한 후, 지연 시간 없이 카메라를 패닝하고 해당 메쉬의 색상을 붉은색으로 점멸시킵니다.
