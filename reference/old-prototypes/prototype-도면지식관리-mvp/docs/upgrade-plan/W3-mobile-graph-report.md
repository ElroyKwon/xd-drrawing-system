# W3 — 모바일·근본원인·보고서 (~36h)

> **선행**: W2 전체 완료
> **후행**: W4 전체

---

## W3-T1. 모바일 브레이크포인트 + 탭 뷰 (~10h)

### 선행
W2-T1

### 신규 파일
- `src/components/shell/MobileTabBar.tsx`
- `src/components/shell/useBreakpoint.ts` (md/lg/sm hook)

### 수정 파일
- `src/app/(s1)/drawings/[id]/page.tsx` — sm: 탭뷰 [리스트|뷰어|사이드], md: 좌 drawer, lg: 3열 그대로
- `src/app/(s1)/search/page.tsx` — sm: 단일 컬럼
- `src/components/shell/AppShell.tsx` — sm 시 SideNav 햄버거 drawer

### 보존 6항목 영향
- **PdfViewer 0 변경**. react-zoom-pan-pinch 핀치줌 자동 적용
- **TransformWrapper doubleClick:disabled 유지** (B-6)

### 브레이크포인트
```css
sm: < 768px   /* 탭 뷰 */
md: 768~1023  /* 좌 drawer */
lg: ≥ 1024    /* 3열 그대로 */
```

### 탭 전환 규약 (스펙 §14.8)
```
리스트 탭 항목 클릭 → 뷰어 탭 자동 활성화
뷰어 → 사이드 탭 수동 전환
사이드 탭 항목 클릭 → 뷰어 탭 + page override
```

### 완료 기준
1. 375×812 뷰포트 (Chrome DevTools) → 탭바 [리스트|뷰어|사이드] 표시
2. 리스트 항목 탭 → 뷰어 탭 자동 활성화
3. 사이드 탭 → EntityToDocs 칩 클릭 → 뷰어 탭 + 페이지 점프
4. 1024px 이상 회귀 0 (3열 그대로)
5. 더블탭 줌 안 일어남 (doubleClick:disabled 유지 확인)

### 위험
- `useBreakpoint` SSR 시 초기값 처리 → useEffect로 hydrated 후 분기 (또는 default desktop)

---

## W3-T2. 근본원인 그래프 (Cytoscape, 1 시나리오) (~8h)

### 선행
W2-T3

### 신규 파일
- `src/app/(s2)/insight/root-cause/[id]/page.tsx`
- `src/components/insight/CytoscapeCanvas.tsx` (cose-bilkent 레이아웃)
- `src/components/insight/CauseCandidateList.tsx`
- `data/insight/root-cause-ahu-3f-01.json` (수동 그래프)

### 데이터 형식
```json
{
  "id": "ahu-3f-01-perf-degradation",
  "focus_node": "AHU-3F-01",
  "nodes": [
    { "id": "CH-001", "label": "냉동기 1호기", "type": "chiller" },
    { "id": "CHWP-001", "label": "냉수 펌프 1호기", "type": "pump" },
    { "id": "AHU-3F-01", "label": "공조기 3F-01", "type": "ahu", "focus": true },
    { "id": "3F-office", "label": "3F 사무실", "type": "space" }
  ],
  "edges": [
    { "source": "CH-001", "target": "CHWP-001", "rel": "supplies" },
    { "source": "CHWP-001", "target": "AHU-3F-01", "rel": "supplies" },
    { "source": "AHU-3F-01", "target": "3F-office", "rel": "serves_space" }
  ],
  "candidates": [
    {
      "rank": 1,
      "cause": "냉수 공급 온도 상승",
      "confidence": 0.78,
      "evidence": [
        { "type": "alarm", "ref": "CHW-T-HI-007" },
        { "type": "drawing_page", "reference": "EE-01-001 p.1", "tag": "CHWP-001" }
      ]
    },
    { "rank": 2, "cause": "팬 벨트 슬립", "confidence": 0.42, ... },
    { "rank": 3, "cause": "급기 필터 막힘", "confidence": 0.31, ... }
  ]
}
```

### CytoscapeCanvas
- `dynamic({ssr:false})` 강제 (Cytoscape는 SSR 불가)
- 레이아웃: `cose-bilkent`
- 노드 클릭 → drawer (속성·최근 알람)
- 노드 우클릭 → "서비스 1 도면으로" → highlight URL

### 완료 기준
1. AnswerCard FollowUpSuggestions의 "근본원인 보기" 클릭 → `/insight/root-cause/ahu-3f-01`
2. 그래프 노드·엣지 표시 + cose-bilkent 자동 배치
3. 후보 1순위 "도면으로" → `/drawings/dwg-elec-001?page=1&highlight=CHWP-001&from=insight&query_id=...`

### 위험
- Cytoscape extension(`cytoscape-cose-bilkent`) 등록 — `cytoscape.use(coseBilkent)` 호출 필요
- 한글 라벨 폰트 → CSS에서 `font-family: "Pretendard Variable"` 명시

---

## W3-T3. 일일 보고서 좌우분할 UI (~10h)

### 선행
W2-T4

### 신규 파일
- `src/app/(s2)/insight/reports/page.tsx` — 목록
- `src/app/(s2)/insight/reports/[id]/page.tsx` — 편집
- `src/components/insight/ReportEditor.tsx`
- `src/components/insight/ReportSection.tsx`
- `data/insight/reports/report-daily-20260417.json`
- `src/app/api/reports/generate/route.ts` (mock 시 3~5초 setTimeout 후 fixed json)
- `src/lib/insight/use-reports-store.ts` (LS 저장 — useAnnotationsStore 패턴 강제 복사)

### 좌우 분할 규약 (스펙 §15.8)
- 좌 (Python 수치): read-only, 편집 불가, "재계산" 버튼만
- 우 (SLM 해석): textarea, 편집 시 `status: draft → reviewed`
- "확정" 버튼 → `status: finalized`. 이후 수정 시 새 revision

### 보고서 샘플 (4 섹션)
```json
{
  "id": "report-daily-20260417",
  "report_type": "daily",
  "period": { "start": "2026-04-17T00:00:00Z", "end": "2026-04-17T23:59:59Z" },
  "status": "draft",
  "sections": [
    {
      "title": "1. 알람 요약",
      "python_data": { "critical": 3, "warning": 14, "avg_resolution_min": 45 },
      "slm_narrative": "냉수 계통 집중. 펌프 1호기 고온 반복 발생. 응축기 점검 권장."
    },
    { "title": "2. KPI", ... },
    { "title": "3. 설비 상태", ... },
    { "title": "4. 내일 주의사항", ... }
  ]
}
```

### useReportsStore 패턴 (B-4 격리)
```ts
const LS_KEY = "dks-reports-v1";  // mvp-annotations-v1과 별도
// hydrated 플래그·loadFromStorage·saveToStorage 패턴 동일 복사
```

### 완료 기준
1. `/insight/reports` → 1건 카드 (오늘자 draft)
2. 편집 진입 → 4 섹션 좌우 분할
3. 우측 편집 → 상태 reviewed
4. 확정 → finalized + 새로고침 후 유지
5. "재생성" → 3~5초 토스트 → 동일 응답
6. localStorage `dks-reports-v1` 확인

### 위험
- 두 LS hook 공존(`mvp-annotations-v1`, `dks-reports-v1`) — 키 충돌 없음 확인

---

## W3-T4. 주석 회귀 점검 (모바일 포함) (~4h)

### 선행
W3-T1

### 신규 파일
- `src/__tests__/regression-annotations.test.ts` (vitest 단위)

### 검증 (수정 0, 검증만)
1. 데스크톱 1920×1013: 핀 생성·편집·삭제 회귀 0
2. 모바일 375×812: 뷰어 탭에서 더블탭 줌 안 일어남, 단탭으로 핀 생성 가능
3. localStorage `mvp-annotations-v1` — 기존 핀 보존

### vitest 단위 5 케이스
- addAnnotation: ID·created_at 자동 생성
- updateAnnotation: 부분 patch 정상
- deleteAnnotation: 1건 제거
- hydrated 플래그: 첫 렌더에서 false → useEffect 후 true
- LS 시드 없을 때 빈 배열 반환

### 완료 기준
1. 데스크톱·모바일 모두 핀 CRUD 정상
2. `vitest run regression-annotations` 5 케이스 통과
3. localStorage 회귀 0

---

## W3-T5. Insight Home + Bell 카운트 (~4h)

### 선행
W2-T2, W3-T3

### 수정/신규 파일
- 수정: `src/components/shell/Header.tsx` — NotificationBell이 알람 unread critical 카운트
- 신규: `src/components/shell/NotificationBell.tsx`
- 신규: `src/lib/insight/use-alarm-stream.ts` (4주는 가상 — JSON 기반 카운트만)
- 수정: `src/app/(s2)/insight/page.tsx` — RecentAlarmsWidget(상위 3건), RecentQueriesWidget(LS 최근 5), SuggestedQuestions(고정 5)

### use-alarm-stream
- 4주 MVP: setInterval 시뮬 OFF default
- 카운트 = critical 알람 미해결 개수 (alarms-fixed.json에서 계산)
- live 모드는 Phase 2

### 완료 기준
1. 어느 화면이든 헤더 종 아이콘에 빨간 배지 "3" (critical 미해결)
2. 클릭 → `/insight/alarms`
3. `/insight` Home 진입 시 3 위젯 모두 데이터

### 위험
- LS의 최근 쿼리 (RecentQueriesWidget) — 빈 LS일 때 placeholder
