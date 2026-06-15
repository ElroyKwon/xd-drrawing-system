# 도면지식관리 — 4페르소나 시연 프로토타입

> [[데이터 지식 스튜디오]](DKS) 기반 **도면지식관리** 서비스의 고객 시연용 Frontend-First 프로토타입.
> 가상 데이터로 4명 페르소나(P1~P4) × 3대 장면(S1~S3) 동작 검증.

---

## 빠른 시작

```bash
cd "prototype-도면지식관리"
npm install
npm run gen:data        # Phase 0 산출물 → JSON 변환 (최초 1회)
npm run copy:drawings   # 도면 PNG 복사 (최초 1회)
npm run dev             # http://localhost:3000
```

---

## ⚠️ Google Drive 경로 운영 주의

이 폴더는 Google Drive 동기화 폴더 안에 위치합니다.

- `node_modules/`는 `.gitignore`로 git 제외되지만, **Google Drive는 여전히 동기화를 시도**합니다.
- **권장**: Google Drive 클라이언트 설정에서 `node_modules` 폴더 동기화 제외 또는 Drive 일시 정지 후 `npm install`.
- `npm run dev` 중에는 Drive 동기화 충돌로 핫 리로드가 불안정할 수 있습니다.

---

## 페르소나 → 진입점

| 페르소나 | 역할 | URL |
|---------|------|-----|
| **P1 김기계** | 기계설비 주임 (냉동기/펌프/공조기) | `/p1-mechanical` |
| **P2 박전기** | 전기 담당 (UPS/변압기/배전반) | `/p2-electrical` |
| **P3 이소방** | 소방·방재 (스프링클러/감지기/Zone) | `/p3-fire` |
| **P4 최안전** | 시설안전 매니저 (분야 횡단 + What-If) | `/p4-safety` |

각 페르소나는 다음 3개 화면을 가집니다:
- `/{persona}` — 랜딩 (페르소나별 차별화)
- `/{persona}/entity/[tag]` — 설비 카드 (S1)
- `/{persona}/chat` — 자연어 질의 (S2)
- `/{persona}/impact` — 영향도 분석 (S3)

---

## 데이터 출처

- **전기 (P2)**: Phase 0 v1.31 실데이터 (`_Python_code/output/pre_analysis/20260327_110407/`)
- **기계 (P1)**, **소방 (P3)**: 분야 보강 mock (`scripts/generate-mock-data.ts` 내 정의)
- **건물안전 (P4)**: 위 3분야 통합 활용
- **관계/문서/Wiki/평면도/정비이력**: 가상 데이터

---

## 기술 스택

- Next.js 14 (App Router) + TypeScript + Tailwind CSS
- reactflow (영향도 그래프), fuse.js (검색), xlsx (P4 내보내기)
- 모든 API 호출은 `src/lib/mockApi.ts`의 가상 함수 (Promise + 인위적 지연)

---

## 디렉토리 안내

```
prototype-도면지식관리/
├─ data/         가상 데이터 JSON
├─ public/       정적 자산 (도면 PNG, 아이콘)
├─ scripts/      데이터 생성 스크립트
└─ src/
   ├─ app/       페르소나별 라우트 (P1~P4)
   ├─ components/ 공통/페르소나별 컴포넌트
   ├─ lib/       mockApi, 타입, 검색, 영향도 엔진
   └─ styles/    페르소나 테마
```

---

## 시연 흐름

상세 시연 스크립트 → `../02-시연-스크립트.md` (작성 예정).

---

## 관련 문서

- DKS 제공 가능 기능: `../00-지식스튜디오-제공가능기능.md`
- 페르소나 토론: `../01-도면지식관리-페르소나-토론.md`
