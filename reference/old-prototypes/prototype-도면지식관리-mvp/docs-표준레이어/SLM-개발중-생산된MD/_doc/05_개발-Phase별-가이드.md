# 개발 Phase별 가이드

**문서 번호:** 05
**작성일:** 2025-12-11
**최종 업데이트:** 2025-12-26
**버전:** 2.0.0 (폴더 구조 개선 반영)

---

## 📋 Phase 개요 (v2.0.0)

```
Phase 1       ──▶  Phase 2      ──▶  Phase 3       ──▶  Phase 4
(데이터 변환)       (검증)            (AI 인사이트)       (리포트 생성)
phase1_convert     phase2_validate   phase3_insights    phase4_report
```

**Phase 1 (Convert)**: CSV → Parquet 표준화
**Phase 2 (Validate)**: 4가지 안전성 검증 (JSON 출력)
**Phase 3 (Insights)**: 5가지 AI 인사이트 (Markdown 출력)
**Phase 4 (Report)**: HTML 리포트 + summary.json 생성

### 실행 방법

**A. 명령어 방식 (개발자 테스트용)**
```bash
# Phase 1
python GEM/scripts/phase1_convert_data.py --csv data.csv

# Phase 2
python GEM/scripts/phase2_validate_safety.py --run_id 20251213_153045_NMC_LG

# Phase 3
python GEM/scripts/phase3_generate_insights.py --run_id 20251213_153045_NMC_LG --model qwen2.5:32b
```

**B. 웹 UI 방식 (사용자용)**
```bash
python GEM/app.py
# 브라우저에서 http://localhost:7860 접속
# Phase 1 → Phase 2 → Phase 3 탭 순서대로 실행
# 우측 챗봇에서 AI와 대화
```

---

## 🔧 Phase 1: 데이터 변환

### 목표
XD-HUB CSV → 배터리 표준 Parquet 변환 + **2중 출력 형식**

### 출력 형식
1. **battery_data.parquet**: 전체 데이터 (분석용, ZSTD 압축)
2. **battery_data_sample.csv**: 1,000행 샘플 (Excel 편집용)

### 출력 위치 (v2.0.0)
```
results/{RUN_ID}/
├── metadata.json                # 🆕 실행 메타데이터
└── phase1_convert/              # 🆕 폴더명 변경
    ├── standard_data.parquet    # 전체 데이터
    └── conversion_log.json      # 🆕 JSON 로그

data/source/upload/YYYYMMDD_HHMMSS/
└── original.csv                 # 원본 CSV 백업
```

### 핵심 모듈

**1. `modules/data_loader/file_loader.py`**
```python
def load_from_csv(rack_id: str) -> pd.DataFrame:
    """
    CSV 파일 로드 및 검증
    1. 파일 존재 확인
    2. pd.read_csv()
    3. validate_dataframe() 호출
    4. 검증 실패 시 DataValidationError 발생
    """
```

**2. `modules/data_loader/api_loader.py`**
```python
async def fetch_batch_async(rack_ids: List[str]) -> Dict:
    """
    Batch 비동기 수집
    1. 20개씩 묶음
    2. aiohttp 비동기 요청
    3. Retry (Exponential Backoff)
    4. Arrow Stream 파싱
    """
```

**3. `modules/sync_engine.py`**
```python
def align_timeseries(dfs: Dict[str, pd.DataFrame]) -> Dict:
    """
    시간축 동기화
    1. 기준 시간축 생성 (10s 간격)
    2. reindex(method='nearest')
    3. System 데이터 Broadcasting
    """
```

### 완료 기준 (DoD)

- [ ] CSV 로드 정상 작동
- [ ] Pydantic 검증 통과
- [ ] Partial Success (80%) 로직 동작
- [ ] Resampling 정확도 확인
- [ ] TC-1~4 테스트 통과

---

## 🧮 Phase 2: 검증 및 분석

### 목표
**4가지 핵심 검증** 실행 + **동일 시간축에 결과 추가**

### 4가지 검증
1. **Thermal Safety**: dT/dt > 임계값 감지
2. **SPC Balance**: Z-Score > ±3σ 감지
3. **Data Integrity**: 센서 고착/범위/NULL 감지
4. **System Correlation**: Rack ↔ DC 버스 상관계수 < 0.90 감지

### 출력 위치 (v2.0.0)
```
results/{RUN_ID}/
├── metadata.json                # 🆕 Phase 2 실행 정보 추가됨
├── phase1_convert/
│   └── standard_data.parquet    # 변환된 표준 데이터
└── phase2_validate/             # 🆕 폴더명 변경
    ├── thermal_safety.json      # 열적 안전성 검증 결과
    ├── spc_balance.json         # SPC 밸런싱 검증 결과
    ├── data_integrity.json      # 센서 무결성 검증 결과
    ├── system_correlation.json  # 시스템 상관성 검증 결과
    └── validation_log.json      # 🆕 JSON 로그
```

### 검증 컬럼 추가 방식
Phase 2는 Phase 1의 Parquet 파일에 다음 컬럼을 추가합니다:
- `dtdt` (float32): 온도 변화율
- `z_score` (float32): Z-Score
- `is_thermal_risk` (bool)
- `is_outlier` (bool)
- `correlation_coefficient` (float32)
- `sensor_frozen` (bool)
- `out_of_range` (bool)

### 핵심 알고리즘

**1. SPC (Z-Score)**
```python
def calculate_zscore(df: pd.DataFrame) -> pd.Series:
    mean = df['v_avg'].mean()
    std = df['v_avg'].std()
    z = (df['v_avg'] - mean) / std
    return z
```

**2. Thermal (dT/dt)**
```python
def calculate_thermal_rate(df: pd.DataFrame) -> pd.Series:
    # 분당 온도 변화율
    dt = df['t_max'].diff() / (10 / 60)  # 10초 → 분 변환
    return dt
```

**3. ISC (Correlation)**
```python
def detect_isc(df: pd.DataFrame) -> pd.Series:
    v_drop = df['v_avg'] < (df['v_avg'].mean() - 3 * df['v_avg'].std())
    t_rise = df['t_max'] > (df['t_max'].mean() + 3 * df['t_max'].std())
    return v_drop & t_rise
```

**4. Integrity (Frozen)**
```python
def check_frozen(df: pd.DataFrame) -> pd.Series:
    variance = df['t_max'].rolling(window=180).var()  # 30분
    return variance == 0
```

### 병렬 처리

```python
def execute_parallel(racks_data: Dict) -> Dict:
    with ProcessPoolExecutor(max_workers=CPU_COUNT) as pool:
        futures = []
        for rack_id, df in racks_data.items():
            future = pool.submit(analyze_rack, rack_id, df)
            futures.append(future)

        results = {}
        for future in as_completed(futures):
            rack_id, metrics, enriched_df = future.result()
            results[rack_id] = (metrics, enriched_df)

    return results
```

### 완료 기준 (DoD)

- [ ] 4대 알고리즘 구현
- [ ] PhysicsValidator 통합
- [ ] 병렬 처리 < 10초
- [ ] DataFrame 스키마 준수
- [ ] TC-1~4 테스트 통과

---

## 🧠 Phase 3: AI 인사이트 생성

### 목표
검증 결과 → **5가지 AI 인사이트** 자동 생성 (표준 프롬프트 템플릿 사용)

### 출력 위치 (v2.0.0)
```
results/{RUN_ID}/
├── metadata.json                   # 🆕 Phase 3 실행 정보 추가됨
├── phase2_validate/
│   └── (검증 결과 JSON 파일들)
└── phase3_insights/                # 🆕 폴더명 변경
    ├── insights_thermal.md         # 열적 안전성 인사이트
    ├── insights_spc.md             # SPC 밸런싱 인사이트
    ├── insights_integrity.md       # 센서 무결성 인사이트
    ├── insights_correlation.md     # 시스템 상관성 인사이트
    ├── insights_comprehensive.md   # 종합 인사이트
    └── insight_generation_log.json # 🆕 JSON 로그
```

### 5가지 인사이트 템플릿
1. **thermal_safety.txt**: 열적 안전성 분석
2. **spc_balance.txt**: SPC 밸런싱 분석
3. **data_integrity.txt**: 센서 무결성 검증
4. **system_correlation.txt**: 시스템 상관성 분석
5. **comprehensive.txt**: 종합 인사이트

### 핵심 프로세스

**1. Context Builder**
```python
def build_semantic_context(analysis_results: Dict) -> str:
    """
    Semantic YAML 생성
    1. Top 5 위험 Rack만 포함 (토큰 절약)
    2. Validation Failed 항목 분리
    3. 의미 부여 ("4.2 (Critical)" 형태)
    """

    yaml_content = f"""
meta:
  period: "{start_time} ~ {end_time}"

key_findings:
  - type: CRITICAL
    target: Rack_012
    issue: Thermal Runaway Risk
    evidence: dT/dt = 12.5 (threshold: 2.0)

sensor_errors:
  - rack_id: Rack_034
    reason: Z-Score > 20.0 (noise)
"""
    return yaml_content
```

**2. LLM Client (Retry + Fallback)**
```python
async def generate_insight(context_yaml: str) -> str:
    for attempt in range(3):
        try:
            response = await asyncio.wait_for(
                call_ollama(context_yaml),
                timeout=60.0
            )
            return response

        except asyncio.TimeoutError:
            if attempt == 2:  # 최종 실패
                return generate_static_report(context_yaml)

            await asyncio.sleep(2 ** attempt)  # Backoff
```

### 완료 기준 (DoD)

- [ ] Semantic YAML 변환
- [ ] Guardrail 프롬프트 적용
- [ ] Timeout/Fallback 동작
- [ ] TC-1~4 테스트 통과

---

## 💾 Phase 4: HTML 리포트 생성

### 목표
**HTML 리포트** + **summary.json** 생성 (오프라인 뷰어)

### 출력 위치 (v2.0.0)
```
results/{RUN_ID}/
├── metadata.json                # 🆕 Phase 4 실행 정보 추가됨
├── phase3_insights/
│   └── (인사이트 Markdown 파일들)
└── phase4_report/               # 🆕 폴더명 변경 (기존 final/)
    ├── report.html              # HTML 리포트 (Chart.js 포함)
    └── summary.json             # 🆕 핵심 지표 요약
```

### 리포트 구성
1. **report.html**:
   - 4개 Chart.js 인터랙티브 그래프
   - 5가지 AI 인사이트 (Markdown → HTML 변환)
   - LG Energy Solution 표준 색상 팔레트
   - 완전 오프라인 뷰어

2. **summary.json**:
   - 핵심 지표 요약 (total_racks, critical_count, warning_count 등)
   - Top 5 위험 Rack 목록
   - 검증 요약 통계
   - 대시보드 API 응답용

### Atomic Write 패턴

```python
def atomic_write(file_path: str, content: any):
    temp_path = file_path + ".tmp"

    try:
        # 1. 임시 파일 쓰기
        with open(temp_path, 'w') as f:
            f.write(content)

        # 2. Rename (원자적 연산)
        os.rename(temp_path, file_path)

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise StorageError(f"Write failed: {e}")
```

### 뷰어 구조

```
index.html
    │
    ├─ Zone A: AI 리포트 (Markdown)
    │   └─ marked.js 렌더링
    │
    ├─ Zone B: 위험도 랭킹 리스트
    │   └─ system_summary.yaml 기반
    │
    └─ Zone C: 상세 차트 (On-Demand)
        └─ Chart.js + Zoom Plugin
```

### 완료 기준 (DoD)

- [ ] Atomic Write 구현
- [ ] 표준 디렉토리 구조 준수
- [ ] Path Sanitization 적용
- [ ] Chart.js 렌더링
- [ ] TC-1~4 테스트 통과

---

## 🚀 Phase 5: 통합 및 배포

### 목표
**운영 API** + **Dev Console** 완성

### Dev Console 구성

**Backend: WebSocket 로그 스트리밍**
```python
# dev_server.py
@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    # Python logging → WebSocket broadcast
    while True:
        log_msg = await log_queue.get()
        await websocket.send_text(log_msg)
```

**Frontend: 자동 재연결**
```javascript
class WebSocketManager {
    constructor(url) {
        this.url = url;
        this.retryCount = 0;
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onclose = () => {
            if (this.retryCount < 5) {
                const delay = Math.pow(2, this.retryCount) * 1000;
                setTimeout(() => this.connect(), delay);
                this.retryCount++;
            }
        };
    }
}
```

### 운영 API 보안

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://xd-works.lss.com"],
    allow_credentials=True
)

@app.post("/analyze")
async def analyze(
    request: AnalyzeRequest,
    api_key: str = Depends(verify_api_key)  # 인증
):
    trace_id = generate_trace_id()
    result = await pipeline.run_full(request.params)
    return {"report_url": result.viewer_url}
```

### 완료 기준 (DoD)

- [ ] WebSocket 재연결 구현
- [ ] API Key 인증
- [ ] 성능 모니터링 배지
- [ ] Mock XD-Works 테스트
- [ ] 배포 체크리스트 완료

---

## 🧪 각 Phase별 핵심 테스트 케이스

### Phase 1
- **TC-1:** 부분 성공 (140/160 성공)
- **TC-2:** 치명적 실패 (100/160 실패)
- **TC-3:** 데이터 검증 (V_max=999V)
- **TC-4:** 시간축 동기화

### Phase 2
- **TC-1:** 정상 연산 (Z=1.2, dT=0.5)
- **TC-2:** 센서 오류 (dT/dt=50)
- **TC-3:** ISC 탐지
- **TC-4:** 성능 < 10초

### Phase 3
- **TC-1:** 정상 응답 (5초 내)
- **TC-2:** 타임아웃 & Fallback
- **TC-3:** Sensor Error 분리
- **TC-4:** Guardrail 방어

### Phase 4
- **TC-1:** 무결성 저장 (강제 종료)
- **TC-2:** Path Traversal 차단
- **TC-3:** 뷰어 데이터 로드
- **TC-4:** 대용량 렌더링

### Phase 5
- **TC-1:** 보안 차단 (No API Key)
- **TC-2:** 경로 공격 차단
- **TC-3:** WS 재연결
- **TC-4:** 상태 모니터링

---

## 🎯 전체 프로젝트 완료 기준

### 기능
- [ ] 5개 Phase 모두 완료
- [ ] 4대 진단 알고리즘 정확도 검증
- [ ] Dev Console 정상 작동
- [ ] 단일 뷰어 렌더링

### 품질
- [ ] 모든 Phase 테스트 통과
- [ ] PhysicsValidator 적용
- [ ] Partial Success 시나리오
- [ ] 성능 SLA 충족 (< 15초)

### 보안
- [ ] API Key 인증
- [ ] Path Sanitization
- [ ] CORS 제한
- [ ] Prompt Guardrail

### 문서
- [ ] README.md
- [ ] API 명세서
- [ ] 배포 가이드
- [ ] 사용자 매뉴얼

---

**이전 문서:** [04_품질-및-보안.md](./04_품질-및-보안.md)
**다음 문서:** [06_기술-스택-및-도구.md](./06_기술-스택-및-도구.md)
