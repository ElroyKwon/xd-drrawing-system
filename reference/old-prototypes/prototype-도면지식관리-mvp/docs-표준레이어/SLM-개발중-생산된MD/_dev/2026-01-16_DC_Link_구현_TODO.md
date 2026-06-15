# DC Link 전압 수집 및 System Correlation 구현 TODO

**작업 일시**: 2026-01-16
**우선순위**: Phase 3 완성 후 진행
**목표**: PCS DC Link 전압 데이터를 수집하고 Phase 2에서 System Correlation 검증 구현

---

## 📋 전체 작업 흐름

```
1. Phase 3 (AI 인사이트 생성) 완성 ✅ 우선
2. DC Link 데이터 수집 테스트
3. Parquet 변환 로직 수정 (BSC + PCS 분리)
4. Phase 2에 System Correlation 구현
5. 전체 통합 테스트
```

---

## ✅ 완료된 작업

### 1. PCS 채널 설정 완료
- [x] `api_config_historical.json`에 PCS_CH_01, 02, 03 추가
- [x] `api_config_realtime.json`에 PCS_CH_01, 02, 03 추가
- [x] `pcs_ch_01_tags.txt` 생성 (PCS_01, PCS_02 DC 전압)
- [x] `pcs_ch_02_tags.txt` 생성 (PCS_03, PCS_04 DC 전압)
- [x] `pcs_ch_03_tags.txt` 생성 (PCS_05, PCS_06 DC 전압)

### 2. PCS-BSC 매핑 구조 확인
```
PCS_CH_01 (PCS_01, PCS_02) → BSC_CH_01, BSC_CH_02
PCS_CH_02 (PCS_03, PCS_04) → BSC_CH_03, BSC_CH_04
PCS_CH_03 (PCS_05, PCS_06) → BSC_CH_05, BSC_CH_06
```

### 3. DC Link 태그 목록 (각 PCS당)
```
PCS_CH_0X.PCS_0Y.PCS.DC_L_V        ← 메인 DC Link 전압 (필수)
PCS_CH_0X.PCS_0Y.PCS.DC_INPUT_V    ← DC 입력 전압
PCS_CH_0X.PCS_0Y.PCS.DC_L_LV       ← DC Link Low 전압
PCS_CH_0X.PCS_0Y.PCS.DCLV_H        ← DC Link High 전압
```

---

## 🚧 남은 작업 (Phase 3 완성 후 진행)

### STEP 1: API 데이터 수집 테스트
**목적**: PCS 채널에서 DC Link 전압이 제대로 수집되는지 확인

**작업**:
1. [ ] Historical API로 PCS 채널 수집 테스트
   ```bash
   # GEM 프로그램에서 API 수집 실행
   # 날짜: 2026-01-XX
   # 채널: PCS_CH_01, 02, 03 포함
   ```

2. [ ] 수집된 CSV 파일 확인
   ```
   data/source/api/2026-01-XX/
   ├── bsc_ch_01_*.csv
   ├── bsc_ch_02_*.csv
   ├── ...
   ├── pcs_ch_01_*.csv  ← 새로 생성됨
   ├── pcs_ch_02_*.csv  ← 새로 생성됨
   └── pcs_ch_03_*.csv  ← 새로 생성됨
   ```

3. [ ] PCS CSV 내용 확인
   ```python
   import polars as pl
   df = pl.read_csv('pcs_ch_01_*.csv')
   print(df.columns)  # DC_L_V가 있는지 확인
   print(df.head())   # 실제 전압 값 확인 (900V 수준)
   ```

**예상 결과**:
- PCS_CH_01.PCS_01.PCS.DC_L_V: ~926V
- PCS_CH_01.PCS_02.PCS.DC_L_V: ~927V

---

### STEP 2: Parquet 변환 로직 수정 (옵션 A)
**목적**: BSC 데이터와 PCS 데이터를 별도 Parquet 파일로 저장

**파일**: `scripts/convert_csv_to_parquet.py`

**작업**:
1. [ ] BSC CSV와 PCS CSV 분리 로직 추가
   ```python
   bsc_csv_files = [f for f in csv_files if 'bsc_ch' in f.name.lower()]
   pcs_csv_files = [f for f in csv_files if 'pcs_ch' in f.name.lower()]
   ```

2. [ ] BSC 데이터 → Long Format 변환 (기존 로직 유지)
   ```
   timestamp | rack_id           | t_avg | v_avg | soc | ...
   2026-01-12 00:00:00 | BANK_01.RACK_01 | 24.0 | 3.52 | 17.0
   ```

3. [ ] PCS 데이터 → Wide Format 유지
   ```
   timestamp | pcs_id | dc_link_v | dc_input_v | dc_l_lv | dclv_h
   2026-01-12 00:00:00 | PCS_01 | 926.4 | 929.0 | 470.4 | 466.6
   ```

4. [ ] 두 개의 Parquet 파일 생성
   ```
   all_channels_20260112_20s_batch_v1.parquet           ← BSC (Long Format)
   all_channels_20260112_20s_batch_v1_pcs_dc.parquet   ← PCS (Wide Format)
   ```

**리턴 값 변경**:
```python
# Before
def convert_and_merge_all_channels(...) -> Path:
    return parquet_path

# After
def convert_and_merge_all_channels(...) -> tuple:
    return (bsc_parquet_path, pcs_parquet_path)
```

---

### STEP 3: Phase 2에서 PCS 데이터 로드 및 조인
**목적**: BSC Rack 데이터와 PCS DC Link 전압을 결합

**파일**: `scripts/phase2_validate_safety.py`

**작업**:
1. [ ] PCS Parquet 파일 로드
   ```python
   # Line 80-90 근처에 추가
   pcs_parquet_path = parquet_path.parent / f"{parquet_path.stem}_pcs_dc.parquet"

   if pcs_parquet_path.exists():
       pcs_df = pl.read_parquet(str(pcs_parquet_path))
       console.info(f"PCS DC Link 데이터 로드: {len(pcs_df):,}개 행")
   else:
       pcs_df = None
       console.warning("PCS DC Link 데이터 없음 - System Correlation 스킵")
   ```

2. [ ] BSC-PCS 매핑 테이블 생성
   ```python
   # PCS_CH_01 (PCS_01, PCS_02) → BANK_01, BANK_02
   pcs_bsc_mapping = {
       'PCS_01': ['BANK_01.RACK_01', 'BANK_01.RACK_02', ...],
       'PCS_02': ['BANK_02.RACK_01', 'BANK_02.RACK_02', ...],
       'PCS_03': ['BANK_03.RACK_01', 'BANK_03.RACK_02', ...],
       # ...
   }
   ```

3. [ ] timestamp 기준으로 조인
   ```python
   if pcs_df is not None:
       # 각 Rack에 해당하는 PCS의 DC Link 전압 매핑
       df = df.with_columns([
           pl.when(pl.col('rack_id').str.starts_with('BANK_01'))
             .then(pl.col('timestamp').map(...))  # PCS_01의 DC_L_V
           .when(pl.col('rack_id').str.starts_with('BANK_02'))
             .then(pl.col('timestamp').map(...))  # PCS_02의 DC_L_V
           # ...
           .alias('dc_link_voltage')
       ])
   ```

---

### STEP 4: System Correlation 상관계수 계산
**목적**: Rack 전압과 DC Link 전압의 상관관계 분석

**파일**: `scripts/phase2_validate_safety.py` (Line 273-286)

**작업**:
1. [ ] 기존 하드코딩 제거
   ```python
   # 삭제
   df = df.with_columns([
       pl.lit(1.0).alias('correlation_coefficient')  # ❌ 삭제
   ])
   ```

2. [ ] 실제 상관계수 계산
   ```python
   if pcs_df is not None and 'dc_link_voltage' in df.columns:
       # Rack별 상관계수 계산
       corr_stats = df.group_by('rack_id').agg([
           pl.corr('v_avg', 'dc_link_voltage').alias('correlation')
       ])

       # 임계값 이하인 Rack 찾기
       correlation_min = 0.8  # 임계값
       abnormal_racks = corr_stats.filter(
           pl.col('correlation') < correlation_min
       )['rack_id'].to_list()

       # 상관계수 컬럼 추가
       df = df.join(corr_stats, on='rack_id', how='left')
       df = df.rename({'correlation': 'correlation_coefficient'})
   else:
       # PCS 데이터 없으면 기본값
       df = df.with_columns([
           pl.lit(None).alias('correlation_coefficient')
       ])
   ```

3. [ ] correlation_stats 업데이트
   ```python
   correlation_stats = {
       'total_detections': len(abnormal_racks),
       'normal_tracking': len(corr_stats) - len(abnormal_racks),
       'abnormal_tracking': abnormal_racks,
       'avg_correlation': corr_stats['correlation'].mean()
   }
   ```

---

### STEP 5: main.py 수정
**목적**: Parquet 변환 결과 처리

**파일**: `main.py`

**작업**:
1. [ ] convert_csv_to_parquet 호출 부분 수정 (Line 909 근처)
   ```python
   # Before
   parquet_path = convert_and_merge_all_channels(...)

   # After
   bsc_parquet_path, pcs_parquet_path = convert_and_merge_all_channels(...)

   if pcs_parquet_path:
       log_msg = session.add_log(f"PCS DC Link 데이터 변환 완료: {pcs_parquet_path.name}")
       await websocket.send_json({"type": "log", "content": log_msg})
   ```

---

### STEP 6: 통합 테스트
**목적**: 전체 워크플로우 검증

**테스트 시나리오**:
1. [ ] API Historical 수집 (PCS 포함)
2. [ ] CSV → Parquet 변환 (BSC + PCS 분리)
3. [ ] Phase 2 실행
   - BSC 데이터 로드 ✅
   - PCS 데이터 로드 ✅
   - 조인 성공 ✅
   - Thermal Safety 검증 ✅
   - SPC Balance 검증 ✅
   - Data Integrity 검증 ✅
   - **System Correlation 검증 ✅** (NEW!)
4. [ ] Phase 3 실행 (AI 인사이트)
5. [ ] HTML 리포트 생성

**예상 결과**:
```json
{
  "system_correlation": {
    "total_detections": 2,
    "normal_tracking": 18,
    "abnormal_tracking": ["BANK_02.RACK_05", "BANK_03.RACK_12"],
    "avg_correlation": 0.92
  }
}
```

---

## 📝 주요 고려사항

### 1. 데이터 수집 방식
- ✅ **20초 평균값** (aggTime=20s)
- ✅ **순간값** (적산 아님)
- DC Link 전압도 동일하게 20초 평균으로 수집됨

### 2. 상관계수 계산 방법
```python
# Polars 내장 함수 사용
pl.corr('v_avg', 'dc_link_voltage')

# 피어슨 상관계수 (Pearson Correlation)
# -1 ~ +1 범위
# +1: 완벽한 양의 상관관계
# 0.8 이상: DC 버스를 잘 추종
# 0.8 미만: 추종 실패 (이상)
```

### 3. PCS-BSC 매핑 관리
**옵션 A**: 하드코딩
```python
pcs_bsc_mapping = {
    'PCS_01': ['BANK_01', 'BANK_02'],
    'PCS_02': ['BANK_03', 'BANK_04'],
    ...
}
```

**옵션 B**: 설정 파일 (권장)
```yaml
# config/api/pcs_bsc_mapping.yaml
pcs_bsc_mapping:
  PCS_01:
    - BANK_01
    - BANK_02
  PCS_02:
    - BANK_03
    - BANK_04
  PCS_03:
    - BANK_05
    - BANK_06
```

---

## 🎯 현재 우선순위

```
1. [진행 중] Phase 3 (AI 인사이트 생성) 완성
2. [대기] DC Link 데이터 수집 테스트
3. [대기] Parquet 변환 로직 수정
4. [대기] Phase 2 System Correlation 구현
5. [대기] 전체 통합 테스트
```

---

## 📚 참고 자료

### 관련 파일 위치
```
GEM/
├── config/
│   ├── api_config_historical.json          ← PCS 채널 추가됨
│   ├── api_config_realtime.json            ← PCS 채널 추가됨
│   └── api/column_mapping.yaml             ← 컬럼 매핑
├── data/map/jeju_bess/
│   ├── pcs_ch_01_tags.txt                  ← DC Link 태그
│   ├── pcs_ch_02_tags.txt
│   └── pcs_ch_03_tags.txt
├── scripts/
│   ├── convert_csv_to_parquet.py           ← 수정 필요
│   └── phase2_validate_safety.py           ← 수정 필요
└── main.py                                  ← 수정 필요
```

### 데이터 예시
**BSC Parquet (Long Format)**:
```
timestamp            | rack_id           | t_avg | v_avg | soc
2026-01-12 00:00:00 | BANK_01.RACK_01  | 24.0  | 3.52  | 17.0
2026-01-12 00:00:00 | BANK_01.RACK_02  | 24.5  | 3.53  | 17.5
```

**PCS Parquet (Wide Format)**:
```
timestamp            | pcs_id | dc_link_v | dc_input_v
2026-01-12 00:00:00 | PCS_01 | 926.4     | 929.0
2026-01-12 00:00:00 | PCS_02 | 927.0     | 930.5
```

---

## ✅ 완료 체크리스트

Phase 3 완성 후 아래 순서대로 진행:

- [ ] STEP 1: API 데이터 수집 테스트 (30분)
- [ ] STEP 2: Parquet 변환 로직 수정 (1시간)
- [ ] STEP 3: Phase 2 PCS 데이터 로드 (1시간)
- [ ] STEP 4: System Correlation 계산 (1시간)
- [ ] STEP 5: main.py 수정 (30분)
- [ ] STEP 6: 통합 테스트 (1시간)

**예상 총 소요 시간**: 5시간

---

**작성일**: 2026-01-16
**작성자**: Claude Code
**다음 작업**: Phase 3 (AI 인사이트 생성) 완성
