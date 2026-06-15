# 비기능 요구사항 (NFR)

**문서 유형**: 최상위 참조 문서
**분량**: 2~3페이지
**목적**: 두 트랙(Insight Lab · Design Lab)에 공통으로 적용되는 성능·접근성·보안·다국어·데이터 정합성·감시 기준을 한 곳에 정리

---

## 0. 이 문서를 읽기 전에

이 NFR은 **목업 단계의 기준선**입니다. 숫자 목표는 실 운영 환경·실 도면 수백~수천 건 규모에서 다시 검증되어야 합니다. 각 항목은 **현재 목업에서 확인된 값**과 **실 서비스 도입 시 제안 목표**를 구분해 기술합니다.

각 섹션의 말미에 간단한 **스스로 본 보완 포인트**가 있고, 문서 맨 아래 §7에 **이해관계자 의견 기록란**을 비워두었습니다.

---

## 1. 성능

### 1.1 첫 화면 TTI (Time To Interactive)

| 화면 | 목업 관측값(로컬 dev) | 실 서비스 제안 목표 | 비고 |
|---|---|---|---|
| `/insight` 허브 | ~1.0~1.4초 | ≤ 1.5초 (프로덕션 build 기준) | 시드 JSON 3종 import, SSR 친화 |
| `/insight/alarms` | ~0.9~1.2초 | ≤ 1.5초 | 리스트 렌더, 썸네일 없음 |
| `/insight/answers/[id]` | ~1.1~1.5초 | ≤ 2.0초 | ChatPanel + 근거 카드 동시 |
| `/insight/lab` | ~1.3~1.8초 | ≤ 2.5초 | Bundle 렌더 + 차트 초기 paint |
| `/design-lab/cards` | ~1.2~1.6초 | ≤ 2.0초 | 26카드 그리드 + 썸네일 lazy |
| `/design-lab/chat` | ~1.0~1.4초 | ≤ 2.0초 | 3분할 레이아웃, 챗 1-턴 시드 |

### 1.2 대형 PDF 렌더

- **대상**: 프로덕션 도면 뷰어(`PdfViewer.tsx`). A0 사이즈·멀티 페이지 PDF
- **현재**: `public/drawings/*.pdf`가 16~18 bytes 더미이므로 실 측정 없음. 이미지 fallback(PNG) 기준 1초 내 렌더
- **제안 목표**: 10MB 이하 PDF는 첫 페이지 ≤ 2초, 페이지 전환 ≤ 500ms
- **전략**: react-pdf의 페이지 lazy 렌더 + `zoom-pan-pinch`의 변환 레이어 분리 유지. PDF 파서는 이미 Web Worker(`pdf.worker.min.mjs`)로 격리됨

### 1.3 카드 그리드 26건 렌더

- **대상**: `/design-lab/cards` 중앙 그리드
- **현재**: 썸네일 26장 동시 노출 시 CLS(Cumulative Layout Shift) ≤ 0.05, LCP ≈ 1.2초 (로컬)
- **제안 목표**: 500건 기준 가상 스크롤(virtualization) 도입 시 TTI ≤ 2.5초
- **주의**: 실 서비스에서 도면이 수백 건으로 늘어날 경우 **가상 스크롤 또는 페이지네이션** 필요. 현재 목업은 전량 DOM 렌더

### 1.4 대화 스트림 지연

| 상황 | 현재 동작 | 제안 목표 |
|---|---|---|
| Design Lab 챗 (시드 응답) | 600~1200ms 고정 지연 | 유지 (데모 안정성) |
| Insight Lab 챗 (실 Gemini 호출 일부) | 첫 토큰 ~1.5~3초, 완료 ~8~15초 | 첫 토큰 ≤ 2초, 완료 ≤ 10초 |
| 스트리밍 방식 | 미구현(전량 수신 후 표출) | SSE/fetch stream 도입 권장 |

### 1.5 스스로 본 보완 포인트

- 실 프로덕션 빌드(`next build` + `next start`) 기준 수치 재측정 필요
- Gemini API 라우팅 실패 시 fallback 시간이 길어질 가능성 — timeout·retry 정책 합의 필요
- 카드 그리드 500건+ 스케일 검증 미실시

---

## 2. 접근성 (A11y)

### 2.1 장갑 착용 현장을 위한 48×48 최소 히트박스

현장 작업자는 **안전장갑·내화장갑을 착용한 상태**로 태블릿을 조작할 수 있습니다. Apple HIG·Material Design의 권장 44pt보다 한 단계 더 확장한 **48×48 CSS 픽셀**을 최소 탭 타깃으로 삼습니다.

구현은 `src/app/globals.css`의 `.tap-target` 유틸리티입니다. 시각 크기는 유지하고 `::before` 투명 영역으로 탭 면적만 확장합니다.

```css
@layer utilities {
  .tap-target { position: relative; }
  .tap-target::before {
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    width: max(48px, 100%);
    height: max(48px, 100%);
    transform: translate(-50%, -50%);
    z-index: -1;
  }
}
```

- **적용 위치**: 허브의 카드 진입, 알람 목록 항목, 보고서 목록 항목, 근본원인 그래프 노드, 카드 그리드 카드, 챗 입력 전송 버튼
- **검증 방법**: DevTools Rendering 패널의 "Emulate CSS prefers-reduced-motion" 대신 `outline: 1px solid rgba(255,0,0,0.3)` 임시 적용으로 가시화해 수동 확인

### 2.2 키보드 네비게이션

| 화면 요소 | 현재 지원 | 개선 필요 |
|---|---|---|
| 네비게이션(SideNav/LabNav) 링크 | `Tab` 포커스 + `Enter` | 포커스 링 명시적 스타일링 부족 |
| 카드 그리드 카드 선택 | `Tab` + `Enter` 가능 | 화살표 이동(grid roving tabindex) 미구현 |
| 챗 입력 | `Enter` 전송, `Shift+Enter` 줄바꿈 | 표준 |
| 주석 팝오버 | `Esc` 닫기 | 포커스 트랩 미검증 |
| 탭(인스펙터 6탭) | `Tab` 이동 가능 | ARIA `role="tablist"`·`aria-selected` 미부여 |

- **제안 목표**: WCAG 2.1 AA 수준. 모든 대화형 요소는 키보드만으로 도달·조작 가능
- **가장 시급**: 포커스 링 일관화, 탭 컨테이너 ARIA 속성

### 2.3 색상 대비

- 본문 텍스트: `text-slate-700` (#334155) on `bg-white` (#FFFFFF) → 대비율 10.3:1 (WCAG AA 통과)
- 보조 텍스트: `text-slate-500` (#64748B) on `bg-white` → 대비율 4.8:1 (AA 통과)
- Severity 색(로즈/앰버/스카이): 색점 옆 **항상 한글 라벨 동반** — 색맹 사용자에도 정보 손실 없음
- 다크 모드(Foundation 트랙만): `color: #e2e8f0` on `#0b1220` → 대비율 13:1 (AAA 통과)

**주의**: 앰버 `amber-400` (#FBBF24) 위에 흰 글씨를 올릴 경우 대비가 낮음 — 현재는 앰버 위에 검은 텍스트만 사용

### 2.4 스스로 본 보완 포인트

- `.tap-target` 유틸리티 적용 범위가 산발적 — audit 필요
- 스크린 리더 대응(ARIA label·live region) 미실시. Insight Lab 챗의 assistant 메시지는 `aria-live="polite"` 필요
- 다크 모드가 Foundation 트랙에만 있어 **Insight Lab·Design Lab 야간 작업 환경에서의 눈부심** 검증 안 됨

---

## 3. 보안·권한

### 3.1 도면 열람 권한 (예상 모델)

현재 목업은 **권한 없이 모든 도면을 열람**합니다. 실 서비스 도입 시 제안하는 권한 모델은 다음과 같습니다.

| 권한 축 | 설명 | 구현 예 |
|---|---|---|
| **공종(discipline) 기반** | 전기 담당자는 전기·공통만, 기계 담당자는 기계·공통만 | `user.disciplines = ['ee', 'common']` ↔ `doc.discipline` |
| **지역(location) 기반** | 담당 플랜트·층·공정 | `user.locations = ['plant-a', 'fl-3']` ↔ `doc.location` |
| **민감도(sensitivity)** | 공개·사내·기밀 | `doc.sensitivity: 'internal' \| 'confidential'` |
| **개정 이력(revision)** | 최신만 보는 일반 사용자 vs 이력 전체를 보는 관리자 | `user.role === 'admin'` 시 이전 REV 노출 |

**주의**: 현재 `data/documents.json` 스키마에는 `location`·`sensitivity` 필드가 선언만 되어 있고 값은 채워지지 않음. CLAUDE.md §6-2 참조.

### 3.2 주석 편집 권한

- **생성**: 로그인 사용자 누구나
- **편집·삭제**: 본인이 작성한 주석만 (본인 판단). 관리자는 전부 가능
- **현재 목업**: 인증 없음, 전부 로컬스토리지(`mvp-annotations-v1`). 실 서비스 전환 시 **서버 저장 + 주석별 `author_id` + 편집 시 토큰 검증** 필요

### 3.3 API 토큰 관리

- **Gemini API 키**: 현재 `.env.local`의 `GEMINI_API_KEY`로 주입, 서버 사이드에서만 사용 (`src/lib/insight/llm-client.ts`). 클라이언트 번들에 절대 노출되지 않음 확인 필요 (`next.config.js`의 `env` 대신 `process.env` 직접 참조)
- **회전 정책**: 제안 — 3개월 회전, 유출 의심 시 즉시 폐기·재발급
- **감사 로그**: 제안 — 호출 주체·도면 ID·프롬프트 해시를 서버 로그에 보관, 프롬프트 원문은 저장하지 않음 (민감 정보 유출 방지)

### 3.4 스스로 본 보완 포인트

- 권한 모델은 **아직 합의 전**. 조직의 기존 권한 체계(AD·LDAP·SSO) 연동 요건 조사 필요
- 주석 `author_id` 필드가 타입에만 있고 인증 경로 없음
- 프롬프트에 도면 텍스트가 포함될 경우 **LLM 공급사에 어디까지 전달되는지** 데이터 거버넌스 확인 필요

---

## 4. 다국어·다크모드

### 4.1 다국어

- **현재**: **한국어 단일**. 모든 UI 문자열 하드코딩 (Insight Lab / Design Lab 모두)
- **제안 목표**:
  - 단기 — 유지 (고객사가 한국어 사용)
  - 중기 — i18n 키 추출(`next-intl` 또는 `react-intl`)해 영어 추가 (해외 법인 대비)
  - 장기 — 기술 용어의 국제 표기(IEC 기호·ISO 분류)는 원어 유지, UI 라벨만 번역
- **주의**: 도면 번호(`EE-01-001`)·엔티티 ID(`VCB-001`)·보고서 템플릿 헤더는 번역 대상 아님

### 4.2 다크모드

- **현재**: **Foundation 트랙(S3)에만 지원** (`html.dark` 토글). `globals.css` 주석 참조: "도면 배경(bg-white)은 의도적으로 유지해 원본 가독성 보장. UI 크롬만 전환"
- **Insight Lab · Design Lab**: 라이트 톤 고정. 보고서 인쇄 친화성과 시각 비교의 일관성 때문
- **제안**: 확장 시 고려사항
  - 도면 원본 이미지는 항상 흰 배경 유지 (CAD 관행)
  - 다크 모드에서 Severity 색은 채도를 한 단계 낮춘 변형 사용(로즈-400·앰버-300·스카이-300)
  - 보고서 편집 화면은 인쇄 시 다크 모드와 무관하게 흰 배경으로 렌더

### 4.3 스스로 본 보완 포인트

- 다국어 도입 결정 시 **일본어·중국어 관련 폰트(Pretendard 이외 fallback)** 검증 필요
- 다크 모드 Insight Lab 확장은 **대화 메시지 말풍선 색** 전면 재설계가 필요 — 현재 검은 말풍선은 다크 모드에서 가독성 저하

---

## 5. 데이터 정합성

### 5.1 보존 6항목 회피 원칙 (절대 원칙)

프로덕션의 6개 항목은 **어떤 트랙에서도 직접 수정·래핑·우회하지 않습니다**.

| # | 항목 | 역할 |
|---|---|---|
| 1 | `src/components/PdfViewer.tsx` | PDF·이미지 자동 분기 뷰어 |
| 2 | `src/components/AnnotationLayer.tsx` | 0-1 정규화 좌표 핀 오버레이 |
| 3 | `src/components/AnnotationPopover.tsx` | 주석 생성·편집·삭제 |
| 4 | `src/components/AnnotationList.tsx` | 주석 목록 사이드 패널 |
| 5 | `src/components/EntityToDocs.tsx` | 엔티티→도면 역추적 |
| 6 | `src/lib/annotations-store.ts` (useAnnotationsStore) | 주석 localStorage 영속 |

- **근거 문서**: `D:\_Project\prototype-도면지식관리-mvp\docs\baseline-mvp\07-quirks-and-todo.md §4`
- **충돌 발견 시**: 즉시 정지·격리 패턴 — 새로운 컴포넌트를 sibling으로 만들고 보존 항목을 호출만 함
- **Design Lab 준수**: 별도 컴포넌트(`src/components/design-lab/*`)와 별도 메타(`src/lib/design-lab/mock-meta.ts`)만 사용 (보존 항목에 의존성 없음 확인됨)

### 5.2 LocalStorage 키

| 키 | 용도 | 위치 |
|---|---|---|
| `mvp-annotations-v1` | 주석 영속 (프로덕션 유일 소스) | `src/lib/annotations-store.ts` |
| `dks-theme` | 테마 토글 (Foundation 트랙) | `html.dark` 클래스 토글 |

- **정합성 원칙**: 주석 시드(`data/annotations.json`)는 초기값. LocalStorage에 값이 있으면 **LocalStorage 우선**
- **주의**: 브라우저 변경·클린 시 주석 유실. 실 서비스에서는 **서버 저장 + 로컬 캐시 2-tier** 필요

### 5.3 데이터 소스의 층위

```
data/ (원천)
├── documents.json           ← 8건 도면 메타 (드로잉 26건으로 확장됨: data/drawings.json)
├── drawings.json            ← 26건 (Design Lab이 쓰는 전체 세트)
├── annotations.json         ← 주석 시드 (빈 [])
├── doc-entity-links.json    ← 도면-엔티티 링크
└── insight/reports/*.json   ← 일일 보고서 시드

src/lib/ (파생)
├── insight/mock-responses.ts   ← AI 시드 응답
└── design-lab/mock-meta.ts     ← 목적·대화요약·온톨로지 메타
```

원천 JSON은 **단일 진실 소스(single source of truth)**입니다. 파생 메타를 원천에 다시 써 넣지 않습니다.

### 5.4 스스로 본 보완 포인트

- `data/documents.json` ↔ `data/drawings.json`의 관계·중복 여부 정리 미완. 장기적으로 단일화 필요
- 주석의 서버 동기화 설계 미실시 — Insight Lab에서 참조 도면의 주석을 실시간으로 가져오는 경로 필요 시 재설계

---

## 6. 감시·모니터링

### 6.1 에러 로깅

- **현재**: `console.error`만 사용. 목업 단계 상용 APM 미도입
- **제안 목표**:
  - 클라이언트 에러 — Sentry 또는 자체 `/api/log-error` 엔드포인트
  - 서버(API route) 에러 — 구조화 로그(JSON) + 외부 로그 수집기(예: Loki·CloudWatch)
  - 치명 에러(뷰어 렌더 실패·주석 저장 실패) 발생 시 **사용자에게 toast 표시 + 재시도 CTA**

### 6.2 성능 지표 수집

- **현재**: 미구현
- **제안 목표**:
  - Web Vitals(LCP·FID·CLS·INP)를 `/api/metrics`로 beacon 전송
  - 집계는 Grafana 대시보드 또는 Datadog RUM
  - 핵심 경로별 SLO 설정 — 예: "도면 뷰어 첫 페이지 렌더 p95 ≤ 3초"

### 6.3 사용 분석 (옵션)

- **현재**: 미구현
- **제안**:
  - 어느 화면이 자주 쓰이는지 (화면별 PV·체류 시간)
  - 어느 알람이 자주 답변 상세로 열리는지 (알람 ID × 열람 횟수)
  - Design Lab 두 화면 중 어느 쪽 체류가 긴지 (UX 결정의 양적 근거)
- **개인정보**: 사용자 식별자는 해시, 도면 ID는 원본 유지 (운영 맥락 필요)

### 6.4 스스로 본 보완 포인트

- APM·로그 수집기 도입은 **인프라 결정(사내 호스팅 vs SaaS)** 완료 후
- 모니터링 자체가 **권한 감사(§3.3)**와 중복되므로 단일 로그 파이프라인으로 묶는 설계 필요

---

## 7. 의견 수렴 포인트

### 7.1 스스로 본 보완 포인트 (NFR 전반)

- 모든 성능 수치는 **로컬 dev 기준**. 프로덕션 빌드·실 서버 환경에서 재측정 필수
- 접근성은 **목표 수준(WCAG 2.1 AA)** 선언만 있고 audit 미실시. axe-core CI 통합 필요
- 권한 모델은 **제안 수준**. 조직의 기존 권한 체계와의 매핑이 미검증
- 다국어 도입 결정(단기 유지 vs 중기 영어 추가)은 이해관계자 합의 필요
- 모니터링 스택(Sentry·Datadog·자체)은 인프라 결정 의존
- 대형 도면(수백~수천 건) 스케일 테스트 미실시
- PDF 실 파일이 없어 `PdfViewer`의 실측 성능 미확인

### 7.2 이해관계자 의견 기록란

<!-- 아래에 자유롭게 덧붙여 주십시오. 형식: `- **YYYY-MM-DD · 이름**: 의견` -->

-

---

## 8. 참조

| 대상 | 경로 |
|---|---|
| 프로젝트 가이드 | `D:\_Project\prototype-도면지식관리-mvp\CLAUDE.md` |
| 보존 6항목 근거 | `D:\_Project\prototype-도면지식관리-mvp\docs\baseline-mvp\07-quirks-and-todo.md` |
| `.tap-target` 정의 | `D:\_Project\prototype-도면지식관리-mvp\src\app\globals.css` |
| 주석 스토어 | `D:\_Project\prototype-도면지식관리-mvp\src\lib\annotations-store.ts` |
| Insight Lab LLM 클라이언트 | `D:\_Project\prototype-도면지식관리-mvp\src\lib\insight\llm-client.ts` |
| Design Lab 목업 메타 | `D:\_Project\prototype-도면지식관리-mvp\src\lib\design-lab\mock-meta.ts` |

**관련 문서**: [전체 지도](./00-executive-summary.md) · [README](./README.md) · [비교 매트릭스](./03-comparison-matrix.md) · [FRS 시드](./05-frs-seed.md)
