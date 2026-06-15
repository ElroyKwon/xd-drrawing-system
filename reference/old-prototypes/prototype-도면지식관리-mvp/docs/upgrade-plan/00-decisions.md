# 00 — 결정사항 + 옵션 A/B + 보존 6항목

## 1. 4개 핵심 결정 (착수 전 사용자 승인 권장)

### D-1. 기존 레포 확장 (신규 X)
- **결정**: `D:\_Project\prototype-도면지식관리-mvp` 그대로 확장
- **근거**: 보존 6항목(아래 §3)이 동작 검증된 코드. 신규 시 동일 코드 재구현 + 회귀 위험.
- **영향**: AppShell 분해는 기존 page.tsx의 state 분리 리팩토링 (큰 수술 X).

### D-2. 단일 Next.js 앱 + 라우트 그룹 (모노레포 X)
- **결정**: `src/app/(s1)/...` `src/app/(s2)/insight/...`
- **근거**: 스펙 §15.9가 AppShell·Header·SideNav·URL·테마·세션 전부 공유로 명시. 분리 시 인증 동기화 + CORS + iframe 부담이 4주 MVP에 과투자.
- **영향**: 빌드 산출물 단일. 두 서비스 자유 이동.

### D-3. LLM 단계적 활성화 (mock → live)
- **결정**: 1주차 모킹 100% / 2주차 보고서 Claude Sonnet / 3주차 알람 Claude Haiku
- **근거**: 스펙 §7.2 권장. 비용 무시 가능 (인터뷰 4명 × 수십 쿼리). 로컬 모델은 vRAM·세팅 시간으로 4주 MVP 부적합.
- **영향**: `NEXT_PUBLIC_LLM_MODE = "mock" | "live"` 환경변수로 단일 진입점 토글 (`src/lib/insight/llm-client.ts`).

### D-4. SSE 스트리밍 (WebSocket X)
- **결정**: SSE 일원화
- **근거**: 답변 토큰·알람 푸시 모두 단방향. Next.js App Router/Edge Runtime에서 SSE 1급 지원. WebSocket의 인증·재연결·heartbeat 부담 회피.
- **영향**: `app/api/insights/ask/stream/route.ts` Edge Runtime + 클라 `EventSource` 또는 `fetch + ReadableStream`.

---

## 2. 청주 YAML 부재 → 옵션 A/B 분기

### 차단 발견
스펙 §14.7: `projects/청주/phase0_v2_0/ontology_readiness/entity_details/*.yaml` (283 태그) → 시드 변환.
**탐색 결과 0건.** `D:/_Project/`, sibling 프로젝트, 모든 부모 경로 검색했으나 yaml 부재.

### 발견 대체
`D:\_Project\prototype-도면지식관리-mvp\dwg\` 79개 실 PDF (총 434MB):
- 전기 40개 (`EE-XX-XXX_*`)
- 건축 9개 (`[LS ELECTRIC R-Center 구축] N. *`)
- 통신 다수 (`ET-XX-XXX_*`)

### 옵션 비교

| 단계 | 옵션 A (yaml 도착) | 옵션 B (default, dwg 79개) |
|------|--------------------|---------------------------|
| 도면 메타 | yaml 100% 자동 | 파일명 정규식 95% + 수동 5% |
| discipline | yaml 자동 | prefix(EE/ET/LSE) 매핑 자동 |
| revision/location | yaml 자동 | 부재 → 수동 |
| entity_tag 매핑 | 283 태그 전수 자동 | 수동 100% (18 도면 × 평균 10 = 180 줄, 약 4h) |
| 관계 (supplies 등) | yaml 자동 | 근본원인 그래프 1건 수동 (W3-T2) |

### 결정
**옵션 B로 1주차 시작.** 청주 yaml이 W2 안에 도착하면 W3 초에 옵션 A로 전환. 도착 안 하면 옵션 B로 4주 완주. 인터뷰 4명에겐 18×180으로 충분 (시나리오 1·2·4·5 모두 시연 가능).

### 전환 비용
청주 yaml 도착 시: `npm run seed:cheongju` → 시드 JSON 덮어쓰기 → PDF 폴더 복사. UI 코드 0 변경. 약 2~4h.

### 코드 격리
두 변환 진입점:
- `scripts/convert-dwg.ts` (옵션 B, default)
- `scripts/convert-cheongju.ts` (옵션 A, yaml 부재 시 친화적 에러)

둘 다 동일 출력 스키마(`Drawing | Entity | DocEntityLink`). 상위 npm script 한 줄만 교체하여 전환.

---

## 3. 보존 6항목 (변경 절대 금지)

`docs/baseline-mvp/07-quirks-and-todo.md §4` 명시. 위반 시 **즉시 정지하고 사용자 협의**.

### B-1. `src/components/PdfViewer.tsx` (235줄)
- **pickMode 줄 29-35**: PDF→이미지→empty 순서. 바꾸면 실 PDF 있는데도 이미지가 먼저 뜸.
- **key 패턴 줄 118**: `${doc.doc_id}-${pageNumber}-${mode}`. 줌 초기화/상태 리셋 보장. 제거 시 totalPages 잔존 버그.
- **handleSurfaceClick 줄 54-61**: 정규화 좌표 (x, y: 0~1).

### B-2. `src/components/AnnotationLayer.tsx` (55줄)
- 컨테이너 `pointer-events-none` (줄 28) + 버튼 `pointer-events-auto` (줄 43)
- `e.stopPropagation()` (줄 40)
- 핀 하단중앙 정렬: `left = a.x * width, top = a.y * height` (줄 33-34)

### B-3. `src/components/AnnotationPopover.tsx` (179줄)
- create/edit 모드 분기 (줄 72-76)
- Escape 닫기
- 빈 텍스트 disabled

### B-4. `src/lib/annotations-store.ts` (73줄)
- `hydrated` 플래그 (useState 줄 33, useEffect 줄 38)
- 제거 시 첫 렌더에서 빈 배열을 LS에 써서 기존 주석 날아감
- LS_KEY="mvp-annotations-v1" (줄 7)

### B-5. `src/lib/data-loader.ts` (39줄)
- `tagToDocsIdx` IIFE 빌드 패턴 (줄 14-22)
- `entity_tag.toUpperCase()` 정규화 (줄 17)
- 새 인덱스도 동일 패턴 따라야 함

### B-6. `TransformWrapper`의 `doubleClick:{disabled:true}`
- `PdfViewer.tsx` 내부. 풀면 더블클릭 줌이 주석 더블클릭 흡수
- 모바일 핀치줌은 react-zoom-pan-pinch 기본 자동 지원 (별도 설정 불필요)

### 격리 패턴

**HighlightOverlay (W2-T1)**:
```tsx
// PdfViewer 내부 수정 X. renderOverlay slot 합성:
<PdfViewer
  doc={doc}
  pageOverride={page}
  renderOverlay={(s) => (
    <>
      <AnnotationLayer ... />
      <HighlightOverlay highlight={tag} surface={s} />
    </>
  )}
/>
```

**새 LocalStorage hook (W3-T3 useReportsStore)**:
```ts
// useAnnotationsStore의 hydrated 패턴 강제 복사
const [items, setItems] = useState(seed);
const [hydrated, setHydrated] = useState(false);
useEffect(() => {
  const fromLs = loadFromStorage();
  if (fromLs) setItems(fromLs);
  setHydrated(true);
}, []);
useEffect(() => {
  if (hydrated) saveToStorage(items);
}, [items, hydrated]);
```

**시드 변환 출력 (W1-T2)**:
```ts
// scripts/convert-dwg.ts 출력 단계
links.push({
  doc_id,
  entity_tag: rawTag.toUpperCase(),  // 강제 정규화
  page,
});
```
