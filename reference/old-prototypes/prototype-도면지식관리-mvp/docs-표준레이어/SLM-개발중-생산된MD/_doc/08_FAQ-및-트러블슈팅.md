# FAQ 및 트러블슈팅

**문서 번호:** 08
**작성일:** 2025-12-11

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1. Dual Engine 구조가 뭔가요?

**A:** SLM(지능)과 Python(연산)을 물리적으로 분리한 아키텍처입니다.

- **문제:** SLM은 3.4억 건 데이터를 직접 계산할 수 없음 (토큰/메모리 한계)
- **해결:** Python이 계산한 결과를 요약해서 SLM에게 전달
- **장점:** 정확성(Python) + 해석력(SLM) 동시 확보

---

### Q2. 왜 No-DB 전략을 사용하나요?

**A:** 폐쇄망 환경 + 운영 복잡도 최소화

- **장점:**
  - DB 서버 불필요 (설치/관리 부담 없음)
  - Parquet는 SQL만큼 빠름
  - 파일 시스템 = 버전 관리 + 백업 용이
- **단점:**
  - 동시 쓰기 제한 (Atomic Write로 해결)
  - 쿼리 복잡도 (분석 결과는 작아서 문제 없음)

---

### Q3. Partial Success 80%의 근거는?

**A:** 과거 데이터 분석 결과

- 80% 미만 시 시스템 상관관계 분석 오차율 급증
- False Positive 17% 상승 구간 확인
- 안전 마진 20% 확보

---

### Q4. PhysicsValidator가 왜 필요한가요?

**A:** 센서 오류를 화재로 오탐지하는 것을 방지

**예시:**
- dT/dt = 50°C/min (센서 노이즈)
- AI: "열폭주 발생!" (오탐)
- 검증기: "물리적 불가능 → 센서 점검 필요" (정확)

---

### Q5. SLM Fallback은 언제 사용되나요?

**A:** AI 응답이 60초 내 안 올 때

- Ollama 서버 다운
- 네트워크 지연
- 모델 과부하

**Fallback 리포트:**
```markdown
# 자동 분석 리포트 (AI 응답 없음)

**시스템 상태:** CRITICAL
**위험 감지:** 총 2개 Rack

## 주요 위험 설비
- Rack_012: Thermal Risk (dT/dt=12.5)
- Rack_005: ISC Detected

> AI 모델 응답 지연으로 수치 기반 요약본 제공
```

---

### Q6. 뷰어가 왜 "단일 정적"인가요?

**A:** 서버 부하 최소화 + 배포 간소화

- **기존 방식:** 분석마다 HTML 생성 → 중복 리소스
- **개선 방식:** 뷰어 1개 + 데이터만 교체
- **장점:**
  - URL 파라미터로 데이터 경로 전달
  - 캐싱 효율 극대화
  - 버전 업그레이드 시 파일 1개만 교체

---

### Q7. WebSocket 재연결이 왜 중요한가요?

**A:** 분석 시간이 길 수 있어서

- Phase 2 연산: 최대 10초
- Phase 3 AI: 최대 60초
- 중간에 네트워크 끊김 시 로그 손실 → 디버깅 불가
- 자동 재연결 → 로그 연속성 유지

---

## 🔧 트러블슈팅

### ❌ 문제 1: "데이터 수집률 80% 미만"

**증상:**
```
CriticalFailure: Data collection rate (65%) below threshold
```

**원인:**
1. XD-HUB API 서버 불안정
2. 네트워크 불량
3. 잘못된 Tag 이름 (`target_tags.txt`)

**해결:**
```bash
# 1. API 서버 상태 확인
curl http://xd-hub:8080/health

# 2. failed_racks.json 확인
cat results/20251130_A001/logs/failed_racks.json

# 3. target_tags.txt 검증
python scripts/validate_tags.py config/target_tags.txt
```

---

### ❌ 문제 2: "PhysicsValidator 대량 실패"

**증상:**
```
WARNING: 50% of racks failed physics validation
```

**원인:**
- 센서 캘리브레이션 오류
- 임계값 설정 오류
- 실제 이상 징후 (드물게)

**해결:**
```python
# 1. validation_report.yaml 확인
cat results/.../summary/validation_report.yaml

# 2. 임계값 조정 (config.yaml)
physics_thresholds:
  max_dtdt: 10.0  # 15.0으로 완화 시도

# 3. 특정 Rack 제외
vip_racks:
  exclude_validation: ["Rack_034"]  # 센서 교체 예정
```

---

### ❌ 문제 3: "SLM 응답 없음 (Timeout)"

**증상:**
```
ERROR: SLM timeout after 60s
INFO: Switching to fallback report
```

**원인:**
1. Ollama 서버 미실행
2. 모델 미다운로드
3. 컨텍스트 토큰 과다

**해결:**
```bash
# 1. Ollama 상태 확인
ollama list
ollama ps

# 2. 모델 다운로드
ollama pull gemma2:27b

# 3. 서버 재시작
ollama serve

# 4. 토큰 줄이기 (context_builder.py)
# Top 5 → Top 3로 변경
```

---

### ❌ 문제 4: "뷰어 차트 깨짐"

**증상:**
- 차트 영역만 빈 화면
- 브라우저 콘솔 에러

**원인:**
1. JSON 파싱 실패
2. Chart.js 버전 불일치
3. 데이터 크기 과다

**해결:**
```javascript
// 1. 브라우저 콘솔 확인
F12 → Console

// 2. JSON 유효성 검사
fetch('/data/20251130_A001/racks/rack_001_ts.json')
  .then(r => r.json())
  .then(console.log)

// 3. 데이터 포인트 제한 (decimation)
new Chart(ctx, {
  options: {
    plugins: {
      decimation: {
        enabled: true,
        algorithm: 'lttb',
        samples: 1000
      }
    }
  }
})
```

---

### ❌ 문제 5: "성능 SLA 초과 (> 15초)"

**증상:**
```
WARNING: Total pipeline: 27070ms (SLA: 15000ms)
```

**원인:**
1. CPU 코어 부족
2. 메모리 부족 (스왑 발생)
3. 데이터 크기 예상 초과

**해결:**
```python
# 1. 병렬 Worker 수 조정
ProcessPoolExecutor(max_workers=8)  # CPU 코어 수에 맞춤

# 2. Batch 크기 조정
config.yaml:
  data:
    batch_size: 10  # 20 → 10

# 3. 데이터 샘플링 (비상시)
df = df[::2]  # 20초 간격으로 다운샘플링
```

---

### ❌ 문제 6: "API Key 인증 실패"

**증상:**
```
401 Unauthorized: Invalid API Key
```

**원인:**
1. `.env` 파일 누락
2. 환경변수 미로드
3. Key 만료

**해결:**
```bash
# 1. .env 파일 확인
cat .env
# GEM_API_KEY=your_key

# 2. 환경변수 로드 확인
echo $GEM_API_KEY  # Linux/Mac
echo %GEM_API_KEY%  # Windows

# 3. Key 재생성
python scripts/generate_api_key.py
```

---

### ❌ 문제 7: "Atomic Write 실패"

**증상:**
```
StorageError: Failed to rename temp file
```

**원인:**
1. 디스크 공간 부족
2. 파일 권한 문제
3. 바이러스 백신 간섭 (Windows)

**해결:**
```bash
# 1. 디스크 공간 확인
df -h  # Linux
Get-PSDrive  # Windows

# 2. 권한 확인
ls -la results/  # Linux
icacls results\  # Windows

# 3. 임시 파일 정리
find results/ -name "*.tmp" -delete
```

---

### ❌ 문제 8: "WebSocket 재연결 실패"

**증상:**
```
Console: WebSocket disconnected (재연결 시도 5회 실패)
```

**원인:**
1. 서버 완전 다운
2. 포트 차단 (방화벽)
3. 프록시 간섭

**해결:**
```bash
# 1. 서버 재시작
python dev_server.py

# 2. 포트 확인
netstat -an | grep 8000  # Linux
netstat -an | findstr 8000  # Windows

# 3. 브라우저 하드 리프레시
Ctrl + Shift + R
```

---

## 🐛 알려진 이슈 (Known Issues)

### Issue #1: IE11 미지원
- **상태:** Won't Fix
- **이유:** 모던 브라우저 전용 (Chart.js, ES6+)
- **대안:** Edge, Chrome, Firefox 사용

### Issue #2: 대용량 데이터 (> 100MB) 뷰어 느림
- **상태:** In Progress
- **해결책:** Parquet.wasm 검토 중

### Issue #3: Ollama GPU 가속 불안정 (AMD)
- **상태:** Known Upstream
- **임시 해결:** CPU 모드 사용

---

## 📞 지원 연락처

### 기술 지원
- **이메일:** support@gem-project.com
- **Slack:** #gem-support
- **GitHub Issues:** https://github.com/gem/issues

### 긴급 연락
- **운영 장애:** hotline@company.com
- **보안 이슈:** security@company.com

---

**이전 문서:** [07_개발-방법론.md](./07_개발-방법론.md)
**다음 문서:** [README.md](./README.md) (프로젝트 루트)
