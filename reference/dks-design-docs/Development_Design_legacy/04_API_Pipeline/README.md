---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - 파이프라인
  - API
  - Git_like
  - RESTful
aliases:
  - 백엔드 파이프라인 및 API 설계 명세
  - API 상세 지침
created: 2026-06-11
updated: 2026-06-11
related:
  - "[[design_documents_map]]"
  - "[[03_Database_Design/README]]"
  - "[[01_Requirements/03_functional_requirements]]"
---

# 04. 백엔드 API 및 파이프라인 설계서 (API)

## 1. Git-like 버전 및 마크업 이력 제어 API 명세 (FastAPI)

### ① 도면 커밋 히스토리 조회
* **Endpoint**: `GET /api/v1/projects/{project_id}/drawings/{drawing_name}/history`
* **Response**:
  ```json
  [
    {
      "drawing_id": "4a5b6c7d-8e9f-0a1b-2c3d-4e5f6a7b8c9d",
      "commit_hash": "a1b2c3d4e5f6g7h8i9j0...",
      "parent_drawing_id": "9z8y7x6w-5v4u-3t2s-1r0q-...",
      "commit_message": "2층 기계실 펌프 P-102 교체 반영",
      "author": "홍길동 대리",
      "created_at": "2026-06-11T13:00:00Z"
    }
  ]
  ```

### ② 도면 간 기하학적 Diff 캐시 조회 (Auto Diff 용)
* **Endpoint**: `GET /api/v1/drawings/{target_drawing_id}/diff/{source_drawing_id}`
* **Response**:
  ```json
  {
    "source_commit": "a1b2c3d4...",
    "target_commit": "z9y8x7w6...",
    "added": [
      {
        "handle": "3F2A",
        "type": "LINE",
        "start": {"x": 105.0, "y": 200.0},
        "end": {"x": 105.0, "y": 350.0},
        "layer": "M_PIPE_NEW"
      }
    ],
    "deleted": [
      {
        "handle": "1B2C",
        "type": "LINE",
        "start": {"x": 105.0, "y": 200.0},
        "end": {"x": 105.0, "y": 300.0},
        "layer": "M_PIPE_OLD"
      }
    ],
    "modified": []
  }
  ```

### ③ 마크업 커밋 등록 (마크업 저장)
* **Endpoint**: `POST /api/v1/drawings/{drawing_id}/markups/commit`
* **Request Body**:
  ```json
  {
    "parent_markup_id": null,
    "markup_data": {                                -- SVG 드로잉 및 주석 데이터의 JSON 스트림
      "paths": [
        {"color": "#ff0000", "width": 3, "points": [{"x": 10, "y": 20}, {"x": 50, "y": 60}]}
      ],
      "comments": [
        {"position": {"x": 55, "y": 65}, "text": "이 부분 배관 확인 요망"}
      ]
    },
    "commit_message": "배관 연결 불량 부위 주석 추가",
    "author": "김철수 과장"
  }
  ```
* **Response**:
  ```json
  {
    "markup_id": "8f7e6d5c-4b3a-2i1o-0p9q-...",
    "status": "OPEN",
    "created_at": "2026-06-11T13:05:00Z"
  }
  ```

### ④ 마크업 커밋 목록 조회 (이력 레이어용)
* **Endpoint**: `GET /api/v1/drawings/{drawing_id}/markups`
* **Response**:
  ```json
  [
    {
      "markup_id": "8f7e6d5c-4b3a-2i1o-0p9q-...",
      "commit_message": "배관 연결 불량 부위 주석 추가",
      "author": "김철수 과장",
      "markup_json_url": "/static/markups/8f7e6d5c.json",
      "status": "OPEN",
      "created_at": "2026-06-11T13:05:00Z"
    }
  ]
  ```

---

## 2. 변환 캐시 JSON 규격 업데이트
* 백엔드가 도면 변환 후 생성하는 JSON 스키마의 `metadata` 세션에 Git-like 이력 보존을 위한 키를 추가 반영합니다.
```json
{
  "metadata": {
    "drawingName": "청주사업장_2F_기계계통도.dwg",
    "commitHash": "a1b2c3d4e5f6g7h8i9j0...",
    "parentCommitHash": "9z8y7x6w5v4u3t2s1r0q...",
    "boundingBox": {
      "min": {"x": -1500.5, "y": -1200.3},
      "max": {"x": 8500.2, "y": 6200.8}
    },
    "centerOffset": {"x": 3500.0, "y": 2500.0}
  },
  "layers": [...],
  "blocks": {...},
  "entities": [...]
}
```
