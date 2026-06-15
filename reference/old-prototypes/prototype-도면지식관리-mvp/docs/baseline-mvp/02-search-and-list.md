# 02 · 검색 + 리스트

좌측 패널(aside, 폭 360px)의 기능. 세 개 컴포넌트 + 한 개 lib 모듈이 관여한다.

| 파일 | 역할 |
|---|---|
| `src/components/SearchBar.tsx` | 검색 입력 (제어 컴포넌트) |
| `src/components/DrawingsList.tsx` | 학제·종류 칩 + 리스트 렌더 |
| `src/lib/search.ts` | Fuse.js 인스턴스 + `searchDocuments()` |
| `src/app/page.tsx` | `filtered` 조합 (검색 + 필터) |

## 1. SearchBar

`src/components/SearchBar.tsx`, 31줄짜리 완전 무상태 제어 컴포넌트.

```tsx
interface Props {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;  // 기본 "도면 제목·내용·학제 검색…"
}
```

왼쪽에 SVG 돋보기 아이콘 하나, input 하나. 포커스 시 `focus:ring-1 focus:ring-slate-500`. debounce 없음 — 문서 8개짜리라 필요 없다.

**한글 IME 주의**: `onChange`는 IME 조합 중에도 발화하지만 Fuse.js는 짧은 prefix에 관대해서 체감 끊김 없음. 만약 수백 건 규모가 되면 `useDeferredValue` 또는 200~300ms debounce 도입 필요.

## 2. DrawingsList

`src/components/DrawingsList.tsx`. 세 영역으로 나뉜다.

### 2.1 학제 칩 (1행)

```
[전체] [전기] [기계] [소방] [시설]
```

- 배열: `const disciplines: (Discipline | "ALL")[] = ["ALL","ELECTRICAL","MECHANICAL","FIRE","FACILITY"]`
- 라벨 매핑은 `disciplineLabels` record 하나에 전부 들어있다.
- 활성 칩은 `bg-slate-800 text-white`, 비활성은 `bg-slate-100 text-slate-600`.
- 단일 선택 — 복수 학제 OR 필터는 범위 밖.

### 2.2 종류 칩 (1행)

```
[모든 종류] [checklist] [code] [drawing] [manual] [spec]
```

- `availableTypes`는 `page.tsx`에서 `Array.from(new Set(documents.map(d => d.type))).sort()`로 계산해 내려준다. 문서가 늘어나면 자동 반영.
- 역시 단일 선택.

### 2.3 리스트

`docs: DocSnippet[]`를 받아 버튼 li로 나열. 각 항목 표시:

```
┌─────────────────────────────────────────┐
│ 데이터센터 냉방 계통도         [기계]    │  ← title + discipline badge
│ 냉동기 2대 (1대 예비) → ...             │  ← snippet (2줄 clamp)
│ DRAWING · p.1 · 2026-03-20              │  ← type / page / last_updated
└─────────────────────────────────────────┘
```

- 학제 뱃지 색: `disciplineStyles` record (전기=amber, 기계=sky, 소방=rose, 시설=emerald).
- 활성 항목은 `bg-sky-50`로 하이라이트.
- 빈 결과일 때: `"결과가 없습니다."`.

## 3. Fuse.js 설정

`src/lib/search.ts` 22줄 전부.

```ts
export const fuse = new Fuse<DocSnippet>(documents, {
  keys: [
    { name: "title",      weight: 0.5 },
    { name: "snippet",    weight: 0.3 },
    { name: "discipline", weight: 0.1 },
    { name: "type",       weight: 0.1 },
  ],
  threshold: 0.4,       // 0=정확 일치만, 1=아무거나
  ignoreLocation: true, // 문자열 내 매칭 위치 무시
  includeScore: true,
});

export function searchDocuments(query: string): DocSnippet[] {
  const q = query.trim();
  if (!q) return documents;                    // 빈 쿼리 = 전체
  return fuse.search(q).map((r) => r.item);    // score는 버림
}
```

### 왜 이 가중치인가
- **title 0.5 / snippet 0.3**: 제목이 가장 강한 신호. 스니펫은 보조.
- **discipline/type 각 0.1**: "전기"라고 입력하면 `discipline="ELECTRICAL"` 문서들이 후보에 들어오도록 최소한 반영. (실제로는 `discipline` 필드가 `"ELECTRICAL"` 문자열이라 "전기" 한글과는 매칭 안 됨 — **현재는 한글 학제 검색이 작동하지 않는 버그/한계**. 한글 검색하려면 `disciplineLabelsKo`를 별도 필드로 인덱싱해야 한다. 07에 TODO 기록.)
- **threshold 0.4**: 오타 1자 정도까지 허용. "냉동기"→"냉동기"만 매칭. "냉장기"도 매칭됨.

### score를 안 쓰는 이유
현재 8건이라 정렬해도 의미 있는 차이가 없다. Fuse의 기본 내부 정렬(score 오름차순) 그대로 사용. 문서 50건+가 되면 `includeScore: true`로 받은 값을 UI에 표시하거나 최소 threshold 필터링에 쓰는 걸 검토.

## 4. `filtered` 합성 (page.tsx)

```tsx
const filtered: DocSnippet[] = useMemo(() => {
  let list = searchDocuments(query);     // Fuse 먼저
  if (discipline !== "ALL") list = list.filter((d) => d.discipline === discipline);
  if (docType !== "ALL")    list = list.filter((d) => d.type === docType);
  return list;
}, [query, discipline, docType]);
```

**순서 중요**: Fuse → discipline → type. Fuse가 먼저라서 "전기" 칩 누르고 "냉동기" 검색하면 전기 학제 문서 중에서 냉동기 매칭이 있는 것만 남는다 (현재 시드에는 그런 교집합 없음 → 빈 리스트).

## 5. 리스트 카운터

좌측 하단 `"{filtered.length} / {documents.length} 건"`. 필터 적용 전후를 한 번에 보여주는 미니 지표. 8/8, 2/8처럼.

## 6. 알려진 한계 / 확장 포인트

| 항목 | 현재 | 확장 방향 |
|---|---|---|
| 한글 학제/종류 검색 | 작동 안 함 (매핑 필드가 영어) | `data-loader`에서 `disciplineKo: "전기"` 파생 필드 주입 후 Fuse 키 추가 |
| 정렬 | Fuse score 또는 JSON 순서 | 날짜/제목 정렬 토글 추가 |
| 복수 학제 | 단일만 | chip을 토글형으로, Set<Discipline>로 |
| 검색어 하이라이트 | 없음 | Fuse `includeMatches` + `<mark>` 래핑 |
| 빈 쿼리 + 필터 | 필터만 적용됨 | OK (의도됨) |
| 문서 수 스케일 | 8건 가정 | 수백 건 이상은 가상 스크롤 필요 |

## 7. 수정 예시: 한글 학제 검색 활성화

`src/lib/data-loader.ts`:
```ts
const disciplineKo: Record<Discipline, string> = {
  ELECTRICAL: "전기", MECHANICAL: "기계", FIRE: "소방", FACILITY: "시설",
};
export const documents: DocSnippet[] = (documentsJson as DocSnippet[])
  .map((d) => ({ ...d, _disciplineKo: disciplineKo[d.discipline] }));
```

`src/lib/search.ts`의 keys에 `{ name: "_disciplineKo", weight: 0.2 }` 추가. 타입 확장도 필요.

이 정도가 `02-search-and-list` 범위에서의 가장 낮은 비용 개선안.
