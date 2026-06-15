# W1 — 인프라·시드·앱 쉘 (~30h)

> **선행**: 없음 (W1 시작점)
> **후행**: W2-T1, W2-T2 모두 W1 완료 의존
> **병렬 가능**: W1-T5 (AppShell)는 W1-T2/T3 (시드)와 병렬

---

## W1-T1. 의존성·환경 세팅 (~2h)

### 신규/수정 파일
- 수정: `package.json` (deps 추가, scripts 보강)
- 수정: `next.config.mjs` (필요 시)
- 신규: `.env.local.example` (NEXT_PUBLIC_LLM_MODE 등)
- 신규: `vitest.config.ts`

### 추가 deps
```
npm i tsx js-yaml @anthropic-ai/sdk cytoscape cytoscape-cose-bilkent react-markdown remark-gfm
npm i -D @types/js-yaml vitest
```

### scripts 추가
```json
"seed:dwg": "tsx scripts/convert-dwg.ts",
"seed:cheongju": "tsx scripts/convert-cheongju.ts",
"seed": "npm run seed:dwg",
"test": "vitest run"
```

### .env.local.example
```
NEXT_PUBLIC_LLM_MODE=mock
ANTHROPIC_API_KEY=
LLM_REPORT_MODEL=claude-sonnet-4-6
LLM_ALARM_MODEL=claude-haiku-4-5-20251001
```

### 완료 기준
1. `npm i` 무에러
2. `npm run dev` 부팅 + `/` 시나리오 A·B·C 회귀 0
3. `npx tsc --noEmit` 통과
4. `npm run lint` 통과

### 위험
- pdfjs-dist + react-pdf 버전 충돌 → 그대로 두기 (이미 동작 검증)
- 한글 경로(`prototype-도면지식관리-mvp`)에서 tsx 실행 시 인코딩 문제 → cross-env 또는 PowerShell UTF-8 모드 검토

---

## W1-T2. 시드 변환 스크립트 골격 (~6h)

### 선행
W1-T1

### 신규 파일
- `scripts/convert-dwg.ts` (옵션 B 본체)
- `scripts/convert-cheongju.ts` (옵션 A 스텁 — yaml 부재 감지 시 친화적 에러)
- `scripts/lib/drawing-meta.ts` (파일명 패턴 → discipline·drawing_number·drawing_type 매핑)
- `scripts/manual-mappings/dwg-selection.yaml` (18개 화이트리스트, 빈 파일로 시작)
- `scripts/manual-mappings/dwg-entity-map.yaml` (도면 × 5~15 태그, 빈 파일로 시작)

### 책임 분담
- `convert-dwg.ts`:
  - 입력: `dwg/` 폴더 스캔 + selection.yaml 화이트리스트 + entity-map.yaml
  - 출력: `data/drawings.json` (18건 신규), `data/entities.json` (신규), `data/doc-entity-links.json` (확장 — 기존 8건 보존 + 18×10 추가)
- `scripts/lib/drawing-meta.ts`:
  - `parseFileName(name): { discipline, drawing_number, title }` (정규식 매핑)
  - 정규식: `/^EE-(\d{2})-(\d{3})_(.+)\.pdf$/i` → ELECTRICAL, EE-XX-XXX
  - `/^ET-(\d{2})-(\d{3})_(.+)\.pdf$/i` → 통신 (ELECTRICAL로 매핑 또는 별도 카테고리)
  - `/^\[LS ELECTRIC.*?\]\s*\d+\.\s*(.+)\.pdf$/` → discipline 매핑 테이블

### 출력 스키마 (옵션 A·B 공통)
```ts
{
  drawings: Drawing[],
  entities: Entity[],
  links: DocEntityLink[]
}
```

### 완료 기준
1. `npm run seed:dwg` 실행 → `data/drawings.json`(8 + 18 = 26건), `data/entities.json` 생성
2. `npm run seed:cheongju` 실행 시 "yaml not found at projects/청주/... — see docs/upgrade-plan/00-decisions.md §2" 메시지 + exit 1
3. `data/doc-entity-links.json`의 entity_tag가 모두 대문자
4. 기존 8 도면 doc_id 충돌 없음 (신규는 `dwg-elec-001` 등 prefix)

### 위험
- 한글 폴더명(`1) 전기공사`) Windows path encoding → Node.js 직접 fs.readdirSync 시 정상 처리 확인
- 파일명에 공백·특수문자 → JSON 출력 시 그대로 보존, URL 인코딩은 Next.js 라우터 단계에서 처리

---

## W1-T3. 18 PDF 복사 + 수동 entity 매핑 (~8h)

### 선행
W1-T2

### 신규 파일
- `public/drawings/dwg/` 18개 PDF
- `scripts/manual-mappings/dwg-selection.yaml` 채우기
- `scripts/manual-mappings/dwg-entity-map.yaml` 채우기

### 18 PDF 선정 가이드 (페르소나 빈도 가중)
**전기 9**:
- EE-01-001 22.9kV 수전 단선결선도
- EE-01-006 R-Center 단선도
- EE-01-013 동력결선도
- EE-01-016 분전반결선도
- EE-02-003 전기 평면도
- EE-03-003 전등 평면도
- EE-04-001 전열 평면도
- EE-05-002 접지 평면도
- EE-00-002 범례·약어

**통신 5**:
- ET-00-001 통신 도면목록
- ET-01-001 통신 단선도
- ET-01-003 광케이블 결선도
- ET-02-001 통신 평면도
- ET-03-001 보안 평면도

**건축/기계/소방 4**:
- LSE-건축
- LSE-기계
- LSE-기계소방
- LSE-전기소방

### 수동 매핑 작성 형식
```yaml
# scripts/manual-mappings/dwg-entity-map.yaml
- doc_id: dwg-elec-001
  drawing_number: EE-01-001
  title: 22.9kV 수전설비 단선결선도
  entities:
    - { tag: KEPCO-IN, page: 1 }
    - { tag: VCB-001, page: 1 }
    - { tag: TR-001, page: 1 }
    - { tag: ACB-001, page: 1 }
    - { tag: BUS-A, page: 1 }
```
18 도면 × 평균 10 태그 = 180 줄 수동. 도면 1개당 평균 13분. 합계 약 4h.

### 완료 기준
1. 18 PDF 모두 `public/drawings/dwg/` 복사 (총 ~100MB, git LFS 검토)
2. `npm run seed:dwg` 재실행 → 18 도면 정상 산출
3. `next dev`에서 18 PDF 모두 react-pdf 렌더 성공
4. EntityToDocs에서 `VCB-001` 검색 → 1+개 도면 매칭
5. 각 도면 평균 페이지 수 1~5 확인

### 위험
- PDF 합계 약 100MB → git에 커밋 시 LFS 검토 또는 .gitignore + README에 다운로드 안내
- pdfjs-dist 워커가 큰 PDF (39MB arch.pdf 등) 렌더 시 메모리 → 18개에 포함 X

---

## W1-T4. disciplineKo 파생 필드 + Fuse 키 추가 (~2h)

### 선행
W1-T2 (시드가 있어야 검증 가능)

### 수정 파일
- `src/lib/types.ts`: `DocSnippet`에 이미 있는 `disciplineKo?` 활용 (없으면 추가)
- `src/lib/data-loader.ts`: 파생 필드 매핑 (IIFE 인덱스 빌드 패턴 유지)
- `src/lib/search.ts`: Fuse keys 확장 (기존 가중치 보존)

### data-loader 변경
```ts
const koMap: Record<Discipline, string> = {
  ELECTRICAL: "전기",
  MECHANICAL: "기계",
  FIRE: "소방",
  FACILITY: "시설",
  // 통신은 ELECTRICAL로 통합 또는 별도 추가
};
export const documents: DocSnippet[] = (documentsJson as DocSnippet[])
  .map(d => ({ ...d, disciplineKo: koMap[d.discipline] }));
```

### search.ts 변경 (가중치 추가만, 기존 보존)
```ts
keys: [
  { name: "title", weight: 0.5 },         // 기존
  { name: "snippet", weight: 0.3 },       // 기존
  { name: "discipline", weight: 0.1 },    // 기존
  { name: "type", weight: 0.1 },          // 기존
  { name: "disciplineKo", weight: 0.15 }, // 신규
  { name: "drawing_number", weight: 0.2 }, // 신규
  { name: "location", weight: 0.1 },      // 신규
],
```

### 완료 기준
1. 한글 검색: "전기" → 9건, "통신" → 5건, "기계" → 1+건
2. 도면번호 검색: "EE-01" → 9건 매칭
3. 영문 회귀: "냉동기" 결과 동일
4. `npx tsc --noEmit` 통과

### 위험
- discipline 매핑에 통신 누락 → koMap에 추가 또는 dwg-elec과 통합

---

## W1-T5. 라우트 그룹 + AppShell 골격 (~8h)

### 선행
W1-T1 (병렬: T2/T3와 동시 진행 가능)

### 신규 파일
- `src/app/(s1)/layout.tsx` — s1 그룹 레이아웃
- `src/app/(s1)/page.tsx` — 현 page.tsx 거의 그대로 이전
- `src/app/(s2)/layout.tsx`
- `src/app/(s2)/insight/page.tsx` — 홈 placeholder
- `src/components/shell/AppShell.tsx`
- `src/components/shell/Header.tsx`
- `src/components/shell/SideNav.tsx`
- `src/lib/nav.ts`

### 수정 파일
- `src/app/layout.tsx` — body wrapping 유지 (AppShell은 그룹별 layout에서 wrap)
- `src/app/globals.css` — 필요 시 토큰 추가
- `src/app/page.tsx` — `redirect('/(s1)')` 또는 보존 (사용자 결정 사안 — 보수적으로 유지)

### 책임 분담
- `AppShell({children, service})` — header + sidenav + main grid
- `SideNav({active})` — `nav.ts` 항목 렌더, "협력업체 브리핑/유사사례/인수인계" disabled
- `Header({active})` — GlobalSearchBar(탭만, Enter 동작은 W2) + NotificationBell(badge 0 고정) + Profile placeholder

### nav.ts 항목
```ts
export const NAV_ITEMS = [
  { id: "home-s1", label: "홈", href: "/", group: "s1" },
  { id: "search", label: "검색", href: "/search", group: "s1" },
  { id: "upload", label: "업로드", href: "/upload", group: "s1", disabled: true },
  { id: "insight-home", label: "인사이트", href: "/insight", group: "s2" },
  { id: "alarms", label: "알람", href: "/insight/alarms", group: "s2" },
  { id: "reports", label: "보고서", href: "/insight/reports", group: "s2" },
  { id: "settings", label: "설정", href: "/settings", group: "common", disabled: true },
] as const;
```

### 완료 기준
1. `/` 진입 → 기존 3열 레이아웃 정상 (회귀 0)
2. `/insight` 진입 → AppShell 동일, 본문 placeholder ("Insight Home — 1주차 placeholder")
3. SideNav에서 `/` ↔ `/insight` 이동 부드러움. activate 표시 정상
4. `npm run lint` + `npx tsc --noEmit` 통과

### 위험
- 라우트 그룹 `(s1)` 도입 시 기존 `/` URL이 `(s1)/page.tsx`로 매핑되는지 확인
- root `layout.tsx`와 `(s1)/layout.tsx`의 중복 wrapping 주의

---

## W1-T6. 인터뷰 일정 확정 (~4h, 사용자 작업)

### 선행
없음 (병렬)

### 산출물
`docs/upgrade-plan/interview-guide.md` 1차 작성 + 사내 캘린더 4명 × 90분 확정

### Day-by-day
- **W1 월**: 후보 4명 식별 (영업 2 + 운영자 2). 컨택 메일 발송
- **W1 수**: 슬롯 확정 + 캘린더 초대 + Zoom/Teams 링크
- **W1 금**: interview-guide.md 1차 완성. 시연 환경(노트북·인터넷·녹화) 체크. 사전 dry-run 1회

### 완료 기준
1. 캘린더에 4명 × 90분 확정
2. interview-guide.md 1장 (시연 스크립트 + 질문지 §10 통합)
3. 녹화 도구(OBS·Loom) 설치 + 테스트 녹화 1분
