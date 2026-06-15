# GEM 프로젝트 개발 가이드 (_dev)

**작성일:** 2025-12-11
**버전:** 1.0

---

## 📚 문서 목록

| 번호 | 파일명 | 내용 | 상태 |
|------|--------|------|------|
| 00 | [00_포맷-비교-분석.md](./00_포맷-비교-분석.md) | CSV/Parquet/Arrow/HDF5 비교 분석 | ✅ 완료 |
| 01 | [01_배터리-표준-파일-명세.md](./01_배터리-표준-파일-명세.md) | Parquet 스키마, 컬럼 명세, 검증 규칙 | ✅ 완료 |
| 02 | [02_수학-공식-명세.md](./02_수학-공식-명세.md) | 4대 알고리즘 수식, Python 구현 | ✅ 완료 |
| 03 | [03_프롬프트-명령-규격.md](./03_프롬프트-명령-규격.md) | DSPy Signature, Context Builder, Guardrail | ✅ 완료 |
| 04 | [04_HTML-스타일-가이드.md](./04_HTML-스타일-가이드.md) | HTML 템플릿, CSS, Markdown 변환 | ✅ 완료 |
| 05 | [05_설정-구조-가이드.md](./05_설정-구조-가이드.md) | Global vs User 설정 분리, 무결성 검증 | ✅ 완료 |
| 06 | [06_실행-계획.md](./06_실행-계획.md) | Phase별 실행 절차, 통합 파이프라인 | ✅ 완료 |
| 07 | [07_배터리-프로파일-가이드.md](./07_배터리-프로파일-가이드.md) | 배터리 제조사별 프로파일 관리 및 선택 | ✅ 완료 |

---

## 🎯 문서 읽기 순서

### 처음 시작하는 경우

```
00_포맷-비교-분석.md
    ↓
01_배터리-표준-파일-명세.md
    ↓
07_배터리-프로파일-가이드.md (배터리 타입 이해)
    ↓
06_실행-계획.md (빠른 시작)
```

### 개발자 (전체 이해)

```
00_포맷-비교-분석.md (배경 지식)
    ↓
01_배터리-표준-파일-명세.md (데이터 구조)
    ↓
02_수학-공식-명세.md (알고리즘)
    ↓
07_배터리-프로파일-가이드.md (배터리 타입별 차이)
    ↓
03_프롬프트-명령-규격.md (AI)
    ↓
04_HTML-스타일-가이드.md (출력)
    ↓
05_설정-구조-가이드.md (구성)
    ↓
06_실행-계획.md (통합)
```

### 시스템 관리자

```
05_설정-구조-가이드.md (Global 설정 관리)
    ↓
07_배터리-프로파일-가이드.md (배터리 프로파일 관리)
    ↓
01_배터리-표준-파일-명세.md (데이터 검증)
    ↓
06_실행-계획.md (운영 절차)
```

---

## 🚀 빠른 시작

### 1. 환경 준비

```bash
# 프로젝트 루트에서
cd d:\0001_project\RFS

# 초기화 스크립트 실행
init.bat

# 가상환경 활성화
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# Ollama 모델 다운로드
ollama pull qwen2.5:32b-instruct-q4_K_M
```

### 2. 데이터 준비

```bash
# XD-HUB CSV 파일을 data/raw/에 복사
copy "C:\원본경로\xdhub_20251130.csv" "data\raw\"
```

### 3. 전체 파이프라인 실행

```bash
# Phase 1~3 자동 실행
python scripts/run_full_pipeline.py
```

### 4. 결과 확인

```bash
# HTML 리포트 열기
start results\20251130_140000\report.html
```

---

## 📊 데이터 흐름도

```
XD-HUB (CSV 1GB)
    ↓ [Phase 1: 13초]
배터리 표준 파일 (Parquet 155MB) ✅
    ↓ [Phase 2: 25초]
분석 결과 (Parquet + JSON) ✅
    ↓ [Phase 3: 60초]
최종 리포트 (HTML) ✅
```

---

## 🏗️ 프로젝트 구조

```
RFS/
├── _dev/                    # 📚 이 폴더 (개발 가이드)
│   ├── README.md
│   ├── 00_포맷-비교-분석.md
│   ├── 01_배터리-표준-파일-명세.md
│   ├── 02_수학-공식-명세.md
│   ├── 03_프롬프트-명령-규격.md
│   ├── 04_HTML-스타일-가이드.md
│   ├── 05_설정-구조-가이드.md
│   └── 06_실행-계획.md
│
├── _doc/                    # 📖 시스템 문서 (_doc 폴더 참조)
│
├── config/
│   ├── global/             # Global 설정 (수정 불가)
│   │   ├── formulas/       # 수학 공식
│   │   ├── prompts/        # 프롬프트
│   │   ├── templates/      # HTML 템플릿
│   │   └── thresholds.yaml # 임계값
│   │
│   └── user/               # User 설정 (수정 가능)
│       ├── prompts/        # 사용자 지침
│       ├── styles/         # 사용자 CSS
│       └── preferences.yaml # 환경설정
│
├── modules/
│   ├── data_loader/        # 데이터 수집
│   ├── intelligence/       # AI 프롬프트
│   ├── storage/            # 파일 저장
│   ├── validators/         # 데이터 검증
│   └── ...
│
├── scripts/
│   ├── phase1_convert_data.py     # Phase 1
│   ├── phase2_run_analysis.py     # Phase 2
│   ├── phase3_generate_report.py  # Phase 3
│   └── run_full_pipeline.py       # 통합 실행 ✅
│
├── data/
│   ├── raw/                # XD-HUB 원본 CSV
│   └── standard/           # 배터리 표준 Parquet ✅
│
└── results/                # 분석 결과 ✅
    └── YYYYMMDD_HHMMSS/
        ├── analysis_result.parquet
        ├── critical_racks.parquet
        ├── warning_racks.parquet
        ├── summary_stats.json
        ├── report.md
        └── report.html     # 최종 리포트 ✅
```

---

## 🔑 핵심 개념

### 배터리 프로파일 시스템 (NEW!)
- **웹 UI 선택**: 사용자가 6개 프로파일 중 직접 선택 (오류 가능성 낮음)
- **제조사별 임계값**: CATL LFP (2.0°C/min) vs Samsung NMC (1.5°C/min)
- **물리적 한계**: 전압 범위, 온도 범위, 수명이 배터리마다 완전히 다름
- **대화형 인터페이스**: 웹 채팅으로 프로파일 선택 및 Phase 실행
- **상세 가이드**: [07_배터리-프로파일-가이드.md](./07_배터리-프로파일-가이드.md)

### 배터리 표준 파일
- **포맷**: Apache Parquet (ZSTD 압축)
- **크기**: 155MB/월 (CSV 대비 85% 절감)
- **스키마**: 13개 컬럼 (timestamp, rack_id, v_avg, t_max, ...)
- **용도**: 모든 분석의 유일한 입력 소스

### 4대 알고리즘
1. **열적 안전성 (Thermal Safety)**: dT/dt > 2.0°C/min 감지 (배터리 타입별 다름)
2. **셀 밸런싱 (SPC)**: Z-Score > 3.0σ 감지 (배터리 타입별 다름)
3. **내부 단락 (ISC)**: 전압/온도/전류 종합 분석
4. **데이터 무결성 (Integrity)**: 물리 법칙 위반 검증

### Global vs User
- **Global**: 수학 공식, 배터리 프로파일, 기본 프롬프트 (수정 불가)
- **User**: 활성 프로파일 선택, 리포트 스타일, 사용자 지침 (수정 가능)

### 단계별 저장
- **Phase 1**: 배터리 표준 파일 저장 + 선택된 프로파일 적용
- **Phase 2**: 분석 결과 Parquet 저장 (프로파일별 임계값 적용)
- **Phase 3**: Markdown + HTML 리포트 저장

---

## 💡 자주 묻는 질문 (FAQ)

### Q1. CSV를 바로 분석하면 안 되나요?
**A:** 안 됩니다. 배터리 표준 파일로 변환해야 합니다.
- 용량: 85% 절감 (1GB → 155MB)
- 속도: 15배 빠름 (180초 → 12초)
- 타입 안전: 스키마 강제로 오류 방지

### Q2. Global 설정을 수정하고 싶어요.
**A:** 시스템 관리자만 가능합니다.
- Global 파일은 무결성 검증(체크섬)으로 보호
- User 설정으로 커스터마이징 가능

### Q3. Parquet 파일이 열리지 않아요.
**A:** Python 또는 Polars로 읽으세요.
```python
import polars as pl
df = pl.read_parquet("battery_data_20251130_140000.parquet")
print(df)
```

### Q4. HTML 리포트가 깨져요.
**A:** UTF-8 인코딩 확인 및 오프라인 모드 사용.
- 모든 리소스(CSS, JS, 폰트)는 HTML에 임베디드
- 인터넷 연결 불필요

### Q5. vLLM vs Ollama?
**A:** Ollama 사용 권장.
- GEM은 동시 요청 5개 이하
- vLLM은 과한 스펙 (동시 요청 100+ 때 필요)

### Q6. 배터리 타입을 모르는데 어떻게 하나요?
**A:** 웹 UI에서 프로파일을 선택하세요.
- 배터리 데이터시트 또는 프로젝트 문서에서 확인
- 6개 프로파일 중 선택 (NMC_LG, NCMA_LG, LFP_LG, LFP_CATL, NMC_Samsung, GENERIC_ESS_SAFE)
- 정말 모르면 GENERIC_ESS_SAFE 선택 (범용, 임시용)
- 상세 정보: [07_배터리-프로파일-가이드.md](./07_배터리-프로파일-가이드.md)

---

## 🛠️ 트러블슈팅

### 문제: Phase 1에서 "컬럼 누락" 오류
**원인:** XD-HUB CSV 컬럼명 불일치

**해결:**
```python
# scripts/phase1_convert_data.py 수정
# 'time' → 실제 컬럼명으로 변경
pl.col('your_time_column').str.to_datetime().alias('timestamp')
```

### 문제: Phase 3에서 SLM 응답 없음
**원인:** Ollama 서버 미실행 또는 모델 미다운로드

**해결:**
```bash
# Ollama 서버 시작
ollama serve

# 모델 확인
ollama list

# 모델 다운로드 (없으면)
ollama pull qwen2.5:32b-instruct-q4_K_M
```

### 문제: HTML 리포트 한글 깨짐
**원인:** UTF-8 인코딩 문제

**해결:**
```python
# config/global/html/markdown_converter.py 확인
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_report)
```

---

## 📞 문의

### 기술 지원
- **Email:** gem-dev@example.com
- **문서 이슈:** [GitHub Issues](https://github.com/example/gem/issues)

### 문서 기여
- Pull Request 환영
- _dev 폴더 내 문서 개선 제안

---

## 🔄 버전 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-12-12 | 1.1 | 배터리 프로파일 시스템 추가 (07), AI 스타일 출력, 중앙 설정 통합 |
| 2025-12-11 | 1.0 | 초기 _dev 문서 전체 작성 (00~06) |

---

**🚀 개발을 시작하려면 [06_실행-계획.md](./06_실행-계획.md)부터 읽어주세요!**
