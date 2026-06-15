# 06 · 데이터 스키마

타입 정의는 **`src/lib/types.ts`가 단일 진실**이다. JSON 시드 3개는 그 타입의 인스턴스로 해석된다(`as DocSnippet[]` 캐스팅).

## 1. 타입 (types.ts 전체)

```ts
export type Discipline = "ELECTRICAL" | "MECHANICAL" | "FIRE" | "FACILITY";

export interface DocFile {
  format: "DWG" | "PDF" | "PNG";
  url: string;
  size_kb: number;
}

export interface DocSnippet {
  doc_id: string;
  title: string;
  type: string;                   // "drawing" | "manual" | "spec" | "code" | "checklist" 등 자유 문자열
  discipline: Discipline;
  page: number;                   // 대표 페이지
  snippet: string;                // 요약문 (검색 대상)
  drawing_ref: string | null;     // public/drawings/ 하위 이미지 파일명
  last_updated: string;           // "YYYY-MM-DD"
  files?: DocFile[];
  download_enabled?: boolean;

  // 이하는 타입에만 추가돼 있고 현재 JSON 시드에선 미사용
  drawing_number?: string;
  drawing_type?: string;
  location?: string;
  revision?: string;
}

export type AnnotationKind = "info" | "warning" | "field-note";

export interface Annotation {
  id: string;
  doc_id: string;
  page: number;
  x: number;           // 0~1 정규화
  y: number;           // 0~1 정규화
  text: string;
  author: string;
  created_at: string;  // ISO 8601
  tags?: string[];
  type: AnnotationKind;
}

export interface DocEntityLink {
  doc_id: string;
  entity_tag: string;
  page?: number;
}
```

## 2. 세 개의 JSON 시드

### 2.1 `data/documents.json`

**8건, 200~300KB**. 포맷 예시 (doc-001):

```json
{
  "doc_id": "doc-001",
  "title": "BESS 전기 단선도 — KEY SLD",
  "type": "drawing",
  "discipline": "ELECTRICAL",
  "page": 3,
  "snippet": "KEPCO 인입 → VCB-001(24kV 630A) → 메인버스 → 4개 분기 (VCB-002~005). 22.9kV 수배전반.",
  "drawing_ref": "page_003.png",
  "last_updated": "2026-04-08",
  "files": [
    { "format": "PDF", "url": "/drawings/real/elec-sld.pdf", "size_kb": 464 }
  ],
  "download_enabled": true
}
```

| 필드 | 의미 |
|---|---|
| `doc_id` | 전체 시스템에서 유일. `"doc-NNN"` 컨벤션. Annotation/DocEntityLink의 FK. |
| `title` | 좌측 리스트, 뷰어 상단, 주석 그룹 헤더에 표시. |
| `type` | 리스트 칩 필터에 그대로 노출. 현재 `availableTypes`가 자동 계산. |
| `discipline` | enum 고정. 칩 필터 + 뱃지 색. |
| `page` | 리스트에 `p.N`으로 표시되는 **대표 페이지**(예: "이 문서의 관심 페이지"). 뷰어의 초기 페이지가 아님. 뷰어는 항상 `pageOverride ?? 1`로 시작. |
| `snippet` | Fuse 검색의 2순위 대상. 리스트 카드에 2줄 clamp. |
| `drawing_ref` | `public/drawings/{값}`으로 해석. null이면 이미지 폴백 불가. |
| `last_updated` | 표시용만. 정렬 키로는 안 쓰임. |
| `files[]` | 현재는 PDF 한 개. 여러 포맷 시 `format`이 `"PDF"`인 첫 항목이 `<Document file=...>`로 감. |
| `download_enabled` | 타입에는 있지만 현재 UI에서 확인/사용 안 함. |

**미사용 optional 필드** (`drawing_number`, `drawing_type`, `location`, `revision`): 도면 메타를 상세히 표현하려고 타입에 추가했으나 **현재 시드도 UI도 사용하지 않는다**. 실제 도면 메타가 확정되면 리스트 카드/뷰어 헤더에 표시할 수 있음.

### 2.2 `data/annotations.json`

**현재 빈 배열 `[]`**. 시드 값 존재 시 localStorage에 아무것도 없는 첫 접속자에게 보여진다. 실제 주석은 브라우저 localStorage에 저장됨.

**주입 시점**: `src/lib/data-loader.ts`의 `seedAnnotations` → `src/lib/annotations-store.ts`의 `useState(seedAnnotations)` 초기값.

### 2.3 `data/doc-entity-links.json`

현재 8건:
```json
[
  { "doc_id": "doc-003", "entity_tag": "CH-001",    "page": 12 },
  { "doc_id": "doc-004", "entity_tag": "CH-001",    "page": 1  },
  { "doc_id": "doc-004", "entity_tag": "CH-002",    "page": 1  },
  { "doc_id": "doc-001", "entity_tag": "VCB-001",   "page": 3  },
  { "doc_id": "doc-001", "entity_tag": "VCB-002",   "page": 3  },
  { "doc_id": "doc-008", "entity_tag": "GEN-001",   "page": 8  },
  { "doc_id": "doc-006", "entity_tag": "AV-3F-001", "page": 1  },
  { "doc_id": "doc-002", "entity_tag": "PCS-001",   "page": 42 }
]
```

**연결 매트릭스**:

| 태그 | 도면 |
|---|---|
| CH-001 | doc-003 (매뉴얼, p.12), doc-004 (계통도, p.1) |
| CH-002 | doc-004 (계통도, p.1) |
| VCB-001 | doc-001 (단선도, p.3) |
| VCB-002 | doc-001 (단선도, p.3) |
| GEN-001 | doc-008 (비상발전기 시방서, p.8) |
| AV-3F-001 | doc-006 (소방평면도, p.1) |
| PCS-001 | doc-002 (PCS 매뉴얼, p.42) |

7개 고유 태그, 8개 링크.

## 3. localStorage 포맷

키: `"mvp-annotations-v1"`  
값: `JSON.stringify(Annotation[])`

예시:
```json
[
  {
    "id": "ann-1760710234567-a7x2k",
    "doc_id": "doc-004",
    "page": 1,
    "x": 0.40,
    "y": 0.35,
    "text": "여기 냉수 공급 기준점",
    "author": "Claude",
    "created_at": "2026-04-17T09:30:54.123Z",
    "tags": ["정비", "냉수"],
    "type": "info"
  }
]
```

## 4. 파일 의존성 맵

```
documents.json ────► DocSnippet[]
                      │
                      ├── Fuse index (search.ts)
                      ├── docById[doc_id]
                      └── availableTypes = Set(d.type)

annotations.json ──► seedAnnotations (빈 배열)
                      │
                      └── useState 초기값 → localStorage로 덮어씀

doc-entity-links ──► DocEntityLink[]
                      │
                      ├── tagToDocsIdx[TAG.upper()] = [doc_id...]
                      ├── allEntityTags (정렬된 유일 태그)
                      ├── docsForTag(tag) = DocSnippet[]
                      └── pageForDocEntity(doc, tag) = page?
```

## 5. 시드 편집 가이드

### 문서 추가
1. `data/documents.json`에 항목 추가. `doc_id`는 새 번호.
2. 실 PDF가 있으면 `public/drawings/real/`에 복사 후 `files[0].url`로 참조.
3. 이미지 폴백이 있으면 `public/drawings/`에 복사 후 `drawing_ref`로 파일명만 기재.
4. 새 `type` 문자열을 쓰면 필터 칩에 자동 등장 (`availableTypes` 자동 갱신).

### 설비 링크 추가
`data/doc-entity-links.json`에 `{doc_id, entity_tag, page?}` 추가. 대소문자는 상관 없음(`toUpperCase` 정규화). 중복 `(doc_id, entity_tag)` 방지를 위해 `tagToDocsIdx`는 내부적으로 dedupe한다.

### 주석 시드 채우기
보통은 빈 배열이지만 **데모용 샘플 주석**을 보이고 싶다면 `data/annotations.json`에 추가. localStorage에 아무것도 없을 때만 보임 — 주석 한 번이라도 만든 사용자에겐 안 보인다.

## 6. 정합성 검증

현재 런타임 검증은 **타입 캐스팅뿐**(`as DocSnippet[]`). 잘못된 JSON이 들어와도 런타임에 조용히 undefined 필드가 섞일 수 있다.

실 배포 전 필요해질 수 있는 검증:
- `doc-entity-links.json`의 `doc_id`가 `documents.json`에 실존하는가
- `drawing_ref`가 가리키는 파일이 `public/drawings/`에 있는가
- `files[].url`이 `public/` 하위로 해석 가능한가

이런 검증은 빌드 스크립트(e.g. `scripts/validate-data.ts`)로 분리하는 게 낫다. Layer 0에서는 시드가 8건이라 수동 검사로 충분.

## 7. 타입 안정성 노트

- `types.ts`는 **런타임 코드가 전혀 없다** — 순수 타입. 그래서 서버/클라 양쪽에서 안전하게 임포트 가능.
- `data-loader.ts`는 JSON을 번들 시간에 임포트하고 인덱스를 즉시 빌드한다. 모듈 레벨 싱글톤이라 컴포넌트가 수백 번 마운트돼도 인덱스는 한 번만 계산됨.
- `useAnnotationsStore`만 훅이고 나머지는 순수 함수/상수. **훅을 쓰는 유일한 곳은 `page.tsx`** — 이 분리 덕분에 뷰 컴포넌트는 localStorage 존재를 몰라도 된다.
