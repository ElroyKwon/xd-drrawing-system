# DKS 제안서 — 편집 및 변환 가이드

## 파일 구성

| 파일 | 용도 |
|---|---|
| `proposal.md` | Marp 슬라이드 원본 (12장) |
| `../screenshots/` | 스크린샷 원본 (proposal.md 기준 상대경로) |

---

## PPTX / PDF 변환 (Marp CLI)

### 설치 (최초 1회)

```bash
npm install -g @marp-team/marp-cli
```

### 변환 명령

```bash
# proposal/ 폴더에서 실행할 것

# PPTX 변환
marp proposal.md --pptx --output proposal.pptx

# PDF 변환
marp proposal.md --pdf --output proposal.pdf

# HTML 미리보기
marp proposal.md --html --output proposal.html
```

> **주의**: 반드시 `docs/mockup-report/proposal/` 폴더에서 실행해야 `../screenshots/` 상대경로가 올바르게 해석됩니다.

### VS Code 실시간 미리보기

1. VS Code 확장 **"Marp for VS Code"** 설치
2. `proposal.md` 열기
3. 우상단 미리보기 아이콘 클릭 → 슬라이드 실시간 렌더 확인

---

## 스크린샷 경로 규칙

- `proposal.md` 위치: `docs/mockup-report/proposal/`
- 스크린샷 위치: `docs/mockup-report/screenshots/`
- **상대 경로: `../screenshots/파일명.png`** (한 단계만 위로)

이미지 크기 조절 (Marp 문법):
```markdown
![w:600px](../screenshots/il-hub-full.png)   # 너비 600px
![w:480px](../screenshots/파일.png)           # 너비 480px (2장 병렬 시)
```

---

## 편집 가이드

### 슬라이드 구분

```markdown
---        ← 슬라이드 구분자 (앞뒤 빈 줄 필수)
```

### 텍스트 밀도 기준

| 요소 | 제한 |
|---|---|
| 슬라이드 제목 | 1줄, 20자 이내 |
| 강조 문구 (`>`) | 1줄, 40자 이내 |
| 본문 bullet | 슬라이드당 최대 5개 |
| 표 | 최대 4열 × 5행 |
| 총 텍스트 | 슬라이드당 200자 이내 권장 |

### 발표자 노트

```markdown
<!--
발표자 노트:
- 발표 시 구두로 부연할 내용
- PPTX 변환 시 노트 섹션에 자동 삽입
-->
```

---

## 표현 가이드 — 과도기적 시스템

제안서 전체에서 일관되게 유지해야 하는 표현 원칙입니다.

| 금지 | 권장 |
|---|---|
| "~이 됩니다" (완료형 단언) | "~을 확인할 수 있습니다" |
| "AI가 정확하게 분석합니다" | "AI 분석 결과를 담당자가 검토·수정합니다" |
| "4~8주면 전사 도입 완료" | "파일럿 기준 4~8주, 전사 확장은 결과 기반으로 결정" |
| "모든 도면 형식 지원" | "현재 PDF 도면 기준으로 파일럿 운영 중" |
| "보고서 자동 생성" | "보고서 **초안** 자동 생성, 담당자 검토" |
| "30초 이내 파악" | "30초 이내 파악을 목표로 설계" |
| 성과 수치 약속 | 수치 없이 워크플로우 전환만 설명 |

---

## 슬라이드 목록

| # | 제목 | 스크린샷 |
|---|---|---|
| 01 | 표지 | 없음 |
| 02 | 지금 이 문제, 익숙하지 않으신가요? | 없음 |
| 03 | 기존 도구들이 해결 못 하는 이유 | 없음 |
| 04 | DKS는 기존 시스템을 교체하지 않습니다 | 없음 |
| 05 | 도면 PDF에서 설비 지식 그래프까지 | `il-lab-bundle.png` |
| 06 | Insight Lab — 운영 현장의 질문에 즉시 답하다 | `il-hub-full.png` |
| 07 | Insight Lab — 화면으로 보기 | `il-alarms-drawer.png` + `il-reports-detail.png` |
| 08 | Design Lab — 도면을 파일이 아닌 지식으로 관리하다 | `dl-cards-full.png` |
| 09 | Design Lab — 화면으로 보기 | `dl-cards-tab-ontology.png` + `dl-chat-drawing-mode.png` |
| 10 | 파일럿 기준 4~8주로 시작하는 방법 | 없음 |
| 11 | 이런 환경이라면 파일럿에 적합합니다 | 없음 |
| 12 | 다음 미팅에서 함께 확인할 수 있습니다 | `il-chat-empty.png` |

---

## 관련 문서

| 문서 | 경로 |
|---|---|
| 목업 보고서 인덱스 | `../README.md` |
| Insight Lab 상세 | `../01-insight-lab/00-overview.md` |
| Design Lab 상세 | `../02-design-lab/00-overview.md` |
| FRS 시드 (개발 착수용) | `../05-frs-seed.md` |
