---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - 데이터베이스
  - 스키마
  - Git_like
  - PostgreSQL
aliases:
  - 데이터베이스 및 온톨로지 스키마 설계
  - DBD 상세 지침
created: 2026-06-11
updated: 2026-06-11
related:
  - "[[design_documents_map]]"
  - "[[02_System_Architecture/README]]"
  - "[[01_Requirements/03_functional_requirements]]"
---

# 03. 데이터베이스 설계서 (DBD)

## 1. 관계형 데이터베이스 (RDB) 테이블 스펙 명세 (Git-like 설계 적용)
서비스 운영 및 Git 스타일의 도면/마크업 이력 제어를 위한 PostgreSQL 상세 스키마 설계입니다.

### ① `projects` (프로젝트 관리)
```sql
CREATE TABLE projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### ② `drawings` (Git-like 도면 커밋 및 버전 이력 관리)
* **설명**: 도면을 Git의 커밋 트리 구조처럼 부모 커밋 ID(`parent_drawing_id`) 관계를 갖도록 설계하여 이전 버전과의 선후 관계를 추적합니다.
```sql
CREATE TABLE drawings (
    drawing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    drawing_name VARCHAR(255) NOT NULL,
    dwg_file_path VARCHAR(512) NOT NULL,            -- S3 내 원본 DWG 경로
    json_cache_path VARCHAR(512) NOT NULL,          -- 파싱된 경량 JSON 캐시 경로
    parent_drawing_id UUID REFERENCES drawings(drawing_id) ON DELETE SET NULL, -- Git의 Parent Commit 역할
    commit_hash VARCHAR(64) NOT NULL,               -- 도면 파일의 SHA-256 해시값 (버전 고유 키)
    commit_message TEXT,                            -- 버전 변경 사항 요약 메모
    author VARCHAR(100) NOT NULL,                   -- 업로드 작성자
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_drawings_project_hash ON drawings(project_id, commit_hash);
```

### ③ `drawings_diff` (도면 버전 간 기하 차이점 캐시)
* **설명**: V1 대비 V2 도면의 기하학적 차이점(추가된 라인, 삭제된 라인 등의 Handle ID 목록)을 백엔드가 사전 연산하여 캐싱해 두는 테이블입니다.
```sql
CREATE TABLE drawings_diff (
    diff_id BIGSERIAL PRIMARY KEY,
    source_drawing_id UUID REFERENCES drawings(drawing_id) ON DELETE CASCADE, -- 부모 도면 버전 (V1)
    target_drawing_id UUID REFERENCES drawings(drawing_id) ON DELETE CASCADE, -- 현재 도면 버전 (V2)
    added_handles JSONB NOT NULL,                   -- 추가된 객체 Handle ID 목록 (예: ["1A2B", "3C4D"])
    deleted_handles JSONB NOT NULL,                 -- 삭제된 객체 Handle ID 목록 (예: ["5E6F"])
    modified_handles JSONB NOT NULL,                -- 속성만 수정된 객체 Handle ID 목록
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_diff_pair UNIQUE (source_drawing_id, target_drawing_id)
);
```

### ④ `markup_commits` (Git-like 마크업 피드백 커밋 관리)
* **설명**: 도면 위에 얹는 펜 드로잉이나 수정 주석을 도면 본체와 분리하여 독자적인 마크업 커밋으로 관리합니다.
```sql
CREATE TABLE markup_commits (
    markup_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID REFERENCES drawings(drawing_id) ON DELETE CASCADE, -- 마크업의 기준 도면 버전
    parent_markup_id UUID REFERENCES markup_commits(markup_id) ON DELETE SET NULL, -- 마크업 이력 연결용
    markup_json_path VARCHAR(512) NOT NULL,         -- S3 내 마크업 벡터 패스 JSON 파일 경로
    commit_message TEXT NOT NULL,                   -- 마크업 피드백 설명 (예: "냉각수 밸브 위치 수정 바람")
    author VARCHAR(100) NOT NULL,                   -- 작성자
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',     -- OPEN, MERGED (도면에 최종 반영 완료), CLOSED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_markup_drawing ON markup_commits(drawing_id);
```

### ⑤ `entity_mappings` (ExternalId - DbId 매핑 테이블)
```sql
CREATE TABLE entity_mappings (
    mapping_id BIGSERIAL PRIMARY KEY,
    drawing_id UUID REFERENCES drawings(drawing_id) ON DELETE CASCADE,
    external_id VARCHAR(64) NOT NULL,               -- CAD 고유 Handle ID
    db_id INT NOT NULL,                             -- 웹 뷰어 세션별 임시 ID
    entity_tag VARCHAR(100),                        -- 설비 태그명
    entity_class VARCHAR(100) NOT NULL,             -- 설비 클래스명
    CONSTRAINT uq_drawing_external UNIQUE (drawing_id, external_id)
);
CREATE INDEX idx_mappings_external ON entity_mappings(drawing_id, external_id);
```

---

## 2. TypeDB 지식 가교 및 동기화 설계
* **독자 노선 분리**: [[TypeDB]] 스키마 빌드 및 지식 주입 파이프라인은 DKS 백엔드가 [[DXF]] 등에서 변환해 독자적으로 가동하므로, 본 도면관리 플랫폼의 뷰어는 직접 TypeDB에 쿼리하지 않습니다.
* **매핑 가교**: AI RAG가 지식 기반으로 답을 찾아 설비의 고유 `ExternalId`(Handle)를 이벤트로 던져주면, 뷰어는 본 RDB의 **`entity_mappings`** 테이블을 로컬 캐시처럼 조회하여 현재 활성화된 뷰어 세션 내의 임시 `DbId`로 변환 매핑하여 화면을 제어합니다.
