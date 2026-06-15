# TODO: 데이터 수집, 저장 및 변환 시스템 구현

**작성일:** 2025-12-26
**관련 문서:** [20_데이터-수집-저장-변환-전략.md](_dev/20_데이터-수집-저장-변환-전략.md)
**상태:** 진행중

---

## 📋 Phase 1: 파일 저장 및 명명 규칙

### 1.1 파일명 기반 모드 구분 구현
- [ ] `storage.py`: 파일명 생성 로직 수정
  ```python
  def get_csv_path(self, channel: str, date: str, mode: str = 'realtime') -> Path:
      """
      Args:
          mode: 'realtime' | 'batch'
      Returns:
          data/source/api/{date}/{channel}_{mode}.csv
      """
  ```
  - 파일: `GEM/api_collector/storage.py`
  - 함수: `get_csv_path()`, `get_parquet_path()`

- [ ] 모드 자동 감지 함수
  ```python
  def detect_mode_from_filename(csv_path: Path) -> str:
      """
      파일명에서 모드 추출
      Returns: 'realtime' | 'batch' | 'upload' | 'unknown'
      """
      if '_realtime.csv' in str(csv_path):
          return 'realtime'
      elif '_batch.csv' in str(csv_path):
          return 'batch'
      elif 'original.csv' in str(csv_path):
          return 'upload'
      else:
          return 'unknown'
  ```
  - 파일: `GEM/api_collector/utils.py` (신규)

### 1.2 용량 모니터링
- [ ] CSV 파일 크기 체크
  ```python
  def check_file_size(csv_path: Path, threshold_mb: int = 10):
      """하루 파일이 threshold_mb 초과 시 경고"""
  ```
  - 파일: `GEM/api_collector/monitor.py`
  - 10MB 초과 시 로그 경고

---

## 📋 Phase 2: Parquet 변환 로직

### 2.1 실시간 모드 - 하루 종료 후 자동 변환
- [ ] 하루 종료 감지 함수
  ```python
  def is_end_of_day(current_time: datetime, trigger_hour: int = 23, trigger_minute: int = 55) -> bool:
      """23:55 도달 확인"""
  ```
  - 파일: `GEM/api_collector/realtime.py`

- [ ] 자동 Parquet 변환
  ```python
  def end_of_day_process(self):
      """
      1. 마지막 재시도
      2. 무결성 검증
      3. PASS → Parquet 변환
      4. FAIL → 알림
      """
      self.retry_failed_requests()
      integrity = validate_integrity(...)

      if integrity['status'] == 'PASS':
          self.convert_to_parquet()
      else:
          self.send_alert(integrity)
  ```
  - 파일: `GEM/api_collector/realtime.py`
  - 클래스: `RealtimeCollector`

- [ ] CSV → Parquet 변환 함수
  ```python
  def convert_to_parquet(csv_path: Path, parquet_path: Path):
      """CSV를 Parquet으로 변환 (압축)"""
      df = pl.read_csv(csv_path)
      df.write_parquet(
          parquet_path,
          compression='zstd',
          compression_level=3,
          row_group_size=50_000
      )
  ```
  - 파일: `GEM/api_collector/converter.py` (신규)

### 2.2 일괄 모드 - 즉시 변환
- [ ] 일괄 수집 완료 후 즉시 변환
  ```python
  def collect_date(self, date: str, channel: str):
      # CSV 저장
      self.save_to_csv(...)

      # 무결성 검증
      integrity = validate_integrity(...)

      if integrity['status'] == 'PASS':
          # 즉시 변환
          self.convert_to_parquet()
      else:
          # 재수집 제안
          prompt_user("검증 실패. 재수집하시겠습니까?")
  ```
  - 파일: `GEM/api_collector/historical.py`
  - 클래스: `HistoricalCollector` (일괄 수집)

### 2.3 변환 완료 플래그
- [ ] `.converted` 플래그 파일 생성
  ```python
  def mark_as_converted(date: str, channel: str, mode: str):
      """
      변환 완료 플래그 생성
      data/source/api/{date}/.{channel}_{mode}.converted
      """
      flag_file = f".{channel}_{mode}.converted"
      # 타임스탬프 기록
  ```
  - 파일: `GEM/api_collector/converter.py`

---

## 📋 Phase 3: 무결성 검증

### 3.1 검증 함수 구현
- [ ] `validate_integrity()` 구현
  ```python
  def validate_integrity(
      csv_path: Path,
      date: str,
      interval_minutes: int = 5
  ) -> dict:
      """
      누락/중복/시간갭 체크

      Returns:
          {
              'status': 'PASS' | 'FAIL',
              'expected_records': 288,
              'actual_records': 287,
              'missing_timestamps': [...],
              'duplicate_timestamps': [...],
              'time_gaps': [...]
          }
      """
  ```
  - 파일: `GEM/api_collector/validator.py` (신규)
  - 함수:
    - `generate_expected_timestamps()`
    - `check_missing()`
    - `check_duplicates()`
    - `check_time_gaps()`

### 3.2 검증 결과 저장
- [ ] `.integrity_check.json` 저장
  ```python
  def save_integrity_report(
      date: str,
      channel: str,
      integrity: dict
  ):
      """
      data/source/api/{date}/.integrity_check.json 저장
      """
  ```
  - 파일: `GEM/api_collector/validator.py`

### 3.3 검증 실패 시 알림
- [ ] 알림 시스템 구현
  ```python
  def send_alert(integrity: dict):
      """
      무결성 검증 실패 시 알림
      - 로그 기록
      - 콘솔 출력
      - (옵션) 이메일/Slack 알림
      """
  ```
  - 파일: `GEM/api_collector/alerting.py` (신규)

- [ ] 재수집 UI 프롬프트
  ```python
  def prompt_recollect(missing_timestamps: list):
      """
      누락 구간 재수집 UI 표시
      """
  ```
  - 파일: `GEM/web/routes/api_collection.py`

---

## 📋 Phase 4: 실시간 수집 실패 처리

### 4.1 실패 요청 저장
- [ ] `.failed_requests.json` 관리
  ```python
  class FailedRequestManager:
      def save_failed_request(self, timestamp: datetime, reason: str):
          """실패 요청 기록"""

      def load_failed_requests(self) -> dict:
          """저장된 실패 요청 로드"""

      def update_request_status(self, timestamp: str, status: str):
          """요청 상태 업데이트 (pending/success/failed)"""
  ```
  - 파일: `GEM/api_collector/failed_request_manager.py` (신규)

### 4.2 재시도 스케줄러
- [ ] 매시 정각 재시도 로직
  ```python
  def retry_failed_requests(self):
      """
      1. .failed_requests.json 로드
      2. status='pending' 요청만 재시도
      3. 성공 → status='success'
      4. 실패 → retry_count++
      5. retry_count >= 5 → status='failed'
      """
  ```
  - 파일: `GEM/api_collector/realtime.py`
  - 호출 시점: 매시 00분

### 4.3 CSV Insert + Sort
- [ ] 재시도 데이터 삽입 함수
  ```python
  def insert_to_csv(
      csv_path: Path,
      timestamp: datetime,
      data: dict
  ):
      """
      1. CSV 로드
      2. 새 행 추가
      3. time 컬럼 기준 정렬
      4. 저장
      """
      df = pl.read_csv(csv_path)
      new_row = pl.DataFrame([{'time': ..., **data}])
      df = pl.concat([df, new_row]).sort('time')
      df.write_csv(csv_path)
  ```
  - 파일: `GEM/api_collector/storage.py`

### 4.4 재시도 제한
- [ ] 최대 5회 재시도 체크
  ```python
  MAX_RETRY_COUNT = 5

  if req['retry_count'] >= MAX_RETRY_COUNT:
      req['status'] = 'failed'
      logger.error(f"재시도 포기: {req['timestamp']}")
  ```
  - 파일: `GEM/api_collector/realtime.py`

---

## 📋 Phase 5: Phase 1 리팩토링

### 5.1 모드 파라미터 추가
- [ ] `run_phase1_internal()` 시그니처 변경
  ```python
  def run_phase1_internal(
      input_source: str,
      mode: str,  # ← 추가
      battery_profile: str,
      progress_callback=None
  ) -> dict:
      """
      Args:
          mode: 'api_realtime' | 'api_batch' | 'upload'
      """
  ```
  - 파일: `GEM/scripts/phase1_convert_data.py`

### 5.2 API Parquet 복사 로직
- [ ] API 모드 처리
  ```python
  if mode in ['api_realtime', 'api_batch']:
      # Parquet 파일 복사
      source_parquet = Path(input_source)
      dest_parquet = manager.phase1_dir / "battery_data.parquet"

      shutil.copy2(source_parquet, dest_parquet)

      # 메타데이터
      df = pl.read_parquet(source_parquet)
      row_count = len(df)

      metadata = {
          'source_type': mode,
          'source_file': str(source_parquet),
          'row_count': row_count,
          'schema_version': '3.0',
      }
  ```
  - 파일: `GEM/scripts/phase1_convert_data.py`

### 5.3 XD-HUB → API 변환
- [ ] 변환 함수 구현
  ```python
  def convert_xdhub_to_api_format(xdhub_csv_path: str) -> pl.DataFrame:
      """
      XD-HUB CSV (Long Format) → API CSV (Wide Format)

      Input (XD-HUB):
          time, rack_name, module_name, voltage_avg, temp_avg, ...

      Output (API):
          time, RACK_001.MODULE_01.voltage_avg, RACK_001.MODULE_01.temp_avg, ...
      """
      df = pl.read_csv(xdhub_csv_path)

      # TODO: Pivot 로직 구현
      # rack_name + module_name → 컬럼명 생성
      # 집계 컬럼 매핑

      return df_api_format
  ```
  - 파일: `GEM/scripts/converter.py` (신규)
  - **우선순위: 낮음** (현재 API 수집이 주 데이터 소스)

### 5.4 Upload 모드 처리
- [ ] 업로드 모드 로직
  ```python
  elif mode == 'upload':
      # XD-HUB CSV → API 형식 변환
      df = convert_xdhub_to_api_format(input_source)

      # Parquet 저장
      dest_parquet = manager.phase1_dir / "battery_data.parquet"
      df.write_parquet(dest_parquet, ...)

      metadata = {
          'source_type': 'upload',
          'source_file': str(input_source),
          ...
      }
  ```
  - 파일: `GEM/scripts/phase1_convert_data.py`

### 5.5 통합 테스트
- [ ] API Realtime 모드 테스트
  ```python
  result = run_phase1_internal(
      input_source="data/source/api/2025-12-26/bsc_ch_01_realtime.parquet",
      mode="api_realtime",
      battery_profile="LFP_CATL"
  )
  ```

- [ ] API Batch 모드 테스트
  ```python
  result = run_phase1_internal(
      input_source="data/source/api/2025-12-26/bsc_ch_01_batch.parquet",
      mode="api_batch",
      battery_profile="LFP_CATL"
  )
  ```

- [ ] Upload 모드 테스트
  ```python
  result = run_phase1_internal(
      input_source="uploaded_xdhub.csv",
      mode="upload",
      battery_profile="LFP_CATL"
  )
  ```

---

## 📋 Phase 6: 웹 UI 업데이트

### 6.1 데이터 소스 선택 UI
- [ ] Phase 1 입력 모드 선택
  ```html
  <select name="data_source">
    <option value="api_realtime">API 실시간 수집</option>
    <option value="api_batch">API 일괄 수집</option>
    <option value="upload">CSV 업로드</option>
  </select>
  ```
  - 파일: `GEM/web/templates/analysis.html`

### 6.2 무결성 검증 결과 표시
- [ ] 검증 결과 UI
  ```html
  <div class="integrity-check">
    <h3>무결성 검증 결과</h3>
    <p>상태: <span class="status-pass">✓ PASS</span></p>
    <p>예상 레코드: 288개</p>
    <p>실제 레코드: 288개</p>
    <p>누락: 0개</p>
    <p>중복: 0개</p>
  </div>
  ```
  - 파일: `GEM/web/templates/api_collection.html`

### 6.3 재수집 프롬프트
- [ ] 누락 구간 재수집 대화상자
  ```javascript
  if (integrity.status === 'FAIL') {
    showRecollectDialog(integrity.missing_timestamps);
  }
  ```
  - 파일: `GEM/web/static/js/api_collection.js`

---

## 📋 Phase 7: 로깅 및 모니터링

### 7.1 로그 구조 개선
- [ ] 날짜별 로그 파일
  ```
  logs/api_collection/
  ├── 2025-12-26_realtime.log
  ├── 2025-12-26_batch.log
  └── 2025-12-26_validator.log
  ```

### 7.2 검증 실패 로그
- [ ] 상세 로그 기록
  ```python
  logger.error(f"[{date}] 무결성 검증 실패")
  logger.error(f"  누락: {missing_timestamps}")
  logger.error(f"  중복: {duplicate_timestamps}")
  logger.error(f"  시간 갭: {time_gaps}")
  ```

### 7.3 재시도 로그
- [ ] 재시도 이력 추적
  ```python
  logger.info(f"[재시도] {timestamp} - 시도 {retry_count}/5")
  logger.success(f"[재시도 성공] {timestamp}")
  logger.error(f"[재시도 포기] {timestamp} - {reason}")
  ```

---

## 📊 우선순위 및 일정

### 🔴 높음 (1주차)
1. Phase 1: 파일명 규칙 구현
2. Phase 2: Parquet 변환 로직
3. Phase 3: 무결성 검증

### 🟡 중간 (2주차)
4. Phase 4: 실패 처리 시스템
5. Phase 5: Phase 1 리팩토링 (API 모드)

### 🟢 낮음 (3주차)
6. Phase 5: XD-HUB 변환 (백로그)
7. Phase 6: 웹 UI 고도화
8. Phase 7: 로깅 개선

---

## 📝 진행 상황

### 완료
- [x] 설계 문서 작성 (20_데이터-수집-저장-변환-전략.md)
- [x] TODO 리스트 작성

### 진행중
- [ ] Phase 1 구현

### 대기
- [ ] Phase 2~7 구현

---

**문서 버전:** 1.0.0
**최종 수정:** 2025-12-26
**담당자:** GEM Development Team
