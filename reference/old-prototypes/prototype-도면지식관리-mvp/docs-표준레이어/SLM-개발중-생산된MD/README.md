---
tags:
  - SLM인사이트
  - GEM
  - 배터리안전진단
  - DualEngine
  - 선행사례
aliases:
  - GEM 개발 문서 묶음
  - SLM 인사이트 개발 원본
created: 2026-04-17
related:
  - "[[../README|docs-표준제안서 README]]"
  - "[[../docs-시스템분석/README|docs-시스템분석 README]]"
  - "[[../../../SLM 인사이트 분석/CLAUDE|SLM 인사이트 분석 CLAUDE]]"
---

# SLM-개발중-생산된MD — GEM(SLM 인사이트) 개발 문서 아카이브

> **목적**: [[SLM 인사이트 분석]](GEM — Generative Engineering Module) 프로젝트 개발 중 생산된 기술 문서를 **DKS 표준제안서 맥락에서 참조 가능하게** 보관
> **수록 방식**: `slm.zip` (1.4MB, 59개 md) — 원본 그대로 압축 보관
> **위치 의의**: DKS 서비스 설계 시 **Dual Engine + 수학/AI 분리 사상**의 **선행 검증 사례**로 참조

---

## 1. 이 폴더는 왜 DKS 제안서 밑에 있는가

DKS 코어 엔진의 철학 중 하나는 **"수학/물리로 1차 인과관계를 확정하고, AI(SLM)는 2차 해석만 담당한다"**(할루시네이션 구조적 통제). 이 사상은 SLM 인사이트 분석(GEM)에서 **먼저 배터리 안전 진단에 적용되어 실증**되었다.

따라서 DKS 제안서/서비스 설계 단계에서:

- GEM의 **4-Layer 아키텍처** → DKS의 온톨로지+RAG+서비스 계층 설계에 직접 참조
- GEM의 **Dual Engine** → DKS의 "온톨로지(규칙 기반) + AI 질의(자연어 해석)" 이원 구조 근거
- GEM의 **No-DB 전략(Parquet+YAML)** → DKS Phase 0 산출물 관리 방식의 원형
- GEM의 **Hot/Cold Path** → DKS 서비스 계층의 실시간 알림 vs 심층 분석 분기 설계에 이식 가능

---

## 2. 압축 파일 구성 (slm.zip)

### 2.1 `_doc/` — 시스템 문서 (고정/체계화, 18개)

| # | 문서 | 내용 | DKS 참조 포인트 |
|:-:|------|------|----------------|
| 00 | 시작하기 | 빠른 시작 가이드 | — |
| 00 | 전체-프로젝트-요약 | Executive Summary | Dual Engine 사상 원문 |
| 01 | 프로젝트-개요 | 4대 알고리즘(Thermal/SPC/ISC/Integrity) | DKS 추론 소비자 유형의 원형 |
| 02 | 시스템-아키텍처 | 4-Layer + State Machine + Hot/Cold Path | **DKS 서비스 계층 설계 직접 참조** |
| 03 | 데이터-명세 | 입출력 스키마 | YAML/Parquet 자산 구조 |
| 04 | 품질-및-보안 | Partial Success, Physics Validator | DKS HITL 정책의 선례 |
| 05 | 개발-Phase별-가이드 | Phase 1~5 실행 절차 | DKS Phase 0/1 단계 구성 참조 |
| 05 | REG_학습_가이드 | REG 학습 데이터 생성 | 데이터 축적 → AI 학습 흐름 |
| 06 | 기술-스택-및-도구 | 기술 스택, 환경 | — |
| 07 | 개발-방법론 | TDD, 코딩 규칙 | 상위 CLAUDE.md Global Rules 정합 |
| 08 | FAQ-및-트러블슈팅 | — | — |
| 09 | SLM-프롬프트-전략 | Prompt Guardrail, Semantic YAML | **DKS AI 프롬프트 설계 직접 참조** |
| 10 | 성능-최적화-가이드 | Parquet, Polars | DKS 대용량 처리 시 참조 |
| 11 | GPU-하드웨어-가이드 | GPU 사양, 비용 | On-premise 배포 시 참조 |
| 12 | 모델-설정-가이드 | Ollama 설정 | 로컬 SLM 배포 참조 |
| — | web_ui_gradio | Gradio UI | — |
| — | api/collector_api, api/fastapi_guide | API 수집 + FastAPI | DKS 백엔드 API 설계 참조 |
| — | setup/ollama_setup, setup/migration | 설치 + 마이그레이션 | — |
| — | phase2_zscore_bug_fix, phase3_insight_improvement_plan | Phase 개선 이력 | 운영 이슈 대응 패턴 |

### 2.2 `_dev/` — 개발 상세 (41개, 이슈·TODO 포함)

| 번호 | 파일 | 내용 |
|:-:|------|------|
| 00 | 설치-가이드 / 포맷-비교-분석 | 설치, CSV/Parquet/Arrow/HDF5 비교 |
| 01 | 배터리-표준-파일-명세 | Parquet 스키마, 검증 규칙 |
| 02 | **수학-공식-명세** | **4대 알고리즘 수식 + Python 구현 (근거 엔진 원문)** |
| 03 | 프롬프트-명령-규격 | DSPy Signature, Context Builder, Guardrail |
| 04 | HTML-스타일-가이드 | 리포트 템플릿, CSS |
| 05 | 설정-구조-가이드 | Global vs User 설정 분리, 무결성 검증 |
| 06 | **실행-계획** | **Phase별 실행 절차, 통합 파이프라인** |
| 07 | 배터리-프로파일-가이드 | 배터리 제조사별 프로파일 관리 |
| 08 | 웹UI-구현-완료 | UI 구현 이력 |
| 09 | 디렉토리-구조 | 폴더 구조 정의 |
| 10 | AI-프롬프트-가이드 | 프롬프트 설계 상세 |
| 11 | HTML-리포트-스타일 | 리포트 스타일 |
| 12 | 종합-인사이트-생성-로직 | 인사이트 수렴 로직 |
| 13 | 로깅-정책 | 로그 레벨·포맷 |
| 16 | API-데이터-수집-시스템 | 수집 모듈 |
| 18 | 전체-프로세스-흐름도 | End-to-End 흐름 (83KB — 가장 상세) |
| 19 | v2.0-변경사항-요약 | 버전 변경 이력 |
| 20 | 데이터-수집-저장-변환-전략 | 파이프라인 설계 |
| 21 | 프롬프트-명령어-시스템 | 프롬프트 DSL |
| — | 2026-01-16_DC_Link_구현_TODO | DC Link 작업 메모 |
| — | 2026-01-16_설정파일_통합_environment.yaml | 설정 통합 작업 |
| — | 2026-01-16_폴더구조_runid명명규칙_개선 | 폴더 구조 개편 |
| — | analysis_criteria | 분석 기준 정의 |
| — | spike_threshold_research_report | Spike 임계값 연구 |
| — | TODO_데이터수집_저장_변환 | 미완료 작업 |
| — | 배치모드_구현_명세 | Batch 모드 구현 |
| — | _archive_14/15/17 | 구 태그 리스트·수집 모듈 완료본 |
| — | 작업내역_복구가이드_20260108 | 복구 가이드 |

---

## 3. 핵심 발췌 — DKS 설계에 직접 주입할 수 있는 것

### 3.1 Dual Engine (수학 근거 + SLM 해석)

```
HOT PATH:  임계값 비교 (< 1초 SLA) — 즉시 알림
COLD PATH: 4대 알고리즘 → SLM 해석 → 리포트 (15초 SLA)

수치 계산 = Python (환각 없음, 재현 가능)
자연어 설명 = SLM (Ollama Gemma 2:27b / Qwen2.5 32B)
```

**DKS 이식**: 설비 관계 질의 시 **TypeDB 추론(근거)** + **SLM 답변 생성(해석)** 분리. AI가 근거 조작 불가.

### 3.2 No-DB 자산화 패턴

```
/results/{YYYYMMDD}_{RunID}/
  ├── index.html              # 뷰어 진입점
  ├── summary/*.yaml          # 구조화 결과
  ├── racks/*.parquet         # 시계열 자산
  └── report/final_report.md  # AI 리포트
```

**DKS 이식**: Phase 0/1 산출물(YAML + 이미지 + 온톨로지)을 **Run-ID 단위 Atomic Write**로 자산화. DB 없이 파일 시스템만으로 복구/재현 가능.

### 3.3 Partial Success 정책

```
데이터 수집률 ≥ 80% → 진행 허용
AI 타임아웃(60초) → 정적 템플릿 리포트 Fallback
dT/dt > 10.0°C/min → Sensor Error 자동 필터
```

**DKS 이식**: Phase 0 qualified 비율 기준(38~57%)이 너무 낮을 때의 **Partial Success 임계값** 설정 참고.

---

## 4. 압축 해제 방법

```bash
cd "G:/내 드라이브/_Obsidian/지식관리/00. XD-AI 플랫폼/데이터 지식 스튜디오/docs-표준제안서/SLM-개발중-생산된MD/"
unzip -o slm.zip -d slm-unpacked/    # 임시 작업 폴더에 해제
# 원본 slm.zip은 그대로 보존
```

> ⚠️ 원본 `slm.zip`은 **SLM 인사이트 분석 프로젝트의 개발 스냅샷**이다. DKS 맥락에서는 **읽기 전용 선행 사례**로만 참조하고, DKS 소스로 직접 편입하지 말 것.

---

## 5. 원본 프로젝트 위치

- 상위 가이드: [[../../../SLM 인사이트 분석/CLAUDE|SLM 인사이트 분석/CLAUDE.md]]
- 수학 공식: `SLM 인사이트 분석/docs/02_수학-공식-명세.md` (zip 내 `_dev/02_수학-공식-명세.md`와 동일 계통)
- 제안서 컨텍스트: `SLM 인사이트 분석/SLM_INSIGHT_제안서_컨텍스트.md`

---

## 6. 상위 문서와의 관계

- [[../README|docs-표준제안서 README]] — DKS 제공 기능 카탈로그(SLM의 Dual Engine을 DKS에 이식)
- [[../docs-시스템분석/README|docs-시스템분석 README]] — DKS 방향성 검토(Layer 0→1→2 전략)
- [[../00-지식스튜디오-제공가능기능|00-지식스튜디오-제공가능기능]] — DKS 기능 단위 카탈로그

---

*이 폴더는 참조 자료 아카이브입니다. 능동 개발은 `SLM 인사이트 분석/` 프로젝트에서 진행됩니다.*
