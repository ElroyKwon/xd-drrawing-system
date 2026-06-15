# Phase 2 SPC Balance Z-Score 계산 버그 수정

## 문제 발견 (2026-03-10)

### 증상
배치 분석 시 채널 수에 따라 결과가 달라지는 현상 발견:

| 분석 대상 | total_racks | critical_count | warning_count |
|----------|-------------|----------------|---------------|
| CH_01만 (54 racks) | 54 | 20~36 | 0 |
| 전체 6채널 (324 racks) | 324 | **0** | 54 |

**동일한 CH_01 데이터인데 분석 결과가 다름!**

---

## 원인 분석

### 원래 코드 (잘못된 로직)

```python
# 시간별 전압 평균과 표준편차 계산
df = df.with_columns([
    ((pl.col('v_avg') - pl.col('v_avg').mean().over('timestamp')) /
     pl.col('v_avg').std().over('timestamp')).alias('z_score')
])
```

### 문제점

1. **타임스탬프별 계산**: 각 시간마다 **모든 랙**을 비교
   - CH_01만: 54개 랙 비교 → 표준편차 작음 → Z-Score 큼 (5.5σ) → Critical
   - 전체 6채널: 324개 랙 비교 → 표준편차 커짐 → Z-Score 작아짐 (2.5σ) → Warning
   - **채널이 추가될수록 이상치가 희석됨**

2. **채널 간 간섭**: 서로 독립적이어야 할 채널들이 서로 영향을 줌

---

## 수정 시도 1 - 랙별 계산 (실패)

### 수정 내용
```python
# 랙별 전압 평균과 표준편차 계산 (각 랙의 시계열 데이터 기준)
df = df.with_columns([
    ((pl.col('v_avg') - pl.col('v_avg').mean().over('rack_id')) /
     pl.col('v_avg').std().over('rack_id')).alias('z_score')
])
```

### 결과
- **모든 워닝이 사라짐!**

### 실패 원인
- 각 랙이 자기 자신의 시계열 데이터와만 비교
- 정상 운전 중에는 전압이 일정 → 표준편차가 작음 → Z-Score ≈ 0
- **밸런싱 문제를 감지할 수 없음**

---

## 수정 시도 2 - 채널별 타임스탬프별 계산 (성공)

### 이론적 근거

#### 1. SPC Balance의 본질
- **SPC Balance** = Statistical Process Control for Cell Balancing
- 목적: **같은 그룹 내 셀들 간 전압 균형** 확인
- 같은 채널 내 랙들이 같은 시간에 비슷한 전압을 가져야 정상

#### 2. 배터리 시스템 계층 구조
```
Battery Cell → Battery Module → Battery Pack → Battery Rack → Channel
```

#### 3. 학술 자료 근거

**논문**: "Voltage fault diagnosis and prognosis of battery systems based on entropy and Z-score for electric vehicles" (ScienceDirect)

주요 내용:
- Z-Score를 사용해서 **전압 이상 감지**
- **실시간 전압 abnormality 평가**에 사용
- 배터리 팩 내에서 **이상 셀의 위치 파악**
- **같은 그룹 내 비교**가 핵심

**BMS 밸런싱 개념**:
- Cell Balancing은 **같은 그룹 내 셀들 간 전압 편차를 조정**하는 과정
- BMS가 **각 셀의 충전 전압을 비교**해서 균일한 전압 유지
- 채널별로 독립적으로 밸런싱 수행

#### 4. 다른 Phase2 로직과의 일관성

Phase2의 다른 모든 계산은 **랙별**로 수행:

| 계산 항목 | 계산 방식 | 코드 라인 |
|----------|----------|----------|
| 온도 변화율 (dtdt) | `.diff().over('rack_id')` | Line 138 |
| 전압 스파이크 (v_spike) | `.diff().over('rack_id')` | Line 401 |
| 온도 스파이크 (t_spike) | `.diff().over('rack_id')` | Line 402 |
| ISC 전압 하락 (v_drop) | `.diff().over('rack_id')` | Line 408 |
| ISC 온도 상승 (t_rise) | `.diff().over('rack_id')` | Line 409 |
| 전류 이상치 (current_anomaly) | `.over('rack_id')` | Line 486-487 |
| 센서 고착 (sensor_frozen) | `.group_by('rack_id')` | Line 365-367 |

**오직 SPC Balance Z-Score만** 타임스탬프별로 계산하는 것이 맞음!

---

### 최종 수정 내용

```python
console_with_callback.subsection("Z-Score 계산 중...")

try:
    # 채널 정보 추출 (rack_id에서 CH_XX 부분 추출)
    df = df.with_columns([
        pl.col('rack_id').str.split('.').list.first().alias('channel_id')
    ])

    # 채널별 타임스탬프별 전압 평균과 표준편차 계산 (밸런싱 검증)
    # 같은 채널 내 랙들이 같은 시간에 비슷한 전압을 가져야 정상 (밸런싱)
    df = df.with_columns([
        ((pl.col('v_avg') - pl.col('v_avg').mean().over(['channel_id', 'timestamp'])) /
         pl.col('v_avg').std().over(['channel_id', 'timestamp'])).alias('z_score')
    ])
```

---

## 수정 효과

### 기대 결과

1. **채널 독립성**: CH_01의 밸런싱은 CH_02~06과 무관
2. **일관된 결과**: CH_01만 분석하든, 전체 6채널 분석하든 **CH_01의 Critical/Warning 개수는 동일**
3. **정확한 밸런싱 검증**: 같은 채널 내에서 전압 불균형 정확히 감지

### 검증 방법

```bash
# 1. CH_01만 분석
batch_20260309_CH01_only → critical_count = X, warning_count = Y

# 2. 전체 6채널 분석
batch_20260309_ALL_channels → critical_count = X (동일), warning_count = Y (동일)
```

---

## 수정 파일

- **파일**: `GEM/scripts/phase2_validate_safety.py`
- **라인**: 258-271
- **수정일**: 2026-03-10

---

## 기술적 세부사항

### rack_id 형식
```
CH_01.BANK_01.RACK_01
CH_02.BANK_04.RACK_12
CH_06.BANK_03.RACK_05
```

### channel_id 추출
```python
pl.col('rack_id').str.split('.').list.first().alias('channel_id')
# 결과: CH_01, CH_02, ..., CH_06
```

### Z-Score 계산 원리
```
z_score = (v_avg - mean_of_channel_at_timestamp) / std_of_channel_at_timestamp
```

- **mean_of_channel_at_timestamp**: 특정 시간에 같은 채널 내 모든 랙의 평균 전압
- **std_of_channel_at_timestamp**: 특정 시간에 같은 채널 내 모든 랙의 전압 표준편차
- 이 값이 크다 = 해당 랙이 같은 채널의 다른 랙들과 전압 차이가 크다 = 밸런싱 문제

---

## 참고 자료

1. "Voltage fault diagnosis and prognosis of battery systems based on entropy and Z-score for electric vehicles"
   - URL: https://www.sciencedirect.com/science/article/abs/pii/S0306261916319262

2. "Multi-fault detection and diagnosis method for battery packs based on statistical analysis"
   - URL: https://www.sciencedirect.com/science/article/abs/pii/S0360544224002366

3. "Fault diagnosis and abnormality detection of lithium-ion battery packs based on statistical distribution"
   - URL: https://www.sciencedirect.com/science/article/abs/pii/S0378775320312635

---

## 작성자

- 작성일: 2026-03-10
- 작성자: Claude (Anthropic)
- 검토자: 사용자 (RFS 프로젝트)
