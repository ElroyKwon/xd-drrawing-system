# API 데이터 수집 시스템

**작성일:** 2025-12-23
**최종 업데이트:** 2025-12-26
**버전:** 2.0.0 (폴더 구조 개선 반영)
**목적:** 제주 장주기 배터리 시스템 데이터 실시간/과거 수집 및 분석

---

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [수집 모드](#수집-모드)
3. [서버 부하 방지 전략](#서버-부하-방지-전략)
4. [데이터 저장 구조](#데이터-저장-구조)
5. [UI/UX 설계](#uiux-설계)
6. [기술 사양](#기술-사양)
7. [에러 처리](#에러-처리)

---

## 1. 시스템 개요

### 1.1 목적

제주 장주기 배터리 시스템(6개 채널, 4,860개 태그)의 데이터를 안정적으로 수집하여 GEM 분석 시스템에 공급합니다.

### 1.2 핵심 요구사항

- ✅ **서버 부하 방지**: 배치 처리 및 딜레이로 API 서버 보호
- ✅ **데이터 무결성**: 누락 구간 자동 감지 및 복구
- ✅ **실시간 수집**: 15초 주기로 최신 데이터 수집
- ✅ **과거 데이터**: 특정 날짜 전체 데이터 수집
- ✅ **사용자 제어**: 시작/정지/재개 가능
- ✅ **일일 분석**: 하루 단위 데이터 기반 리포트 생성

### 1.3 기존 참조 시스템

**소스:** `D:\0001_project\git\acs-data-utils\xd\get_trends.py`

**핵심 로직:**
```python
# API 엔드포인트
API_URL = "https://hndc-xd.twoz.kr/runtime-api/runtime/historian/get-data-list"

# 요청 파라미터
params = {
    'aggTime': '5m',              # 집계 간격
    'startDt': '2025-12-23 00:00:00',
    'endDt': '2025-12-23 23:59:59',
    'excludeZero': 'false',
    'fillWithPreviousValue': 'false',
    'searchType': 'TAG',
    'tagFullName': 'TAG1,TAG2,TAG3,...'  # 콤마로 구분
}

# 헤더
headers = {
    'proj-id': 'f92984a4-8427-4990-a7fa-574847436804',
    'accept': 'application/json, text/plain, */*'
}
```

---

## 2. 수집 모드

### 2.1 모드 1: 과거 데이터 수집 (Historical Mode)

**용도:** 특정 날짜의 전체 데이터를 한 번에 수집

**특징:**
- 하루 전체 (00:00:00 ~ 23:59:59)
- 완료 후 사용자 확인 프롬프트
- 분석 진행 여부 선택 가능
- **모든 배치가 동일한 시간 범위 사용** (참고: get_trends.py)

**핵심 로직:**
```python
# 하루 전체를 한 번의 시간 범위로 요청
date = "2025-12-20"
start_dt = f"{date} 00:00:00"
end_dt = f"{date} 23:59:59"
agg_time = "5m"

# 태그만 배치로 나눠서 요청 (시간은 동일!)
for channel in channels:
    tags = load_channel_tags(channel)  # 810개
    batches = create_batches(tags, batch_size=20)  # 41개 배치

    for batch in batches:
        # 모든 배치가 같은 시간 범위 요청
        result = api_request(
            tags=batch,
            start_dt="2025-12-20 00:00:00",  # 고정
            end_dt="2025-12-20 23:59:59",    # 고정
            agg_time="5m"
        )
        # → 각 태그마다 288개 시간 포인트 받음
        #    (00:00, 00:05, 00:10, ..., 23:55)

        time.sleep(1.0)  # 배치 간 딜레이
```

**플로우:**
```
[사용자] 날짜 선택 (2025-12-20)
         집계 간격 선택 (5m)
    ↓
[시스템] 시간 범위 고정
         start_dt = "2025-12-20 00:00:00"
         end_dt = "2025-12-20 23:59:59"
    ↓
[시스템] 수집 시작 (배치 처리)
    ↓
    ├─ CH_01: 배치 1/41 ... 41/41 완료 (810개 태그 × 288개 시간)
    ├─ CH_02: 배치 1/41 ... 41/41 완료
    ├─ CH_03: 배치 1/41 ... 41/41 완료
    ├─ CH_04: 배치 1/41 ... 41/41 완료
    ├─ CH_05: 배치 1/41 ... 41/41 완료
    └─ CH_06: 배치 1/41 ... 41/41 완료
    ↓
[시스템] 수집 완료! (총 243개 배치)
         총 시간 포인트: 288개 (5분 간격)
    ↓
[프롬프트] "2025-12-20 데이터 수집 완료!
           총 1,440개 레코드 수집 (288 시간 × 6 채널)

           지금 분석을 진행하시겠습니까?"

           [예] [아니오]
    ↓
[예 선택] → GEM 분석 시작
[아니오] → 대기
```

**배치 처리 전략:**
```
총 태그: 4,860개 (6채널 × 810개)
배치 크기: 20개

방법 1: 채널 순차 처리 (채택)
  CH_01: 810개 ÷ 20 = 41배치
  CH_02: 810개 ÷ 20 = 41배치
  ...
  총 배치: 243개 (41 × 6)
  총 시간: 243배치 × 1초 = ~4분

방법 2: 전체 태그 배치 (비효율)
  4,860개 ÷ 20 = 243배치
  하나의 긴 큐로 처리
  → 채널 구분 없어서 CSV 저장 복잡
```

**저장 위치 (폴더 구조 2.0.0):**
```
GEM/data/source/api/2025-12-20/
├── bsc_ch_01.csv
├── bsc_ch_02.csv
├── bsc_ch_03.csv
├── bsc_ch_04.csv
├── bsc_ch_05.csv
└── bsc_ch_06.csv
```

### 2.2 모드 2: 실시간 수집 (Real-time Mode)

**용도:** 현재 진행형으로 계속 데이터 수집

**특징:**
- **수집 주기 = 집계 간격** (중요!)
  - aggTime=5m → 5분마다 수집
  - aggTime=1m → 1분마다 수집
- 집계 시각 정렬 (5분 단위: 00, 05, 10, 15, ...)
- 시작/정지/재개 가능
- 자정(00:00) 자동 날짜 전환

**왜 수집 주기 = 집계 간격?**
```
집계 간격 5분인데 15초마다 수집하면?
→ 같은 데이터를 20번 중복 수집! (5분 ÷ 15초 = 20)
→ 서버 부하만 증가, 새 데이터 없음

올바른 방식:
→ 5분마다 1번만 수집
→ 매번 새로운 데이터 획득
```

**시간 정렬 로직:**
```python
# 현재 시각을 집계 간격에 맞춰 정렬
now = datetime.now()  # 09:17:32

if agg_time == "5m":
    # 5분 단위로 내림
    minutes = (now.minute // 5) * 5  # 17 // 5 = 3, 3 * 5 = 15
    aligned = now.replace(minute=minutes, second=0, microsecond=0)
    # → 09:15:00

elif agg_time == "1m":
    # 1분 단위로 내림
    aligned = now.replace(second=0, microsecond=0)
    # → 09:17:00

# API 요청 시간 범위
start_dt = aligned.strftime('%Y-%m-%d %H:%M:%S')  # "2025-12-23 09:15:00"
end_dt = now.strftime('%Y-%m-%d %H:%M:%S')        # "2025-12-23 09:17:32"

# 이 범위로 요청하면 09:15:00 데이터 1개만 받음 (5분 집계)
```

**플로우:**
```
[시작] 클릭 (09:17:32)
    ↓
[갭 체크] 마지막 수집 시각 확인
    ├─ 갭 없음 → 바로 시작
    └─ 갭 있음 → "09:00 ~ 09:15 데이터 누락
                   채우시겠습니까?"
                   [예] → 과거 모드로 갭 채우기 → 실시간 시작
                   [아니오] → 갭 무시하고 시작
    ↓
[5분 주기 반복] (aggTime=5m 기준)

    시각: 09:17:32
    정렬: 09:15:00
    수집: 09:15:00 데이터
    ├─ CH_01: 배치 1~41 (약 50초 소요)
    ├─ CH_02: 배치 1~41
    ├─ CH_03: 배치 1~41
    ├─ CH_04: 배치 1~41
    ├─ CH_05: 배치 1~41
    └─ CH_06: 배치 1~41

    → 다음 5분 경계(09:20:00)까지 대기

    시각: 09:20:05
    정렬: 09:20:00
    수집: 09:20:00 데이터
    ├─ CH_01~06 수집

    → 09:25:00까지 대기

    (계속 반복...)
    ↓
[정지] 클릭
    → 현재 배치 완료 후 중지
    → 중지 시각 기록
    ↓
[재개] 클릭
    → 갭 체크 → 채우기 제안 → 계속
    ↓
[자정 00:00 도달]
    → "2025-12-23 데이터 수집 완료!
       분석을 진행하시겠습니까?"
       [예] [아니오]
    → 새 날짜 폴더로 전환 (2025-12-24/)
```

**실행 타임라인 예시:**
```
시각        정렬시각    수집 데이터    동작
────────────────────────────────────────────
09:17:32 → 09:15:00 → 09:15:00 → 6채널 수집 시작
09:22:50 → 09:20:00 → 09:20:00 → 6채널 수집 시작
09:25:10 → 09:25:00 → 09:25:00 → 6채널 수집 시작
09:30:05 → 09:30:00 → 09:30:00 → 6채널 수집 시작
```

**저장 방식:**
```python
# 실시간으로 append 모드로 저장 (폴더 구조 2.0.0)
with open('GEM/data/source/api/2025-12-23/bsc_ch_01.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow([timestamp, val1, val2, ...])
```

---

## 3. 서버 부하 방지 전략

### 3.1 문제 인식

**위험 상황:**
```
6개 채널 × 810개 태그 = 4,860개 태그
동시에 같은 시간대 데이터 요청 → 서버 과부하 → 시스템 다운
```

### 3.2 해결 방안

#### A) 채널별 순차 처리 (핵심 전략)

**과거 데이터 수집 (Historical):**
```
총 6개 채널을 순차적으로 처리:

채널      배치 수    딜레이    소요 시간
─────────────────────────────────────
CH_01     41개      1.0초     ~50초
CH_02     41개      1.0초     ~50초
CH_03     41개      1.0초     ~50초
CH_04     41개      1.0초     ~50초
CH_05     41개      1.0초     ~50초
CH_06     41개      1.0초     ~50초
─────────────────────────────────────
                    총: ~5분

※ 시간 범위는 모든 배치 동일 (00:00 ~ 23:59)
※ 태그만 배치로 분할
```

**실시간 수집 (Real-time):**
```
5분 주기(aggTime=5m 기준)로 6개 채널 순차 처리:

시각        채널      수집 데이터    소요
───────────────────────────────────────
09:17:32   CH_01     09:15:00      ~50초
09:18:22   CH_02     09:15:00      ~50초
09:19:12   CH_03     09:15:00      ~50초
09:20:02   CH_04     09:15:00      ~50초
09:20:52   CH_05     09:15:00      ~50초
09:21:42   CH_06     09:15:00      ~50초
───────────────────────────────────────
완료: 09:22:32 (총 5분)

→ 다음 5분 경계(09:25:00)까지 대기
→ 09:25:XX부터 09:25:00 데이터 수집
```

**배치 처리 상세:**
```
채널당 810개 태그 ÷ 20개/배치 = 41개 배치

배치 1: 태그 1~20    → API 호출 → 1초 딜레이
배치 2: 태그 21~40   → API 호출 → 1초 딜레이
배치 3: 태그 41~60   → API 호출 → 1초 딜레이
...
배치 41: 태그 801~810 → API 호출 → 완료

총 소요 시간:
  - API 응답: 41배치 × ~0.2초 = ~8초
  - 딜레이: 40배치 × 1.0초 = 40초
  - 합계: ~50초/채널
```

#### B) 설정 가능한 파라미터

```python
API_CONFIG = {
    # API 연결 정보
    "api_url": "https://hndc-xd.twoz.kr/runtime-api/runtime/historian/get-data-list",
    "proj_id": "f92984a4-8427-4990-a7fa-574847436804",

    # 배치 처리 설정
    "batch_size": 20,           # 한 번에 요청할 태그 수
    "batch_delay": 1.0,         # 배치 간 대기 시간 (초)

    # 집계 간격 (중요!)
    "agg_time": "5m",          # 데이터 집계 간격 (1m, 5m, 10m, 30m, 1h)
                               # ※ 실시간 수집 주기 = agg_time
                               # ※ 5m = 5분마다 수집
                               # ※ 1m = 1분마다 수집

    # 에러 처리
    "timeout": 30,             # API 요청 타임아웃 (초)
    "retry_count": 3,          # 실패 시 재시도 횟수
    "retry_delay": 5,          # 재시도 간 대기 시간 (초)
    "max_concurrent": 1        # 동시 요청 수 (항상 1로 고정)
}

# 집계 간격별 예상 수집 시간 (6채널 기준)
AGG_TIME_INFO = {
    "1m": {
        "collection_cycle": "1분마다",
        "time_points_per_day": 1440,  # 24 × 60
        "channel_processing_time": "~50초",
        "total_cycle_time": "~5분"
    },
    "5m": {
        "collection_cycle": "5분마다",
        "time_points_per_day": 288,   # 24 × 60 ÷ 5
        "channel_processing_time": "~50초",
        "total_cycle_time": "~5분"
    },
    "10m": {
        "collection_cycle": "10분마다",
        "time_points_per_day": 144,   # 24 × 60 ÷ 10
        "channel_processing_time": "~50초",
        "total_cycle_time": "~5분"
    }
}
```

#### C) 자동 부하 조절

```python
# API 응답 시간 모니터링
if response_time > 2.0:  # 2초 이상
    # 경고 표시
    status_color = "🟡 느림"

    # 자동 딜레이 증가
    current_delay = min(current_delay * 1.5, 5.0)  # 최대 5초

if response_time > 5.0:  # 5초 이상
    # 위험 표시
    status_color = "🔴 위험"

    # 배치 크기 감소
    current_batch_size = max(current_batch_size - 5, 10)  # 최소 10개
```

#### D) HTTP 상태 코드 처리

```python
# 429: Too Many Requests
if status_code == 429:
    wait_time = 30  # 30초 강제 대기
    show_warning(f"서버 부하 감지. {wait_time}초 대기 중...")
    time.sleep(wait_time)
    # 재시도

# 500: Internal Server Error
if status_code == 500:
    show_error("서버 오류 발생!")
    pause_collection()  # 즉시 중단
    prompt_user("서버 오류로 수집을 일시 중지했습니다. 재시도하시겠습니까?")

# 503: Service Unavailable
if status_code == 503:
    wait_time = 60
    show_error(f"서버 점검 중. {wait_time}초 후 재시도...")
    time.sleep(wait_time)
```

---

## 4. 데이터 저장 구조

### 4.1 디렉토리 구조 (폴더 구조 2.0.0)

```
GEM/
├── api_collector/              # API 수집 모듈 ✅
│   ├── __init__.py
│   ├── site_manager.py        # 🆕 사이트 관리 (Multi-Site)
│   ├── historical.py          # 과거 데이터 수집기
│   ├── realtime.py            # 실시간 수집기
│   ├── config.py              # 설정 관리
│   ├── storage.py             # CSV 저장 로직 (사이트별)
│   └── monitor.py             # 상태 모니터링
│
├── data/                       # 🆕 통합 데이터 폴더
│   ├── map/                    # 🆕 사이트별 배터리 맵 (Multi-Site 지원)
│   │   ├── jeju_bess/         # 제주 BESS 프로젝트
│   │   │   ├── 제주장주기밧데리맵.xlsx  # 배터리 맵 Excel
│   │   │   ├── bsc_ch_01_tags.txt      # 채널별 태그
│   │   │   ├── bsc_ch_02_tags.txt
│   │   │   ├── bsc_ch_03_tags.txt
│   │   │   ├── bsc_ch_04_tags.txt
│   │   │   ├── bsc_ch_05_tags.txt
│   │   │   ├── bsc_ch_06_tags.txt
│   │   │   └── all_channels_tags.json  # 통합 태그
│   │   │
│   │   └── busan_bess/        # 향후 추가 사이트 예시
│   │       └── 부산BESS맵.xlsx
│   │
│   ├── source/                 # 원본 데이터 소스
│   │   ├── api/                # API 수집 데이터 ✅
│   │   │   ├── 2025-12-20/    # 날짜별 폴더
│   │   │   │   ├── bsc_ch_01.csv
│   │   │   │   ├── bsc_ch_02.csv
│   │   │   │   ├── bsc_ch_03.csv
│   │   │   │   ├── bsc_ch_04.csv
│   │   │   │   ├── bsc_ch_05.csv
│   │   │   │   └── bsc_ch_06.csv
│   │   │   │
│   │   │   └── 2025-12-23/    # 실시간 수집 중
│   │   │       ├── bsc_ch_01.csv (append 모드)
│   │   │       └── ...
│   │   │
│   │   ├── upload/             # 사용자 업로드
│   │   │   └── YYYYMMDD_HHMMSS/
│   │   │
│   │   └── samples/            # 샘플 데이터
│   │
│   └── standard/2025/          # 표준화된 Parquet
│
├── results/                    # 분석 결과 ✅
│   └── {RUN_ID}/              # 예: 20251226_140000_NMC_LG
│       ├── metadata.json       # 🆕 실행 메타데이터
│       ├── phase1_convert/    # Phase 1: 데이터 변환
│       ├── phase2_validate/   # Phase 2: 수학적 검증
│       ├── phase3_insights/   # Phase 3: AI 인사이트
│       └── phase4_report/     # Phase 4: HTML 리포트
│           ├── report.html
│           └── summary.json    # 🆕 핵심 지표 요약
│
├── logs/                       # 🆕 로그 파일 세분화
│   ├── api_collection/         # API 수집 로그 ✅
│   │   ├── 2025-12-20.log
│   │   └── 2025-12-23.log
│   ├── analysis/               # 분석 실행 로그
│   └── system/                 # 시스템 로그
│
└── config/
    └── api_config.json         # API 설정
        {
          "api_url": "https://...",
          "proj_id": "...",
          "batch_size": 20,
          "batch_delay": 1.0,
          "agg_time": "5m"
        }
```

### 4.2 CSV 파일 구조

**파일명:** `bsc_ch_01.csv`

**헤더:**
```csv
time,BSC_CH_01.BANK_01.RACK_01.MOD_AVG_TEMP,BSC_CH_01.BANK_01.RACK_01.MOD_MAX_TEMP,...
```

**데이터 행:**
```csv
2025-12-23 00:00:00,25.3,28.1,22.5,45,2.8,12,720.5,3.65,3.70,3.60,5,2,150.2,85.5,98.2,...
2025-12-23 00:05:00,25.4,28.2,22.6,46,2.9,13,721.0,3.66,3.71,3.61,5,2,151.0,85.6,98.1,...
```

**특징:**
- **시간 컬럼:** 첫 번째 컬럼은 항상 `time` (KST 기준)
- **태그 순서:** 채널별 태그 파일(`bsc_ch_01_tags.txt`) 순서와 동일
- **실시간 append:** 새 데이터는 파일 끝에 추가
- **인코딩:** UTF-8

### 4.3 저장 로직 (폴더 구조 2.0.0)

```python
# api_collector/storage.py

from pathlib import Path
import csv

def save_batch_data(channel, date, timestamp, values):
    """
    배치 데이터를 CSV에 저장

    Args:
        channel: 채널명 (예: 'BSC_CH_01')
        date: 날짜 (예: '2025-12-23')
        timestamp: 시각 (예: '2025-12-23 09:15:00')
        values: 태그값 딕셔너리 {tag_name: value}
    """
    # 날짜 폴더 생성 (폴더 구조 2.0.0)
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "source" / "api" / date
    data_dir.mkdir(parents=True, exist_ok=True)

    # CSV 파일 경로
    csv_file = data_dir / f"{channel.lower()}.csv"

    # 헤더 확인 (파일 없으면 생성)
    if not csv_file.exists():
        create_csv_with_header(csv_file, channel)

    # 데이터 추가 (append 모드)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # 태그 순서대로 값 정렬
        tag_order = load_tag_order(channel)
        row = [timestamp]
        for tag in tag_order:
            row.append(values.get(tag, ''))  # 값 없으면 빈 문자열

        writer.writerow(row)


def load_tag_order(channel, site="jeju_bess"):
    """
    채널별 태그 순서 로드 (Multi-Site 지원)

    Args:
        channel: 채널명 (예: 'BSC_CH_01')
        site: 사이트명 (예: 'jeju_bess')

    Returns:
        List[str]: 태그 목록
    """
    project_root = Path(__file__).parent.parent
    tag_file = project_root / "data" / "map" / site / f"{channel.lower()}_tags.txt"

    with open(tag_file, 'r', encoding='utf-8') as f:
        tags = [line.strip() for line in f if line.strip()]

    return tags
```

---

## 5. UI/UX 설계

### 5.1 Slm 화면 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│  GEM - 데이터 수집                                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  [데이터 소스 선택]                                       │
│  ○ CSV 파일 직접 로드                                    │
│  ○ API - 과거 데이터 수집                                │
│  ● API - 실시간 수집                                     │
│                                                           │
├─────────────────────────────────────────────────────────┤
│  [API 설정]                              [기본값 복원]    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ API URL:      [https://hndc-xd.twoz.kr/...]    │   │
│  │ Project ID:   [f92984a4-8427-4990-...]         │   │
│  │                                                  │   │
│  │ 배치 크기:    [15  ▼] 개                        │   │
│  │ 배치 딜레이:  [1.0 ▼] 초                        │   │
│  │ 수집 주기:    [15  ▼] 초                        │   │
│  │ 집계 간격:    [5m  ▼]                           │   │
│  │                                                  │   │
│  │ [설정 저장]                                      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  [사이트 선택]                          🆕 Multi-Site    │
│  ● 제주 BESS (jeju_bess) - 6개 채널, 4860개 태그        │
│  ○ 부산 BESS (busan_bess) - 4개 채널, 3200개 태그       │
│                                                           │
│  [채널 선택]  (선택된 사이트: 제주 BESS)                 │
│  ☑ BSC_CH_01 (810개 태그)                               │
│  ☑ BSC_CH_02 (810개 태그)                               │
│  ☑ BSC_CH_03 (810개 태그)                               │
│  ☑ BSC_CH_04 (810개 태그)                               │
│  ☑ BSC_CH_05 (810개 태그)                               │
│  ☑ BSC_CH_06 (810개 태그)                               │
│  [전체 선택] [전체 해제]                                 │
│                                                           │
├─────────────────────────────────────────────────────────┤
│  [실시간 상태]                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 상태: ● 수집 중                                  │   │
│  │                                                  │   │
│  │ 현재 채널:    BSC_CH_03                         │   │
│  │ 배치 진행:    25/41 (61%)                       │   │
│  │ ████████████░░░░░░░░                            │   │
│  │                                                  │   │
│  │ 마지막 수집:  2025-12-23 16:35:45               │   │
│  │ 수집 레코드:  3,250개                            │   │
│  │ 에러:        0건                                 │   │
│  │                                                  │   │
│  │ API 응답:    250ms 🟢 정상                       │   │
│  │ 서버 상태:   🟢 정상                             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  [시작]  [정지]  [CSV 저장 위치: GEM/data/source/api/]   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 5.2 상태 표시

**수집 중:**
```
● 수집 중 (녹색 점멸)
현재 채널: BSC_CH_03
배치: 25/41 (61%)
████████████░░░░░░░░
```

**정지:**
```
○ 정지됨 (회색)
마지막 수집: 2025-12-23 16:35:45
```

**에러:**
```
⚠️ 경고 (노란색)
API 응답 느림 (2.5초)
배치 딜레이 자동 증가: 1.5초
```

**심각한 에러:**
```
🔴 오류 (빨간색)
서버 오류 (500)
수집 일시 중지
```

### 5.3 프롬프트 예시

#### 과거 수집 완료
```
┌──────────────────────────────────────┐
│  데이터 수집 완료!                    │
├──────────────────────────────────────┤
│                                       │
│  날짜: 2025-12-20                    │
│  수집 레코드: 1,440개                 │
│  시간 범위: 00:00 ~ 23:59            │
│  집계 간격: 5분                       │
│                                       │
│  지금 분석을 진행하시겠습니까?         │
│                                       │
│         [예]         [아니오]         │
│                                       │
└──────────────────────────────────────┘
```

#### 갭 감지
```
┌──────────────────────────────────────┐
│  데이터 누락 감지                     │
├──────────────────────────────────────┤
│                                       │
│  누락 구간:                           │
│  09:15 ~ 11:30 (2시간 15분)          │
│                                       │
│  누락 레코드: 약 27개 (5분 간격)      │
│                                       │
│  이 구간을 채우시겠습니까?             │
│                                       │
│    [예]    [아니오]    [무시하고 계속] │
│                                       │
└──────────────────────────────────────┘
```

---

## 6. 기술 사양

### 6.1 API 스펙

**엔드포인트:**
```
GET https://hndc-xd.twoz.kr/runtime-api/runtime/historian/get-data-list
```

**요청 파라미터:**
| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---------|------|------|------|------|
| aggTime | string | Y | 집계 간격 | 1m, 5m, 10m, 30m, 1h |
| startDt | string | Y | 시작 시각 | 2025-12-23 00:00:00 |
| endDt | string | Y | 종료 시각 | 2025-12-23 23:59:59 |
| excludeZero | boolean | Y | 0값 제외 | false |
| fillWithPreviousValue | boolean | Y | 이전값 채우기 | false |
| searchType | string | Y | 검색 타입 | TAG |
| tagFullName | string | Y | 태그 리스트 | TAG1,TAG2,TAG3 |

**요청 헤더:**
```
proj-id: f92984a4-8427-4990-a7fa-574847436804
accept: application/json, text/plain, */*
```

**응답 형식:**
```json
{
  "BSC_CH_01.BANK_01.RACK_01.MOD_AVG_TEMP": {
    "records": [
      {"time": "2025-12-23T00:00:00Z", "value": 25.3},
      {"time": "2025-12-23T00:05:00Z", "value": 25.4},
      ...
    ]
  },
  "BSC_CH_01.BANK_01.RACK_01.MOD_MAX_TEMP": {
    "records": [...]
  },
  ...
}
```

### 6.2 성능 목표

| 항목 | 목표 | 비고 |
|------|------|------|
| API 응답 시간 | < 1초 | 정상 상태 |
| 배치 처리 시간 | ~21초 | 41배치 × 0.5초 |
| 채널당 수집 시간 | ~24초 | 배치 + 오버헤드 |
| 전체 사이클 | ~2.5분 | 6개 채널 순차 |
| 실시간 주기 | 15초 | 설정 가능 |
| 동시 요청 수 | 1개 | 고정 |

### 6.3 데이터 볼륨

**하루 데이터 (5분 간격):**
```
시간 포인트: 24시간 × 60분 ÷ 5분 = 288개
채널당 태그: 810개
채널당 레코드: 288 × 810 = 233,280개 값

전체 (6채널): 233,280 × 6 = 1,399,680개 값
CSV 크기 (예상): ~50MB/일 (압축 전)
```

---

## 7. 에러 처리

### 7.1 에러 분류

#### Level 1: 경고 (자동 복구)
```python
# API 응답 느림
if response_time > 2.0:
    log_warning(f"API 응답 느림: {response_time}초")
    auto_adjust_delay()  # 딜레이 자동 증가

# 일시적 네트워크 오류
if connection_error:
    retry_with_backoff(max_retries=3)
```

#### Level 2: 에러 (사용자 알림)
```python
# 429 Too Many Requests
if status_code == 429:
    show_notification("서버 부하 감지. 30초 대기 중...")
    wait(30)
    retry()

# 타임아웃
if timeout_error:
    show_notification("API 타임아웃. 재시도 중...")
    retry()
```

#### Level 3: 심각 (즉시 중단)
```python
# 500 Internal Server Error
if status_code == 500:
    pause_collection()
    show_error("서버 오류로 수집 중지. 재시도하시겠습니까?")
    wait_user_action()

# 인증 오류
if status_code == 401:
    stop_collection()
    show_error("인증 오류. API 설정을 확인하세요.")
```

### 7.2 로그 기록 (폴더 구조 2.0.0)

```
GEM/logs/
└── api_collection/                 # 🆕 API 수집 로그 폴더
    ├── 2025-12-23.log             # 날짜별 수집 로그
    │   2025-12-23 09:00:00 [INFO] Collection started (realtime mode)
    │   2025-12-23 09:00:01 [INFO] CH_01 batch 1/41 completed (250ms)
    │   2025-12-23 09:00:02 [INFO] CH_01 batch 2/41 completed (280ms)
    │   2025-12-23 09:15:30 [WARN] API response slow (2.5s)
    │   2025-12-23 09:15:31 [INFO] Auto-adjusted delay to 1.5s
    │   2025-12-23 10:30:00 [ERROR] Server error 500
    │   2025-12-23 10:30:01 [INFO] Collection paused
    │
    └── 2025-12-20.log             # 과거 수집 로그
        2025-12-20 10:00:00 [INFO] Historical collection started
        2025-12-20 10:00:01 [INFO] Date: 2025-12-20, Mode: full_day
        2025-12-20 10:04:32 [INFO] All channels completed (243 batches)
        2025-12-20 10:04:33 [INFO] Total records: 1,440
```

---

## 8. 구현 체크리스트

### 8.1 모듈 개발
- [x] `api_collector/config.py` - 설정 로드/저장 ✅
- [x] `api_collector/historical.py` - 과거 데이터 수집 ✅
- [x] `api_collector/realtime.py` - 실시간 수집 ✅
- [x] `api_collector/storage.py` - CSV 저장 ✅
- [ ] `api_collector/monitor.py` - 상태 모니터링 (기본 구현 완료)

### 8.2 UI 개발 (FastAPI 기반)
- [x] 데이터 소스 선택 라디오 버튼 ✅
- [x] API 설정 폼 ✅
- [x] 채널 선택 체크박스 ✅
- [x] 실시간 상태 표시 패널 ✅
- [x] 시작/정지 버튼 ✅
- [x] 프롬프트 대화상자 ✅

### 8.3 기능 개발
- [x] 과거 데이터 수집 로직 ✅
- [x] 실시간 수집 스레드 ✅
- [ ] 갭 감지 및 채우기 (부분 구현)
- [ ] 자정 자동 전환 (설계 완료)
- [x] 배치 처리 및 딜레이 ✅
- [x] 에러 처리 및 재시도 ✅

### 8.4 테스트
- [x] 과거 수집 테스트 ✅
- [x] 실시간 수집 테스트 ✅
- [ ] 정지/재개 테스트 (기본 구현)
- [ ] 갭 채우기 테스트 (미구현)
- [ ] 에러 시나리오 테스트 (부분 테스트)
- [ ] 부하 테스트 (기본 검증 완료)

---

## 9. 실행 예제 (폴더 구조 2.0.0)

### 9.1 과거 데이터 수집

```bash
# 웹 UI 실행
cd D:\0001_project\RFS\GEM
python main.py

# 브라우저에서 http://localhost:8000 접속
# "API 수집" 탭 선택
# "과거 데이터 수집" 선택
# 날짜: 2025-12-20
# 채널: BSC_CH_01~06 전체 선택
# "수집 시작" 클릭

# 결과 확인
# → data/source/api/2025-12-20/ 폴더에 6개 CSV 파일 생성
# → logs/api_collection/2025-12-20.log 로그 파일 생성
```

**생성된 파일:**
```
GEM/data/source/api/2025-12-20/
├── bsc_ch_01.csv (약 8MB, 288행 × 810컬럼)
├── bsc_ch_02.csv
├── bsc_ch_03.csv
├── bsc_ch_04.csv
├── bsc_ch_05.csv
└── bsc_ch_06.csv
```

### 9.2 실시간 수집

```bash
# 웹 UI에서
# "API 수집" 탭 → "실시간 수집" 선택
# 채널: BSC_CH_01~06 전체 선택
# 집계 간격: 5m
# "수집 시작" 클릭

# 실시간으로 데이터가 추가됨
# → data/source/api/2025-12-23/ 폴더에 append 모드로 저장
# → 5분마다 새로운 행 추가
# → 웹 UI에서 실시간 진행 상황 표시
```

**실행 중 화면:**
```
상태: ● 수집 중
현재 채널: BSC_CH_03
배치 진행: 25/41 (61%)
████████████░░░░░░░░

마지막 수집: 2025-12-23 16:35:45
수집 레코드: 3,250개
에러: 0건

API 응답: 250ms 🟢 정상
```

### 9.3 수집된 데이터로 GEM 분석 실행

```bash
# 웹 UI 메인 화면에서
# "데이터 소스" → "API 수집 데이터" 선택
# 날짜 선택: 2025-12-20
# 배터리 프로파일: LFP_CATL
# "Phase 1-4 전체 실행" 클릭

# 분석 결과 확인
# → results/20251220_100000_LFP_CATL/
#    ├── metadata.json
#    ├── phase1_convert/
#    ├── phase2_validate/
#    ├── phase3_insights/
#    └── phase4_report/report.html
```

### 9.4 프로그래매틱 실행 (Python API)

```python
# API 수집 모듈 직접 사용
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent / "GEM"))

from api_collector.historical import HistoricalCollector
from api_collector.config import API_CONFIG

# 과거 데이터 수집
collector = HistoricalCollector(config=API_CONFIG)

result = collector.collect_date(
    date="2025-12-20",
    channels=["BSC_CH_01", "BSC_CH_02", "BSC_CH_03",
              "BSC_CH_04", "BSC_CH_05", "BSC_CH_06"],
    agg_time="5m"
)

print(f"수집 완료: {result['total_records']}개 레코드")
print(f"저장 위치: {result['output_dir']}")
# → data/source/api/2025-12-20/
```

---

## 10. 구현 상태 요약 (2025-12-26)

### ✅ 완료된 기능
1. **API 수집 모듈** - 완전 구현
   - 과거 데이터 수집 (날짜 범위 지정)
   - 실시간 데이터 수집 (5분 간격)
   - 배치 처리 (20개/배치, 1초 딜레이)
   - 채널별 선택 수집

2. **폴더 구조 2.0.0** - 적용 완료
   - `data/source/api/` - API 수집 데이터
   - `data/tags/` - 채널별 태그 정의
   - `logs/api_collection/` - 날짜별 로그

3. **웹 UI (FastAPI)** - 구현 완료
   - API 수집 인터페이스
   - 실시간 진행 상황 표시
   - WebSocket 기반 로그 스트리밍

4. **GEM 연동** - 완료
   - API 수집 데이터 → GEM 분석 파이프라인
   - 자동 파일 인식 및 로드
   - Phase 1-4 실행

### ⚠️ 부분 구현 / 개선 필요
1. **갭 감지 및 복구** - 설계 완료, 구현 대기
2. **자정 자동 전환** - 로직 설계, 테스트 필요
3. **서버 부하 자동 조절** - 기본 구현, 튜닝 필요
4. **모니터링 대시보드** - 기본 상태 표시, 고도화 필요

### 🔄 향후 개선 사항
1. **성능 최적화**
   - 비동기 배치 처리 (asyncio)
   - 멀티스레드 채널 수집
   - 메모리 효율화

2. **모니터링 강화**
   - 실시간 그래프 (Chart.js)
   - 알람 시스템 (이메일/Slack)
   - 성능 메트릭 수집

3. **안정성 향상**
   - 네트워크 재연결 로직
   - 데이터 무결성 검증
   - 백업 및 복구 시스템

---

**문서 버전:** 2.0.0 (폴더 구조 개선 반영)
**최종 수정:** 2025-12-26
**작성자:** GEM Development Team
