# REG 학습 데이터 생성 가이드

## 📌 개요

GEM 시스템의 분석 결과를 활용하여 **REG (Regression) 모델 학습용 데이터셋**을 자동으로 생성합니다.

---

## 🎯 REG 학습 목표

### 입력 (Features)
- 배터리 시계열 데이터 (전압, 전류, 온도, SOC)
- 배터리 프로파일 정보 (타입, 제조사, 정격 용량)
- 시스템 메타데이터 (채널, Rack, Module)

### 출력 (Labels)
- 열적 안전성 위험도 (0~1)
- 셀 밸런싱 이상 여부 (0/1)
- 내부 단락 가능성 (0~1)
- 데이터 무결성 점수 (0~1)

---

## 📊 학습 데이터 생성 로직

### 1. 데이터 소스
```
results/YYYYMMDD_HHMMSS_배터리타입/
├── metadata.json                 # 입력 특성
│   ├── data_source              # API / Upload
│   ├── battery_profile          # NMC_LG, LFP_CATL, ...
│   ├── channels                 # [BSC_CH_01, BSC_CH_02]
│   ├── date_range               # 2025-12-23 ~ 2025-12-24
│   └── config_params            # batch_size, agg_time, ...
│
├── phase1_convert/
│   └── standard_data.parquet    # 원본 시계열 데이터
│
├── phase2_validate/
│   ├── thermal_safety.json      # 열적 안전성 검증 결과
│   ├── spc_balance.json         # 셀 밸런싱 검증 결과
│   ├── system_correlation.json  # 내부 단락 검증 결과
│   └── data_integrity.json      # 데이터 무결성 검증 결과
│
└── phase4_report/
    └── summary.json             # 핵심 지표 요약 (레이블)
```

### 2. 학습 데이터 변환 프로세스

```
[Phase 1] Parquet → 시계열 특성 추출
  ↓
  - 전압 통계: mean, std, min, max, range
  - 온도 통계: mean, std, gradient(dT/dt)
  - 전류 패턴: peak, valley, cycle_count
  - SOC 변화율: charge_speed, discharge_speed

[Phase 2] JSON → 레이블 생성
  ↓
  - thermal_safety.json → thermal_risk_score (0~1)
  - spc_balance.json → balance_anomaly (0/1)
  - system_correlation.json → short_circuit_risk (0~1)
  - data_integrity.json → integrity_score (0~1)

[Phase 3] 메타데이터 → 추가 특성
  ↓
  - battery_type_encoded (LFP=0, NMC=1, NCA=2)
  - channel_id (CH_01=1, CH_02=2, ...)
  - rack_id, module_id

[Phase 4] 학습 데이터셋 생성
  ↓
  data/training/processed/YYYYMMDD_HHMMSS.parquet
  ├── Features (30+ columns)
  └── Labels (4 columns)
```

---

## 🗂️ 학습 데이터 폴더 구조

```
data/training/
├── raw/                              # 원본 학습 자료
│   └── YYYYMMDD_HHMMSS_배터리타입/
│       ├── standard_data.parquet     # Phase1 결과 복사
│       ├── thermal_safety.json       # Phase2 결과 복사
│       ├── spc_balance.json
│       ├── system_correlation.json
│       ├── data_integrity.json
│       └── metadata.json             # 실행 메타데이터
│
├── processed/                        # 전처리된 학습 데이터
│   └── YYYYMMDD_HHMMSS.parquet
│       ├── [Features]
│       │   ├── voltage_mean, voltage_std, voltage_range
│       │   ├── temp_mean, temp_std, temp_gradient
│       │   ├── current_peak, current_valley
│       │   ├── soc_change_rate
│       │   ├── battery_type_encoded
│       │   └── channel_id, rack_id, module_id
│       │
│       └── [Labels]
│           ├── thermal_risk_score      # 0~1
│           ├── balance_anomaly         # 0/1
│           ├── short_circuit_risk      # 0~1
│           └── integrity_score         # 0~1
│
└── labels/                           # 레이블만 별도 저장 (검증용)
    └── YYYYMMDD_HHMMSS_labels.json
        ├── thermal: {...}
        ├── balance: {...}
        ├── correlation: {...}
        └── integrity: {...}
```

---

## 🔧 자동화 스크립트

### `scripts/generate_training_data.py`

```python
"""
분석 결과 → REG 학습 데이터 변환
"""

def extract_features_from_parquet(parquet_path):
    """Parquet에서 시계열 특성 추출"""
    df = pl.read_parquet(parquet_path)

    features = {
        'voltage_mean': df['voltage_avg'].mean(),
        'voltage_std': df['voltage_avg'].std(),
        'voltage_range': df['voltage_max'].max() - df['voltage_min'].min(),

        'temp_mean': df['temp_avg'].mean(),
        'temp_std': df['temp_avg'].std(),
        'temp_gradient': calculate_max_gradient(df['temp_avg']),

        'current_peak': df['current'].max(),
        'current_valley': df['current'].min(),

        'soc_change_rate': calculate_soc_rate(df['soc']),
    }
    return features

def extract_labels_from_phase2(phase2_dir):
    """Phase2 JSON에서 레이블 생성"""

    # Thermal Safety
    thermal = json.load(open(phase2_dir / 'thermal_safety.json'))
    thermal_risk = len(thermal.get('critical_events', [])) / 100  # 정규화

    # SPC Balance
    spc = json.load(open(phase2_dir / 'spc_balance.json'))
    balance_anomaly = 1 if spc.get('outlier_count', 0) > 0 else 0

    # Internal Short
    correlation = json.load(open(phase2_dir / 'system_correlation.json'))
    short_risk = correlation.get('short_circuit_probability', 0.0)

    # Data Integrity
    integrity = json.load(open(phase2_dir / 'data_integrity.json'))
    integrity_score = integrity.get('overall_score', 1.0)

    labels = {
        'thermal_risk_score': min(thermal_risk, 1.0),
        'balance_anomaly': balance_anomaly,
        'short_circuit_risk': short_risk,
        'integrity_score': integrity_score,
    }
    return labels

def convert_result_to_training_data(result_dir):
    """
    results/YYYYMMDD_HHMMSS_배터리타입/
    → data/training/processed/YYYYMMDD_HHMMSS.parquet
    """

    # 1. 메타데이터 로드
    metadata = json.load(open(result_dir / 'metadata.json'))

    # 2. 특성 추출
    features = extract_features_from_parquet(
        result_dir / 'phase1_convert' / 'standard_data.parquet'
    )

    # 3. 레이블 추출
    labels = extract_labels_from_phase2(
        result_dir / 'phase2_validate'
    )

    # 4. 메타특성 추가
    battery_type_map = {'LFP': 0, 'NMC': 1, 'NCA': 2}
    features['battery_type_encoded'] = battery_type_map.get(
        metadata['battery_profile'].split('_')[0], -1
    )
    features['channel_count'] = len(metadata['channels'])

    # 5. DataFrame 생성
    training_data = pl.DataFrame({
        **features,
        **labels,
        'run_id': metadata['run_id'],
        'timestamp': metadata['timestamp'],
    })

    # 6. 저장
    output_path = Path('data/training/processed') / f"{metadata['run_id']}.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    training_data.write_parquet(output_path)

    return output_path
```

---

## 📝 실행 예시

### 1. 단일 결과 → 학습 데이터 변환
```bash
python scripts/generate_training_data.py --result_id 20251224_120000_NMC_LG
```

### 2. 전체 results/ → 학습 데이터셋 생성
```bash
python scripts/generate_training_data.py --all
```

### 3. 학습 데이터 통합 (여러 실행 결과 병합)
```bash
python scripts/merge_training_datasets.py \
  --input data/training/processed/*.parquet \
  --output data/training/final_dataset.parquet
```

---

## 🧪 학습 데이터 검증

### `scripts/validate_training_data.py`

```python
"""학습 데이터 품질 검증"""

def validate_training_dataset(parquet_path):
    df = pl.read_parquet(parquet_path)

    checks = {
        'row_count': len(df),
        'feature_columns': len([c for c in df.columns if c not in LABEL_COLUMNS]),
        'label_columns': len([c for c in df.columns if c in LABEL_COLUMNS]),
        'null_ratio': df.null_count().sum() / (len(df) * len(df.columns)),
        'label_distribution': {
            'thermal_risk': df['thermal_risk_score'].describe(),
            'balance_anomaly_ratio': df['balance_anomaly'].sum() / len(df),
        }
    }

    return checks
```

---

## 🎓 REG 모델 학습 워크플로

```
1. 데이터 수집
   ├── API 수집 (실제 운영 데이터)
   └── CSV 업로드 (실험실 데이터)

2. GEM 분석 (Phase 1~3)
   → results/YYYYMMDD_HHMMSS_배터리타입/

3. 학습 데이터 생성
   → scripts/generate_training_data.py
   → data/training/processed/

4. 데이터셋 병합 (N개 실행 결과)
   → data/training/final_dataset.parquet

5. REG 모델 학습 (별도 모듈)
   ├── Input: final_dataset.parquet
   ├── Algorithm: XGBoost, LightGBM, Neural Network
   └── Output: trained_model.pkl

6. 모델 평가
   ├── Test Set 분리 (20%)
   ├── Metrics: MAE, RMSE, F1-Score
   └── Cross-Validation

7. 배포
   └── GEM에 통합 (Phase 2 대체 가능)
```

---

## 🔍 주요 특성 (Features) 목록

### 시계열 통계 (Parquet 추출)
- `voltage_mean`, `voltage_std`, `voltage_range`
- `temp_mean`, `temp_std`, `temp_gradient`, `temp_max_change`
- `current_peak`, `current_valley`, `current_std`
- `soc_mean`, `soc_change_rate`

### 배터리 프로파일
- `battery_type_encoded` (LFP=0, NMC=1, NCA=2)
- `manufacturer_encoded` (CATL=0, LG=1, Samsung=2)
- `rated_capacity_kwh`

### 시스템 메타데이터
- `channel_id`, `rack_count`, `module_count`
- `data_duration_hours`
- `sampling_interval_sec`

### 시간 특성
- `hour_of_day`, `day_of_week`, `season`

---

## 📌 참고 사항

1. **레이블 정규화**: 모든 레이블은 0~1 범위로 정규화
2. **이상치 처리**: Phase2 결과가 비정상적으로 높으면 상한선 적용
3. **결측치 처리**: Phase1 Parquet에 NULL이 있으면 보간 또는 제외
4. **클래스 불균형**: balance_anomaly는 0/1 이진 분류 → SMOTE 적용 고려

---

## 🚀 다음 단계

1. `scripts/generate_training_data.py` 구현
2. 10개 이상의 results/ 데이터로 학습 데이터셋 생성
3. REG 모델 학습 (XGBoost 추천)
4. 모델 성능 평가 (테스트 데이터)
5. GEM Phase 2에 통합 (실시간 예측)

---

**작성일**: 2025-12-26
**버전**: 1.0.0
