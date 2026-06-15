# GEM 배터리 안전성 분석 - 기술 명세서

**작성일**: 2026-01-27
**버전**: 3.2
**목적**: Phase2 안전성 검증의 실제 구현 내용 문서화
**최종 수정**: 2026-01-27 - 센서무결성 차트 개선, Chart.js 툴팁 활성화

---
## 1. 데이터 구조

### 1.1 Phase1: 데이터 수집 및 변환

**입력**: XD-HUB CSV 또는 API Parquet
**출력**: 표준 Parquet (`data/results/{RUN_ID}/phase1/battery_data.parquet`)

**컬럼 매핑** (`phase1_convert_data.py:358-370`):

| 원본 CSV 컬럼 | 표준 Parquet 컬럼 | 타입 | 설명 | 원본 태그 (XD-HUB) |
|-------------|-----------------|------|------|------------------|
| `time` | `timestamp` | DateTime | UTC 시간 | `TIMESTAMP` |
| `rack_name` | `rack_id` | String | Rack 식별자 | `RACK_ID` |
| `module_name` | `module_id` | String | Module 식별자 | `MODULE_ID` |
| `voltage_avg` | `v_avg` | Float32 | 평균 전압 (V) | `CELL_AVG_V` |
| `voltage_min` | `v_min` | Float32 | 최소 전압 (V) | `CELL_MIN_V` |
| `voltage_max` | `v_max` | Float32 | 최대 전압 (V) | `CELL_MAX_V` |
| `voltage_std` | `v_std` | Float32 | 전압 표준편차 (V) | `CELL_STD_V` |
| `temp_avg` | `t_avg` | Float32 | 평균 온도 (°C) | `MOD_AVG_TEMP` |
| `temp_min` | `t_min` | Float32 | 최소 온도 (°C) | `MOD_MIN_TEMP` |
| `temp_max` | `t_max` | Float32 | 최대 온도 (°C) | `MOD_MAX_TEMP` |
| `current` | `current` | Float32 | 전류 (A, 방전 음수) | `RACK_CURRENT` |
| `soc` | `soc` | Float32 | 충전율 (%) | `RACK_SOC` |
| - | `quality_flag` | Int8 | 품질 플래그 (0~3) | - |

**원본 백업**:
- Upload 모드: `data/results/{RUN_ID}/raw/original.csv`
- API 모드: `data/results/{RUN_ID}/raw/original.parquet`

---

## 2. Phase2: 안전성 검증

### 2.1 Thermal Safety (열적 안전성)

**분석 대상**: 온도 변화율 (dT/dt)

**계산 공식** (`phase2_validate_safety.py:160-162`):
```python
# Rack별 그룹화하여 온도 변화율 계산
dtdt = (t_avg.diff().over('rack_id') / interval_sec) * 60

# 단위: °C/min
# interval_sec: 자동 감지 (첫 2개 레코드 시간 차이)
# t_avg.diff(): 현재 온도 - 이전 온도
# over('rack_id'): Rack별로 독립 계산
```

**사용 컬럼**:
- `t_avg` (평균 온도)
- `timestamp` (시간 간격 계산)
- `rack_id` (Rack별 그룹화)

**출력 컬럼**:
- `dtdt`: 온도 변화율 (Float, °C/min)
- `thermal_level`: 레벨 (String: 'normal', 'warning', 'critical', 'sensor_error')
- `is_thermal_risk`: Critical 플래그 (Boolean, 하위 호환용)

**판정 로직** (`phase2_validate_safety.py:193-202`):
```python
# 절댓값 기준
if abs(dtdt) > physics_max:           # 100.0°C/min
    thermal_level = 'sensor_error'
elif abs(dtdt) >= critical:           # 2.0°C/min (겨울, NMC)
    thermal_level = 'critical'
elif abs(dtdt) >= warning:            # 1.2°C/min (겨울, NMC)
    thermal_level = 'warning'
else:
    thermal_level = 'normal'
```

**임계값 (프로파일: `config/battery/profiles/NMC_LG.yaml`)**:
```yaml
thresholds:
  thermal_safety:
    critical: 1.5    # 기본값
    warning: 0.8
    physics_max: 100.0

seasonal_adjustment:
  winter:
    thermal_critical_offset: 0.5  # 1.5 + 0.5 = 2.0
    thermal_warning_offset: 0.4   # 0.8 + 0.4 = 1.2
```

---

### 2.2 SPC Balance (Z-Score, 셀 밸런싱)

**분석 대상**: 전압 통계적 편차

**계산 공식** (`phase2_validate_safety.py:269-272`):
```python
# 시간축별 Z-Score 계산
z_score = (v_avg - mean(v_avg).over('timestamp')) / std(v_avg).over('timestamp')

# mean(...).over('timestamp'): 동일 시간의 전체 Rack 평균
# std(...).over('timestamp'): 동일 시간의 전체 Rack 표준편차
```

**사용 컬럼**:
- `v_avg` (평균 전압)
- `timestamp` (시간축별 통계)

**출력 컬럼**:
- `z_score`: Z-Score 값 (Float, σ 단위)
- `spc_level`: 레벨 (String: 'normal', 'warning', 'critical', 'sensor_error')
- `is_outlier`: Critical 플래그 (Boolean, 하위 호환용)

**판정 로직** (`phase2_validate_safety.py:285-294`):
```python
if abs(z_score) > physics_max:        # 10.0σ
    spc_level = 'sensor_error'
elif abs(z_score) >= critical:        # 3.0σ (겨울, NMC)
    spc_level = 'critical'
elif abs(z_score) >= warning:         # 2.0σ (겨울, NMC)
    spc_level = 'warning'
else:
    spc_level = 'normal'
```

**임계값 (프로파일: `config/battery/profiles/NMC_LG.yaml`)**:
```yaml
thresholds:
  spc_balance:
    critical: 2.5    # 기본값
    warning: 1.5
    physics_max: 10.0

seasonal_adjustment:
  winter:
    voltage_tolerance: 0.08  # Z-Score 허용 범위 확대
    # Critical: 2.5 + 0.5 = 3.0
    # Warning: 1.5 + 0.5 = 2.0
```

**통계 이론**:
- 1σ 이내: 68.3% (정상)
- 2σ 이내: 95.5% (정상 편차)
- 3σ 초과: 0.3% (이상치)

---

### 2.3 Data Integrity (데이터 무결성)

**검증 항목**:

1. **센서 고착 (Sensor Frozen)** (`phase2_validate_safety.py:357-365`)
   - Rack별 표준편차 < 0.001
   - 전체 분석 기간 동안 v_avg 또는 t_avg의 표준편차가 0.001 미만
   - 컬럼: `v_avg`, `t_avg`

2. **범위 이탈 (Out of Range)**
   - 물리적 한계 초과
   - 전압: 2.8~4.2V (NMC)
   - 온도: -10~55°C (NMC)

3. **Spike 검출**
   - **계산 공식** (`phase2_validate_safety.py:403-420`):
   ```python
   # 변화율 절대값 계산 (주의: v_spike, t_spike는 V/s, °C/s 단위)
   v_spike = |ΔV / interval_sec|  # V/s (절대값)
   t_spike = |ΔT / interval_sec|  # °C/s (절대값)

   # Spike 판정
   has_spike = (v_spike > voltage_spike_threshold) | (t_spike > temp_spike_threshold)
   ```
   - **v_spike vs v_drop 차이**:
     - v_spike: 절대값, V/s 단위 (Spike 검출용)
     - v_drop: 하락만, V/min 단위 (ISC 검출용)
   - **임계값** (`config/battery/profiles/NMC_LG.yaml:68-71`):
   ```yaml
   integrity_check:
     voltage_spike_threshold: 0.005  # V/s (5 mV/s) - 2026-01-27 최적화
     temp_spike_threshold: 0.25      # °C/s (15 °C/min) - 열폭주 전조 감지 가능
   ```
   - **설정 근거** (2026-01-27 실측 데이터 분석):
     - 실제 최대값: V=0.0009 V/s, T=0.05 °C/s
     - 임계값: 실제 최대값의 **5배** (정상 운영 여유 확보)
     - False Positive 최소화 (센서 노이즈 ±2mV 고려)
   - **이전 설정**: V=0.3 V/s, T=3.0 °C/s (실제값의 300~60배, Spike 감지 불가능)
   - **샘플링 간격 동적 처리**: interval_sec 자동 감지하여 모든 간격에서 동일 기준 적용

4. **Data Quality % (데이터 품질 점수)**
   - **목적**: 센서 무결성 종합 점수
   - **계산 공식** (`phase2_validate_safety.py:428-439`):
   ```python
   # 품질 점수: 정상=100%, 이상=0%
   data_quality_pct = when(sensor_frozen | out_of_range | has_spike)
                      .then(0.0)
                      .otherwise(100.0)
   ```
   - **의미**:
     - 100%: 정상 센서 데이터
     - 0%: 이상 감지 (고착/범위이탈/스파이크 중 하나 이상 발생)

**차트 구성** (2026-01-27 최종 개선):
- **메인 차트**: 센서 이상 발생 추이 (Frozen + Out of Range + Spike)
  - 꺾은선 차트 (Line), 3개 독립 선 (`battery_report_v2.html:1098-1180`)
  - Boolean → 숫자 변환 (True=1, False=0) (1093-1095줄)
  - Y축: 0 (정상) ~ 1.5, 0일 때도 3개 선이 X축에 표시됨
  - 이전: 막대 차트 (stacked) → 문제: 3개 값이 더해져서 의미 불명확
- **서브 차트 1**: 급격한 변화율 (V_spike, T_spike) (`battery_report_v2.html:1182-1202`)
  - Spike 검출의 원인 데이터 표시
  - 이전: V_max, V_min (원시 전압) → 변경: Spike 검출값 직접 표시
- **서브 차트 2**: Data Quality % (0~100%) (`battery_report_v2.html:1204-1244`)
  - 센서 무결성 종합 점수

**출력**:
- JSON 파일: `data/results/{RUN_ID}/phase2/data_integrity.json`
- Rack Detail JSON: `sensor_frozen`, `out_of_range`, `has_spike`, `data_quality_pct` 컬럼 포함

---

### 2.4 ISC Detection (내부단락 감지)

**분석 대상**: 전압 하락 + 온도 상승 동시 발생

**물리적 근거**:
- 배터리 내부단락 시 특징적인 현상:
  - **전압 하락**: 내부 저항 증가로 인한 전압 강하
  - **온도 상승**: 단락 전류로 인한 줄열(Joule heating)

**계산 공식** (`phase2_validate_safety.py:394-407, 525-549`):
```python
# 1. 방향성 변화율 계산 (ISC 특성에 맞게)
# 주의: v_drop, t_rise는 V/min, °C/min (ISC 검출용)
v_drop = when(ΔV < 0).then(-ΔV / interval_sec * 60).otherwise(0)  # V/min
t_rise = when(ΔT > 0).then(ΔT / interval_sec * 60).otherwise(0)   # °C/min

# 2. ISC Score 계산 (0~1 범위)
isc_score = 0.5 × v_drop_norm + 0.3 × t_rise_norm + 0.2 × current_norm

# 3. 정규화 (0~1 범위)
v_drop_norm = (v_drop / voltage_rate_max).clip(0, 1)      # 하락률 정규화
t_rise_norm = (t_rise / temperature_rate_max).clip(0, 1)  # 상승률 정규화
current_norm = current_anomaly.clip(0, 1)                  # Z-Score 기반
```

**ISC vs Spike 변화율 차이**:
- **v_drop (ISC용)**: 하락만, V/min 단위 (느린 단락 감지)
- **v_spike (Spike용)**: 절대값, V/s 단위 (급격한 센서 오류 감지)
- **t_rise (ISC용)**: 상승만, °C/min 단위
- **t_spike (Spike용)**: 절대값, °C/s 단위

**current_anomaly 계산** (`phase2_validate_safety.py:466-467`):
```python
# Rack별 전류의 Z-Score (표준편차 기반 이상치 점수)
current_anomaly = |current - mean(current_per_rack)| / std(current_per_rack)

# 예시:
# current = 50A, mean = 48A, std = 1.0A
# → current_anomaly = |50 - 48| / 1.0 = 2.0σ
# → clip(2.0, 0, 1) = 1.0 (최대값 제한)
```

**클리핑(Clipping) 처리**:
- **목적**: ISC Score를 0~1 범위로 제한하여 임계값(0.5, 0.25)과 비교 가능하게 함
- **효과**:
  - `v_drop = 0.5 V/min` → `0.5/0.2 = 2.5` → **clip → 1.0**
  - `t_rise = 15 °C/min` → `15/10 = 1.5` → **clip → 1.0**
  - `current_anomaly = 1.868σ` → **clip → 1.0**
- **의미**: 정상 범위를 크게 벗어난 경우 최대 기여도(1.0)로 제한

**2차 판단 기준 (Rack별 종합 평가)** - 2026-01-27 개선:
1. **Rankings 포함 여부 확인**:
   - ISC Warning < 44회이고 다른 이슈도 없으면 → Rankings에 미포함 (정상)
   - 다른 이슈(Spike, Frozen 등)로 Rankings에 포함되었더라도 ISC는 별도 판단

2. **ISC Warning 카운트** (`phase2_validate_safety.py:947-997`):
   - Rankings에 포함된 Rack 중 ISC Warning ≥ 44회만 최종 ISC Warning으로 판정
   - ISC Warning < 44회: 1차 경고는 있었지만 기준 미달로 제외
   - 제외된 건수는 `primary_warning_excluded`에 누적하여 투명성 확보

3. **Primary Issue 표시** (`phase2_validate_safety.py:811-813`):
   - ISC Warning < 44회: Primary Issue에 표시 안함 (최종 판단 정상)
   - ISC Warning ≥ 44회: Primary Issue에 표시 (최종 판단 Warning)
   - 상세 화면: "ISC Warning N회 발생 (최종 판단: 정상 - 기준 44회 미만)" 메시지

4. **isc_detection.json 저장 시점** (`phase2_validate_safety.py:998-1012`):
   - 이전: Rankings 계산 **전** 저장 (1차 판단 값)
   - 개선: Rankings 계산 **후** 저장 (2차 판단 값)
   - 결과: Phase3 리포트에 올바른 카운트 표시

5. **근거**:
   - 전체 4320개 타임스탬프(24시간) 대비 1% 기준
   - Rack 점수 계산: `score += min(int(warning_ratio * 100), 44)`
   - 예: 7회/4320 = 0.16% → int(0.16) = 0점 (Rankings 미포함, Primary Issue 미표시)
   - 예: 44회/4320 = 1.02% → int(1.02) = 1점 (Rankings 포함, Primary Issue 표시)

**정규화 기준값** (`config/battery/profiles/NMC_LG.yaml:64-65`):
```yaml
normalization:
  voltage_rate_max: 0.2      # V/min - 실제 ESS 운영 데이터 기반 (수정됨: 30 → 0.2)
  temperature_rate_max: 10.0  # °C/min
```

**가중치** (`config/battery/profiles/NMC_LG.yaml:60-62`):
```yaml
weights:
  voltage: 0.5        # 전압 강하 (NMC는 전압 변화에 민감)
  temperature: 0.3    # 온도 상승
  current: 0.2        # 전류 이상
```

**임계값** (`config/battery/profiles/NMC_LG.yaml:57-58`):
```yaml
critical: 0.5   # ISC Score ≥ 0.5 → Critical
warning: 0.25   # ISC Score ≥ 0.25 → Warning
```

**차트 표시** (`battery_report_v2.html:900-983`):
- 메인 차트: ISC Score (0~1) 선 그래프
- Critical 임계선 (0.5) 표시
- 서브 차트: V_spike, dT/dt (원인 분석용)

---

### 2.5 System Correlation (시스템 상관성)

**분석 대상**: 전압 추종 분석

**출력**:
- JSON 파일: `data/results/{RUN_ID}/phase2/system_correlation.json`

---

## 3. Rack Scoring 시스템

**점수 계산** (프로파일 기반):

```python
# Critical 이벤트 (고정 점수)
if thermal_critical > 0:
    score += 100
if zscore_critical > 0:
    score += 80
if isc_critical > 0:
    score += 120

# Warning 이벤트 (비율 기반, 상한 있음)
if thermal_warning > 0:
    ratio = thermal_warning / total_records
    score += min(int(ratio * 100), 30)

if zscore_warning > 0:
    ratio = zscore_warning / total_records
    score += min(int(ratio * 100), 25)

# Integrity 이벤트 (건수 기반)
score += frozen_count * 3
score += out_of_range_count * 2
score += spike_count * 4
```

**Status 판정**:
```python
if score >= 100:
    status = "Critical"  # 즉시 조치
elif score >= 10:
    status = "Warning"   # 주의 관찰
else:
    status = "Normal"
```

**점수 설정 (프로파일: `config/battery/profiles/NMC_LG.yaml`)**:
```yaml
rack_scoring:
  critical_scores:
    thermal: 100
    spc: 80
    isc: 120
    sensor_error: 100

  warning_max_scores:
    thermal: 30
    spc: 25
    isc: 35

  integrity_scores:
    sensor_frozen: 3
    out_of_range: 2
    spike: 4

  status_thresholds:
    critical: 100
    warning: 10      # v2.0: 40 → 10 변경
```

---

## 4. Phase4: HTML 리포트

### 4.1 차트 공통 설정

**Chart.js 툴팁 활성화** (`battery_report_v2.html:395-427`):
```javascript
const commonOptions = {
    interaction: {
        mode: 'index',
        intersect: false
    },
    plugins: {
        tooltip: {
            enabled: true,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            // ... 스타일 설정
        }
    },
    events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove']
}
```
- **이전**: `interaction: { mode: null }` → 모든 interaction 비활성화
- **현재**: 마우스 오버 시 데이터 값 표시

### 4.2 차트 데이터 매핑

**온도 변화율 (dT/dt) 차트** (`battery_report_v2.html:432-471`):

```javascript
// 모든 데이터에 막대 표시 (배경)
if (dtdt >= 0) {
    normalPositiveData.push(dtdt);  // 양수 막대
    normalNegativeData.push(null);
} else {
    normalPositiveData.push(null);
    normalNegativeData.push(dtdt);  // 음수 막대
}

// 레벨별 점 오버레이 (전경)
if (thermal_level === 'critical') {
    criticalData.push(dtdt);  // 빨간 점
} else if (thermal_level === 'warning') {
    warningData.push(dtdt);   // 파란 점
}
```

**Z-Score 차트** (`battery_report_v2.html:803`):
```javascript
// Critical 라벨 비활성화
upper_critical: {
    type: 'line',
    yMin: 3.0,
    yMax: 3.0,
    borderColor: '#ef4444',
    label: { display: false }  // 라벨 숨김
}
```

---

## 5. UI 구현

### 5.1 Phase3 완료 후 버튼

**위치**: `static/app.js:1434-1498`

**박스 크기**:
- `max-width: 400px` (컴팩트한 박스)
- `padding: 20px` (내부 여백)

**버튼 크기**:
- `flex: 1` (균등 분할)
- `padding: 16px 24px` (큰 클릭 영역)
- `font-size: 16px` (명확한 가독성)

---

## 6. 업데이트 이력

**v3.2 (2026-01-27)**:
1. 센서무결성 차트 개선:
   - 메인 차트: Bar (stacked) → Line (3개 독립 선)
   - 서브 차트 1: V_max, V_min → V_spike, T_spike
   - 논리적 구조 개선: Spike 검출값을 직접 표시
2. Chart.js 툴팁 활성화 (`interaction: mode='index'`)
3. 센서무결성 탭 구조 명확화 (ISC 탭과 독립성)

**v3.1 (2026-01-27)**:
1. Spike 임계값 최적화 (0.005 V/s, 0.25 °C/s)
2. ISC 2차 판단 개선 및 isc_detection.json 저장 시점 수정
3. ISC Warning Primary Issue 표시 로직 개선 (44회 기준)

**v3.0 (2026-01-26)**:
1. 실제 코드 구현 기반으로 전체 재작성
2. 원본 CSV 태그 → Parquet 컬럼 매핑 추가
3. 계산 공식 코드 참조 명시
4. API 모드 원본 백업 추가
5. dT/dt 차트 데이터 매핑 수정 (모든 값에 막대 표시)
6. Z-Score 차트 Critical 라벨 제거
7. Phase3 버튼 UI 개선

**v2.0 (2026-01-26)**:
- 프로파일 기반 설계 추가

**v1.0 (2026-01-26)**:
- 초기 작성
