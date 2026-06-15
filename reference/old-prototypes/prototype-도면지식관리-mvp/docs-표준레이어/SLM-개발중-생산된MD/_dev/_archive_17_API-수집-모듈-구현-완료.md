# API 수집 모듈 구현 완료

**작성일:** 2025-12-23
**버전:** 1.0.0
**모듈 경로:** `GEM/api_collector/`

---

## 구현 완료 항목

### ✅ 1. 모듈 구조

```
GEM/api_collector/
├── __init__.py          # 패키지 초기화 및 export
├── config.py            # API 설정 관리 (JSON 기반)
├── storage.py           # CSV 저장 및 append 로직
├── monitor.py           # 수집 상태 모니터링
├── historical.py        # 과거 데이터 수집
├── realtime.py          # 실시간 데이터 수집
├── demo.py              # CLI 데모 스크립트
└── README.md            # 모듈 사용 설명서
```

### ✅ 2. 핵심 기능

#### A. 설정 관리 (config.py)
- JSON 파일 기반 설정 (`GEM/config/api_config.json`)
- UI에서 편집 가능
- 기본값 복원 기능
- 집계 간격 정보 제공

**주요 메서드:**
```python
config = APIConfig()
config.get('agg_time')              # 설정값 조회
config.set('batch_size', 30)        # 설정값 변경
config.save()                       # 파일 저장
config.reset_to_default()           # 기본값 복원
config.get_collection_interval_seconds()  # 수집 주기(초)
```

#### B. 데이터 저장 (storage.py)
- 날짜별 폴더 자동 생성 (`GEM/data/csv/YYYY-MM-DD/`)
- 채널별 CSV 파일 관리
- Append 모드 지원 (실시간 수집용)
- 태그 순서 관리 (파일 기반)

**주요 메서드:**
```python
storage = DataStorage()
storage.get_csv_path(channel, date)           # CSV 경로
storage.save_batch_data(...)                  # 단일 시점 저장 (append)
storage.save_multiple_timepoints(...)         # 다중 시점 저장
storage.get_last_timestamp(channel, date)     # 마지막 시각
storage.check_data_gap(...)                   # 갭 확인
```

#### C. 상태 모니터링 (monitor.py)
- 실시간 수집 상태 추적
- API 응답 시간 측정
- 서버 건강도 판단
- 진행률 계산

**상태 종류:**
- `IDLE`: 대기
- `RUNNING`: 수집 중
- `PAUSED`: 일시 중지
- `COMPLETED`: 완료
- `ERROR`: 에러

**서버 건강도:**
- 🟢 정상: < 2초
- 🟡 느림: 2~5초
- 🔴 위험: > 5초

#### D. 과거 데이터 수집 (historical.py)
- 특정 날짜 전체 데이터 수집 (00:00 ~ 23:59)
- 배치 처리 (태그를 20개씩 분할)
- 배치 간 딜레이 (서버 부하 방지)
- 채널 순차 처리 (6개 채널)
- 진행 콜백 지원

**사용 예:**
```python
collector = HistoricalCollector(config, storage, monitor)
results = collector.collect_date(
    date="2025-12-20",
    channels=["BSC_CH_01", "BSC_CH_02"],
    progress_callback=my_callback
)
```

#### E. 실시간 수집 (realtime.py)
- 집계 간격에 맞춘 주기적 수집
- 시간 정렬 (aggregation boundary alignment)
- 데이터 갭 자동 감지 및 채우기
- 자정 날짜 전환 자동 처리
- 일시 중지/재개 지원

**핵심 로직:**
```python
# 1. 시간 정렬
aligned_time = collector.align_time_to_interval(now, agg_time)
# 09:17:32 → 09:15:00 (5m 간격)

# 2. 다음 수집 시각 계산
next_time = collector.get_next_collection_time(current, agg_time)

# 3. 갭 확인 및 채우기
gap_times = collector.check_data_gap(channel, current_time)
collector.fill_data_gap(channel, gap_times, agg_time)

# 4. 현재 시점 수집
collector.collect_timepoint(channel, collection_time, agg_time)
```

---

## 주요 설계 원칙

### 1. 수집 주기 = 집계 간격

**중요한 개념:**
- API의 `aggTime` 파라미터는 서버가 데이터를 집계하는 간격
- 실시간 수집 주기는 이 간격과 **반드시 동일**해야 함
- 더 짧은 주기로 수집하면 중복 데이터 반환

**예:**
```
aggTime = 5m
→ 5분마다 수집해야 함 (15초마다 수집하면 중복)

aggTime = 1m
→ 1분마다 수집해야 함
```

### 2. 시간 정렬

실시간 수집 시 현재 시간을 집계 간격 경계에 맞춰 정렬:

```python
now = datetime(2025, 12, 23, 9, 17, 32)
agg_time = "5m"

# 정렬 로직
aligned_minute = (17 // 5) * 5  # = 15
aligned = now.replace(minute=15, second=0, microsecond=0)
# → 2025-12-23 09:15:00
```

### 3. 배치 처리

**서버 부하 방지:**
- 태그를 배치로 분할 (기본 20개)
- 배치 간 딜레이 적용 (기본 1초)
- 채널 순차 처리 (병렬 X)

**처리 순서:**
```
BSC_CH_01 → 41개 배치 (810개 태그 ÷ 20)
  배치 1/41 → API 호출 → 1초 대기
  배치 2/41 → API 호출 → 1초 대기
  ...
  배치 41/41 → API 호출
BSC_CH_02 → 41개 배치
  ...
BSC_CH_06 → 41개 배치
```

### 4. 데이터 갭 처리

**과거 데이터 수집:**
- 시간 범위 고정 (00:00 ~ 23:59)
- 태그만 배치로 분할
- Overwrite 모드

**실시간 수집:**
- 마지막 타임스탬프 확인
- 누락된 시점 계산
- Historical 수집으로 채우기
- Append 모드

---

## 사용 방법

### CLI 사용

```bash
# 과거 데이터 수집
python -m api_collector.demo --mode historical --date 2025-12-20

# 특정 채널만
python -m api_collector.demo --mode historical --date 2025-12-20 \
  --channels BSC_CH_01 BSC_CH_02

# 실시간 수집 (Ctrl+C로 중지)
python -m api_collector.demo --mode realtime

# 설정 파일 사용
python -m api_collector.demo --mode realtime --config custom_config.json
```

### Python 코드

```python
from api_collector import (
    APIConfig, DataStorage, CollectionMonitor,
    HistoricalCollector, RealtimeCollector
)

# 설정
config = APIConfig()
storage = DataStorage()
monitor = CollectionMonitor()

# 과거 데이터 수집
hist = HistoricalCollector(config, storage, monitor)
results = hist.collect_date(date="2025-12-20")

# 실시간 수집
rt = RealtimeCollector(config, storage, monitor)
rt.run_continuous()
```

---

## UI 통합 가이드

### Streamlit 연동 예제

```python
import streamlit as st
from api_collector import APIConfig, CollectionMonitor, RealtimeCollector

# 세션 상태
if 'monitor' not in st.session_state:
    st.session_state.monitor = CollectionMonitor()
    st.session_state.collector = RealtimeCollector(
        monitor=st.session_state.monitor
    )

# 제어 버튼
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("▶ 시작"):
        st.session_state.monitor.start_collection()
with col2:
    if st.button("⏸ 일시정지"):
        st.session_state.monitor.pause_collection()
with col3:
    if st.button("⏹ 중지"):
        st.session_state.monitor.complete_collection()

# 상태 표시
summary = st.session_state.monitor.get_summary()

st.metric("상태", summary['status'])
st.metric("현재 채널", summary['current_channel'])
st.metric("진행률", f"{summary['progress_percentage']:.1f}%")

col1, col2, col3 = st.columns(3)
col1.metric("총 레코드", f"{summary['total_records']:,}")
col2.metric("경과 시간", summary['elapsed_time'])
col3.metric("서버 상태", summary['server_health'])

# 설정 편집
with st.expander("⚙ 설정"):
    config = APIConfig()

    agg_time = st.selectbox(
        "집계 간격",
        ["1m", "5m", "10m", "30m", "1h"],
        index=["1m", "5m", "10m", "30m", "1h"].index(config.get('agg_time'))
    )

    batch_size = st.number_input(
        "배치 크기",
        value=config.get('batch_size'),
        min_value=10,
        max_value=50
    )

    batch_delay = st.number_input(
        "배치 딜레이 (초)",
        value=config.get('batch_delay'),
        min_value=0.1,
        max_value=5.0,
        step=0.1
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 저장"):
            config.set('agg_time', agg_time)
            config.set('batch_size', batch_size)
            config.set('batch_delay', batch_delay)
            config.save()
            st.success("설정 저장됨")

    with col2:
        if st.button("🔄 기본값 복원"):
            config.reset_to_default()
            st.success("기본값으로 복원됨")
            st.rerun()
```

### 데이터 소스 선택 UI

```python
import streamlit as st

st.header("데이터 소스 선택")

source_type = st.radio(
    "데이터 소스",
    ["API 수집 데이터", "수동 업로드 CSV"],
    horizontal=True
)

if source_type == "API 수집 데이터":
    # 날짜 선택
    date = st.date_input("날짜 선택")

    # 채널 선택
    channels = st.multiselect(
        "채널 선택",
        [f"BSC_CH_{i:02d}" for i in range(1, 7)],
        default=[f"BSC_CH_{i:02d}" for i in range(1, 7)]
    )

    # 데이터 존재 여부 확인
    from api_collector import DataStorage
    storage = DataStorage()

    date_str = date.strftime('%Y-%m-%d')
    available_channels = []

    for channel in channels:
        csv_path = storage.get_csv_path(channel, date_str)
        if csv_path.exists():
            size = storage.get_file_size(channel, date_str)
            available_channels.append({
                'channel': channel,
                'size': size,
                'records': sum(1 for _ in open(csv_path)) - 1  # 헤더 제외
            })

    # 사용 가능한 데이터 표시
    if available_channels:
        st.success(f"✅ {len(available_channels)}개 채널 데이터 발견")

        import pandas as pd
        df = pd.DataFrame(available_channels)
        df['size_kb'] = df['size'] / 1024
        st.dataframe(df[['channel', 'records', 'size_kb']])

        if st.button("이 데이터로 분석 시작"):
            # TODO: 분석 페이지로 이동
            pass
    else:
        st.warning("⚠ 선택한 날짜/채널의 데이터가 없습니다.")

        if st.button("지금 수집하기"):
            # TODO: 수집 실행
            pass

else:
    # CSV 파일 업로드
    uploaded_file = st.file_uploader("CSV 파일 선택", type=['csv'])

    if uploaded_file:
        # TODO: CSV 로드 및 검증
        pass
```

---

## 다음 단계

### 1. UI 통합 (Slm.py)
- [ ] 데이터 소스 선택 UI
- [ ] 수집 제어 UI (시작/중지/재개)
- [ ] 상태 모니터링 대시보드
- [ ] 설정 편집 UI
- [ ] 과거 데이터 수집 실행 UI

### 2. 완료 프롬프트 처리
- [ ] 과거 수집 완료 후 사용자 확인
- [ ] 분석 작업 연결

### 3. 추가 기능
- [ ] 로그 파일 저장
- [ ] 수집 이력 관리
- [ ] 에러 알림 (이메일/슬랙)
- [ ] 데이터 품질 검증

### 4. 테스트
- [ ] 단위 테스트 작성
- [ ] 통합 테스트
- [ ] 실제 API 연동 테스트

---

## 파일 경로 정리

### 소스 코드
```
D:\0001_project\RFS\GEM\api_collector\
├── __init__.py
├── config.py
├── storage.py
├── monitor.py
├── historical.py
├── realtime.py
├── demo.py
└── README.md
```

### 설정 파일
```
D:\0001_project\RFS\GEM\config\
└── api_config.json
```

### 데이터 파일
```
D:\0001_project\RFS\GEM\data\
├── bsc_ch_01_tags.txt  ~ bsc_ch_06_tags.txt  (810개씩)
├── all_channels_tags.json  (4,860개)
└── csv\
    ├── 2025-12-20\
    │   ├── BSC_CH_01.csv
    │   └── ...
    └── 2025-12-21\
        └── ...
```

### 문서
```
D:\0001_project\RFS\_dev\
├── 14_필수태그-전체-리스트.md
├── 15_채널별-필수태그-전체.md
├── 16_API-데이터-수집-시스템.md
└── 17_API-수집-모듈-구현-완료.md  (이 문서)
```

---

**구현 완료일:** 2025-12-23
**버전:** 1.0.0
**개발자:** Claude Code
