# 05 · 설비 역추적

"이 설비 태그(`CH-001`)가 어느 도면에 나오는가"를 역방향으로 찾는 기능. Layer 0의 4요소 중 가장 "지식관리스러운" 부분.

| 파일 | 역할 |
|---|---|
| `src/components/EntityToDocs.tsx` | 우측 탭 UI |
| `src/lib/data-loader.ts` | `tagToDocsIdx`, `docsForTag`, `pageForDocEntity` |
| `data/doc-entity-links.json` | 설비↔도면 매핑 시드 |

## 1. 데이터 모델

```ts
// src/lib/types.ts
export interface DocEntityLink {
  doc_id: string;
  entity_tag: string;  // "CH-001", "VCB-001" 등
  page?: number;       // 태그가 등장하는 페이지(선택)
}
```

`data/doc-entity-links.json` 예시 (현재 시드 8건):
```json
[
  { "doc_id": "doc-001", "entity_tag": "VCB-001", "page": 3 },
  { "doc_id": "doc-001", "entity_tag": "VCB-002", "page": 3 },
  { "doc_id": "doc-003", "entity_tag": "CH-001", "page": 12 },
  { "doc_id": "doc-004", "entity_tag": "CH-001", "page": 1 },
  ...
]
```

`(doc_id, entity_tag)`가 논리적 유일키. `page`는 옵션 — 없으면 클릭 시 페이지 1로 간주된다(`PdfViewer`가 `pageOverride=undefined` → `1`).

## 2. 파생 인덱스 (data-loader)

JSON 원본 그대로 쓰지 않고 **모듈 로드 시점에 두 개 인덱스를 빌드**한다.

```ts
export const tagToDocsIdx: Record<string, string[]> = (() => {
  const idx: Record<string, string[]> = {};
  for (const link of docEntityLinks) {
    const tag = link.entity_tag.toUpperCase();        // 정규화
    if (!idx[tag]) idx[tag] = [];
    if (!idx[tag].includes(link.doc_id)) idx[tag].push(link.doc_id);
  }
  return idx;
})();

export const allEntityTags: string[] = Array.from(
  new Set(docEntityLinks.map((l) => l.entity_tag.toUpperCase()))
).sort();
```

- `toUpperCase()` 정규화로 `ch-001`, `CH-001` 모두 동일 취급.
- `tagToDocsIdx["CH-001"] = ["doc-003", "doc-004"]`.
- `allEntityTags`는 우측 탭의 "전체 태그 칩"에 사용.

### 조회 함수
```ts
export function docsForTag(tag: string): DocSnippet[] {
  const docIds = tagToDocsIdx[tag.toUpperCase()] ?? [];
  return docIds.map((id) => docById[id]).filter(Boolean);
}

export function pageForDocEntity(doc_id: string, entity_tag: string): number | undefined {
  const link = docEntityLinks.find(
    (l) => l.doc_id === doc_id && l.entity_tag.toUpperCase() === entity_tag.toUpperCase()
  );
  return link?.page;
}
```

`pageForDocEntity`는 O(n) 선형 탐색이지만 8건이라 무시. 스케일이 커지면 `Record<docId, Record<tag, page>>`로 중첩 인덱스를 추가하면 됨.

## 3. UI: EntityToDocs

우측 사이드의 "설비 역추적" 탭. 111줄.

### 3.1 두 가지 진입

1. **직접 입력**: `<input placeholder="예: CH-001">`. 입력값이 `trimmed`로 정리돼 인덱스 조회.
2. **칩 클릭**: 입력이 비어있을 때만 `allEntityTags` 전체를 칩으로 나열. 칩 클릭은 `setTag(s)`로 입력값을 채운다.

```
┌─ 설비 태그 역추적 ──────────────────────┐
│ [예: CH-001                          ] │  ← input
│                                        │
│ 전체 태그: 7건                         │
│ [AV-3F-001] [CH-001] [CH-002] [GEN-001]│  ← chips (입력 비었을 때만)
│ [PCS-001] [VCB-001] [VCB-002]          │
├────────────────────────────────────────┤
│ 냉동기 운전 매뉴얼 (Carrier 30XW)      │
│  manual · MECHANICAL · p.12            │  ← hits (매칭되면 표시)
│ ─────────────────────────────────────  │
│ 데이터센터 냉방 계통도                 │
│  drawing · MECHANICAL · p.1            │
├────────────────────────────────────────┤
│                          2건 매칭       │
└────────────────────────────────────────┘
```

### 3.2 자동완성

```ts
const suggestions = useMemo(() => {
  if (!trimmed) return [];
  const q = trimmed.toUpperCase();
  return allEntityTags.filter((t) => t.includes(q)).slice(0, 6);
}, [trimmed]);
```

- 입력값 기준 부분 문자열 매칭, 최대 6개.
- **렌더 조건**: `suggestions.length > 0 && hits.length === 0` — 매칭 문서가 이미 있으면 자동완성을 숨긴다(중복 노이즈 방지).

예: 사용자가 `CH` 입력 → hits는 `CH-001 + CH-002` 둘 다의 문서가 매칭 안 됨(정확 일치만) → suggestions로 `CH-001, CH-002`가 제시됨 → 칩 클릭하면 그 태그로 확정.

**한계**: 현재 `docsForTag`는 **정확 일치**만 찾는다. `CH`라고만 쳐도 CH-001, CH-002 문서를 한꺼번에 보여주고 싶다면 `docsForTag`에 prefix/substring 매칭을 추가해야 한다.

### 3.3 매칭 결과 (hits)

```ts
const hits: Array<{ doc: DocSnippet; page?: number }> = useMemo(() => {
  if (!trimmed) return [];
  const docs = docsForTag(trimmed);
  return docs.map((doc) => ({
    doc,
    page: pageForDocEntity(doc.doc_id, trimmed),
  }));
}, [trimmed]);
```

- 문서 + 해당 문서에서 그 태그가 나오는 페이지 번호를 같이 묶어서 반환.
- 페이지 정보 없으면 `undefined`.

### 3.4 클릭 핸들링

```tsx
<button onClick={() => onOpenDoc(doc.doc_id, page)}>
```

`page.tsx`에서 받는 측:
```tsx
<EntityToDocs
  onOpenDoc={(id, page) => {
    setSelectedId(id);
    setSelectedPage(page);
  }}
/>
```

**결과**:
- 중앙 뷰어가 그 문서로 교체 + 해당 페이지로 점프.
- 좌측 리스트의 선택 상태도 동기화(`selectedId`가 하이라이트 트리거).
- 우측 탭은 **그대로 "설비 역추적" 유지** — 다른 태그로 계속 탐색 가능.

## 4. 왜 이게 가치 있는가

기존 NAS+엑셀 시나리오:
1. "CH-001 도면 어딨지?" → 담당자에게 카톡
2. 답장 2시간 후: "Q:\설비\기계\2024\냉방\hvac-master.pdf에 있을걸"
3. 파일 열고 53페이지 중에서 `Ctrl+F`로 찾기
4. 또 다른 도면(매뉴얼)에도 있는지는 모름 → 다시 1번으로

Layer 0 시나리오:
1. 우측 탭에 `CH-001` 입력
2. 매칭 문서 2건 즉시 리스트 → 각각 클릭하면 해당 페이지 점프

**시간 압축**: 카톡 왕복 + 파일 서치 → 3초. 이게 가설의 핵심이다.

## 5. 링크 생성의 실무 쟁점

현재 `doc-entity-links.json`은 **손으로 편집된 시드 8건**. 실제 현장에서는:

- **자동 추출**: PDF에서 OCR로 `CH-001` 같은 토큰을 뽑아 링크 생성. OPAS/XGI 같은 태그 컨벤션이 있으면 정규식 가능.
- **수동 큐레이션**: 설비 담당자가 "이 도면에 이 설비가 있다"를 표시하는 UI. (Layer 1 업로드 기능의 후보 기능.)
- **하이브리드**: 자동 추출 후 담당자가 confirm/반려.

**범위 결정 근거**: Layer 0은 "역추적이 가치 있다"만 증명하면 된다. 링크를 누가 어떻게 만드는지는 Layer 1~2 문제.

## 6. 동일 태그 여러 페이지 케이스

예: `VCB-001`이 `doc-001`의 3페이지와 7페이지 양쪽에 나오는 경우. 현재 모델은 `(doc_id, entity_tag)` 유일키라 **한 페이지만 기록 가능**.

해결안:
- `page?: number` → `pages?: number[]`로 확장.
- EntityToDocs UI에서 `p.3, 7`처럼 쉼표 나열, 클릭 시 첫 페이지로 점프 + 페이지 네비게이터가 나머지 안내.

Layer 0에서는 미구현. 시드 데이터에도 해당 케이스 없음.

## 7. 확장 포인트

| 요구 | 수정 위치 |
|---|---|
| 부분 매칭(`CH` → `CH-001`, `CH-002`) | `docsForTag`에 fallback 매칭 추가 |
| 태그 카테고리(전기/기계) | `DocEntityLink`에 discipline 필드 |
| 역추적 결과를 학제로 필터링 | `EntityToDocs`에 discipline chip 추가 |
| 태그 alias (CH-001 ≡ CH001) | `data-loader`에서 정규화 규칙 |
| 링크 수동 편집 UI | 새 컴포넌트 `EntityLinker` — Layer 1 |
| 자동 추출 파이프라인 | 서버 측 — MVP 범위 밖 |

## 8. 알려진 이슈

- **한글 설비 태그 미지원**: `allEntityTags`/`tagToDocsIdx`가 `toUpperCase()`만 하고 한글은 그대로 둔다. 만약 시드에 `"냉동기-1호기"`가 들어오면 동작은 하지만 "CH-001" 관례와 섞여 UX가 어색. 컨벤션 통일 필요.
- **빈 태그 입력**: `trimmed === ""`에서 hits/suggestions 모두 빈 배열. 정상.
- **대소문자 혼용 시드**: 현재 시드는 모두 대문자. 소문자가 섞이면 `toUpperCase` 정규화로 자동 합쳐짐 — 의도된 동작.
