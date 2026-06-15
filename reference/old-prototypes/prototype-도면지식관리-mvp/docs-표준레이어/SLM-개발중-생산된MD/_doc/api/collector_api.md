# API 데이터 수집 모듈

제주 장주기 배터리 시스템 데이터를 XD Runtime Historian API를 통해 수집합니다.

## 주요 기능

- **과거 데이터 수집**: 특정 날짜의 전체 데이터 수집 (00:00 ~ 23:59)
- **실시간 수집**: 집계 간격에 맞춘 지속적 데이터 수집
- **데이터 갭 자동 감지 및 채우기**: 누락된 시간 포인트 자동 보완
- **서버 부하 방지**: 배치 처리 및 딜레이 적용
- **상태 모니터링**: 실시간 수집 상태 추적
- **설정 관리**: JSON 파일 기반 설정 (UI에서 편집 가능)

## 모듈 구조

```
api_collector/
├── __init__.py          # 패키지 초기화
├── config.py            # API 설정 관리 (JSON)
├── storage.py           # CSV 저장 및 append
├── monitor.py           # 수집 상태 모니터링
├── historical.py        # 과거 데이터 수집
├── realtime.py          # 실시간 데이터 수집
├── demo.py              # 데모 스크립트
└── README.md            # 이 문서
```

## 설정 파일

설정은 `GEM/config/api_config.json`에 저장됩니다:

```json
{
  "api_url": "https://hndc-xd.twoz.kr/runtime-api/runtime/historian/get-data-list",
  "proj_id": "f92984a4-8427-4990-a7fa-574847436804",
  "batch_size": 20,
  "batch_delay": 1.0,
  "agg_time": "5m",
  "timeout": 30,
  "retry_count": 3,
  "retry_delay": 5
}
```

### 주요 설정 항목

- `api_url`: API 엔드포인트
- `proj_id`: 프로젝트 ID
- `batch_size`: 배치당 태그 수 (20 권장)
- `batch_delay`: 배치 간 딜레이 (초)
- `agg_time`: 집계 간격 (1m, 5m, 10m, 30m, 1h)
- `timeout`: API 타임아웃 (초)

## 사용법

### 1. 과거 데이터 수집

특정 날짜의 전체 데이터를 한 번에 수집합니다.

```python
from api_collector import HistoricalCollector, APIConfig, DataStorage, CollectionMonitor

# 설정
config = APIConfig()
storage = DataStorage()
monitor = CollectionMonitor()

# 수집기 생성
collector = HistoricalCollector(config, storage, monitor)

# 수집 실행
results = collector.collect_date(
    date="2025-12-20",
    channels=["BSC_CH_01", "BSC_CH_02"]  # None이면 전체 6개 채널
)
```

**명령줄:**
```bash
python -m api_collector.demo --mode historical --date 2025-12-20
```

### 2. 실시간 수집

집계 간격에 맞춰 지속적으로 데이터를 수집합니다.

```python
from api_collector import RealtimeCollector, APIConfig, DataStorage, CollectionMonitor

# 설정
config = APIConfig()
storage = DataStorage()
monitor = CollectionMonitor()

# 수집기 생성
collector = RealtimeCollector(config, storage, monitor)

# 연속 실행 (Ctrl+C로 중지)
collector.run_continuous(
    channels=None  # 전체 채널
)
```

**명령줄:**
```bash
python -m api_collector.demo --mode realtime
```

### 3. 설정 수정

```python
from api_collector import APIConfig

# 설정 로드
config = APIConfig()

# 값 수정
config.set('agg_time', '10m')
config.set('batch_size', 30)

# 저장
config.save()

# 기본값 복원
config.reset_to_default()
```

## 데이터 구조

### 채널 구조
- **6개 채널**: BSC_CH_01 ~ BSC_CH_06
- **각 채널당 810개 태그** (4 BANK × 13~14 RACK × 15 패턴)
- **총 4,860개 태그**

### CSV 출력
```
GEM/data/csv/
├── 2025-12-20/
│   ├── BSC_CH_01.csv
│   ├── BSC_CH_02.csv
│   ├── ...
│   └── BSC_CH_06.csv
└── 2025-12-21/
    └── ...
```

**CSV 형식:**
```csv
time,BSC_CH_01.BANK_01.RACK_01.MOD_AVG_TEMP,BSC_CH_01.BANK_01.RACK_01.MOD_MAX_TEMP,...
2025-12-20 00:00:00,25.3,26.1,...
2025-12-20 00:05:00,25.4,26.2,...
```

## 주요 개념

### 집계 간격 (agg_time)

API는 지정된 간격으로 데이터를 집계합니다:

- `1m`: 1분 간격
- `5m`: 5분 간격 (기본값)
- `10m`: 10분 간격
- `30m`: 30분 간격
- `1h`: 1시간 간격

### 수집 주기 = 집계 간격

**중요:** 실시간 수집 주기는 집계 간격과 동일해야 합니다.

- 집계 간격 5분 → 5분마다 수집
- 집계 간격 1분 → 1분마다 수집

더 짧은 주기로 수집하면 중복 데이터가 반환됩니다.

### 시간 정렬

실시간 수집 시 현재 시간을 집계 간격 경계에 맞춰 정렬합니다:

```
현재 시간: 09:17:32
집계 간격: 5m
정렬 시간: 09:15:00
```

### 배치 처리

서버 부하 방지를 위해 태그를 배치로 나눠 처리합니다:

- 배치 크기: 20개 태그 (권장)
- 배치 간 딜레이: 1초
- 채널 순차 처리: 6개 채널을 하나씩 처리

### 데이터 갭 처리

실시간 수집 시 누락된 데이터를 자동으로 감지하고 채웁니다:

1. CSV 파일의 마지막 시각 확인
2. 현재 시각까지 누락된 포인트 계산
3. 누락된 시점의 데이터를 API로 요청
4. CSV에 추가

## 모니터링

### 수집 상태

```python
monitor = CollectionMonitor()

# 상태 확인
print(monitor.get_status_text())      # "● 수집 중"
print(monitor.get_progress_percentage())  # 65.5
print(monitor.get_elapsed_time())     # "00:05:23"

# 요약 정보
summary = monitor.get_summary()
# {
#   "status": "● 수집 중",
#   "current_channel": "BSC_CH_03",
#   "batch_progress": "25/41",
#   "total_records": 1250,
#   "server_health": "🟢 정상",
#   ...
# }
```

### 서버 상태

API 응답 시간에 따라 서버 상태를 표시합니다:

- 🟢 정상: < 2초
- 🟡 느림: 2~5초
- 🔴 위험: > 5초

## UI 연동

### Streamlit 통합 예제

```python
import streamlit as st
from api_collector import RealtimeCollector, APIConfig, DataStorage, CollectionMonitor

# 세션 상태 초기화
if 'monitor' not in st.session_state:
    st.session_state.monitor = CollectionMonitor()
    st.session_state.collector = RealtimeCollector()

# 수집 제어
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("시작"):
        st.session_state.monitor.start_collection()
with col2:
    if st.button("일시정지"):
        st.session_state.monitor.pause_collection()
with col3:
    if st.button("재개"):
        st.session_state.monitor.resume_collection()

# 상태 표시
summary = st.session_state.monitor.get_summary()
st.metric("상태", summary['status'])
st.metric("진행률", f"{summary['progress_percentage']:.1f}%")
st.metric("서버 상태", summary['server_health'])

# 설정 편집
with st.expander("설정"):
    config = APIConfig()

    agg_time = st.selectbox("집계 간격", ["1m", "5m", "10m", "30m", "1h"],
                            index=1)
    batch_size = st.number_input("배치 크기", value=20, min_value=10, max_value=50)

    if st.button("저장"):
        config.set('agg_time', agg_time)
        config.set('batch_size', batch_size)
        config.save()
        st.success("설정 저장됨")
```

## 에러 처리

### API 오류

- HTTP 400/500 에러: 재시도 로직 적용
- 타임아웃: 설정에서 timeout 조정
- 네트워크 오류: 자동 재시도 (retry_count)

### 데이터 저장 오류

- 디렉토리 없음: 자동 생성
- 파일 권한 오류: 로그 출력 및 건너뛰기
- 디스크 공간 부족: 에러 상태로 전환

## 참고 자료

- 상세 설계 문서: `_dev/16_API-데이터-수집-시스템.md`
- 태그 리스트: `data/bsc_ch_01_tags.txt` ~ `bsc_ch_06_tags.txt`
- 참고 구현: `D:\0001_project\git\acs-data-utils\xd\get_trends.py`

## 테스트

각 모듈은 독립적으로 테스트 가능합니다:

```bash
# Config 테스트
python -m api_collector.config

# Storage 테스트
python -m api_collector.storage

# Monitor 테스트
python -m api_collector.monitor

# Historical 테스트
python -m api_collector.historical

# Realtime 테스트
python -m api_collector.realtime
```

## 버전 이력

- **1.0.0** (2025-12-23): 초기 구현
  - 과거 데이터 수집
  - 실시간 데이터 수집
  - 데이터 갭 감지 및 채우기
  - JSON 기반 설정 관리
  - 상태 모니터링

## 라이선스

Copyright (c) 2025 TWENTYOZ. All rights reserved.
