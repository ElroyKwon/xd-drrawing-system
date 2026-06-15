# 01. 프로젝트 개요

## 1.1 시스템 정의

**DKS(도면지식관리 시스템, Drawing Knowledge Studio)** 는 플랜트·건물 설비의 도면 정보를 온톨로지(지식 그래프) + RAG(문서 검색) + LLM-Wiki 세 가지 레이어로 구조화하고, 담당 분야별 맞춤 UX로 제공하는 지식 엔진 프로토타입이다.

---

## 1.2 배경 및 목적

### 문제 인식
현장에서 설비 관련 정보는 다음과 같이 파편화되어 있다.

- **도면 (PDF/DWG)**: 수백 페이지, 버전 관리 없음, 검색 불가
- **CMMS**: 정비이력만 있고 설계 정보 없음
- **엑셀 대장**: 사람마다 다른 형식, 업데이트 누락
- **구두 전달**: 담당자 퇴사 시 노하우 소실

### 해결 목표
1. 도면 → 자동 태그 추출 → 지식 그래프 구축
2. 자연어 질의로 설비 관계, 사양, 법규 확인
3. 설비 정지 시 영향 범위 즉시 시뮬레이션
4. 담당 분야별 최적화 UX (기계/전기/소방/안전)

---

## 1.3 Phase 0 범위

| 항목 | 내용 |
|------|------|
| 기준 프로젝트 | BESS(배터리 에너지 저장 시스템) PJT |
| 실데이터 | 전기 설비 80건 |
| 보강 mock 데이터 | 기계 25건 + 소방 20건 |
| 백엔드 | 가상(mock) — 실제 LLM·DB 미연결 |
| 목적 | UX 검증, 기능 흐름 시연, 이해관계자 피드백 |

---

## 1.4 기술 스택

| 구분 | 기술 | 선택 이유 |
|------|------|-----------|
| 프레임워크 | Next.js 14 (App Router) | SSR + 클라이언트 컴포넌트 혼용, 경로 기반 라우팅 |
| 언어 | TypeScript | 타입 안전성, 팀 협업 |
| 스타일링 | Tailwind CSS v3 | 빠른 UI 구성, 커스텀 테마 |
| 그래프 뷰 | React Flow (reactflow) | 방향 그래프 인터랙션 |
| 퍼지 검색 | Fuse.js | 태그·이름·설명 복합 가중치 검색 |
| 엑셀 내보내기 | xlsx (SheetJS) | 브라우저 측 xlsx 생성 |
| 아이콘 | lucide-react | 일관된 라인 아이콘 세트 |
| 데이터 | JSON 파일 (정적 import) | Phase 0 mock — 실운영 시 API 교체 예정 |

---

## 1.5 4 페르소나 개념

시스템의 핵심 UX 철학은 **같은 데이터, 다른 화면**이다. 동일한 지식 그래프를 보되, 역할에 따라 다른 인터페이스를 제공한다.

| 코드 | 이름 | 직책 | 핵심 니즈 | 특이사항 |
|------|------|------|-----------|----------|
| P-01 | 김기계 | 기계설비 엔지니어 | 큰 글씨, 정비이력, 영향 체인 | `large: true`, `answerMode: "short"` |
| P-02 | 이전기 | 전기 엔지니어 | 관계 테이블, 그래프 뷰, 도면 | `answerMode: "structured"`, `impactView: "graph"` |
| P-03 | 박소방 | 소방안전관리자 | 원문 인용, 평면도 오버레이 | `answerMode: "citation"`, `impactView: "floor"` |
| P-04 | 최안전 | 시설안전팀장 | What-If 시뮬레이션, 전 분야 집계, 엑셀 | `answerMode: "composite"`, `impactView: "what-if"` |

---

## 1.6 데이터 아키텍처 개념도

```
[원본 도면 PDF/DWG]
        ↓  (LLM 추출 — Phase 1 예정)
[entities.json]  ←→  [relations.json]   ← 지식 그래프
        ↓                    ↓
[wiki-pages.json]    [documents.json]   ← RAG 레이어
        ↓
[maintenance-logs.json]                 ← 운영 데이터
[floor-plans.json]                      ← 공간 데이터

            ↓ data-loader.ts
     [impact-engine.ts]  [search.ts]   ← 로직 레이어
            ↓
         [mockApi.ts]                  ← API 추상화
            ↓
      [React 컴포넌트]                 ← 프레젠테이션
```
