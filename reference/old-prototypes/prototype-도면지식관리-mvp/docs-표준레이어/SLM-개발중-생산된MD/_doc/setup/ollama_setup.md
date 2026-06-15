# Ollama 설치 및 설정 가이드

## 📋 개요

GEM 시스템은 **2개의 Ollama 모델**을 사용합니다:

| 모델 | 크기 | 용도 | 위치 |
|------|------|------|------|
| **qwen2.5:14b** | 8GB | 일반 대화 (엔지니어 ↔ AI) | main.py:219 |
| **qwen2.5:32b** | 20GB | Phase 3 AI 인사이트 생성 | main.py:473 |

**총 용량**: ~28GB

---

## 🚀 설치 방법

### 1. Ollama 서버 설치

#### Windows:
1. https://ollama.com/download 접속
2. **Windows용 설치 파일** 다운로드
3. 설치 파일 실행
4. 설치 완료 후 **자동으로 백그라운드 서비스 실행**

#### 설치 확인:
```bash
ollama --version
```

출력 예시:
```
ollama version 0.1.26
```

---

### 2. AI 모델 다운로드

#### 모델 1: qwen2.5:14b (일반 대화용)
```bash
ollama pull qwen2.5:14b
```

**다운로드 시간**: 약 5-10분 (인터넷 속도에 따라)
**용량**: ~8GB

#### 모델 2: qwen2.5:32b (인사이트 생성용)
```bash
ollama pull qwen2.5:32b
```

**다운로드 시간**: 약 15-20분 (인터넷 속도에 따라)
**용량**: ~20GB

#### 다운로드 확인:
```bash
ollama list
```

출력 예시:
```
NAME              ID              SIZE      MODIFIED
qwen2.5:14b       abc123def456    8.0 GB    2 minutes ago
qwen2.5:32b       def789ghi012    20 GB     5 minutes ago
```

---

## 🔧 실행 방법

### 옵션 1: 자동 실행 (Windows 서비스)

Ollama 설치 시 **자동으로 백그라운드 서비스**로 실행됩니다.

**확인 방법:**
```bash
# PowerShell
Get-Service | findstr ollama
```

**서비스 상태:**
- Running: 정상 실행 중 ✅
- Stopped: 수동으로 시작 필요

---

### 옵션 2: 수동 실행

#### 방법 A: 배치 파일 사용 (추천)
```bash
start_ollama.bat
```

#### 방법 B: 직접 명령어
```bash
ollama serve
```

**실행 확인:**
- 브라우저에서 http://localhost:11434 접속
- "Ollama is running" 메시지 확인

---

## 💬 사용 시나리오

### 1. 일반 대화 (qwen2.5:14b)

**엔지니어 ↔ AI 대화:**
```
엔지니어: "임계값을 3.0으로 변경해줘"
AI (14b): "임계값을 3.0℃/min으로 변경하겠습니다.
          이는 기본값 2.0보다 50% 완화된 기준입니다.
          분석을 진행할까요?"
```

**특징:**
- ✅ 빠른 응답 (~2-3초)
- ✅ 파라미터 변경 대화
- ✅ 실시간 상호작용

---

### 2. AI 인사이트 생성 (qwen2.5:32b)

**Phase 3에서 자동 실행:**
```
검증 결과 입력:
- 열적 안전성: 5건 검출
- SPC 밸런싱: 2건 검출
- 센서 무결성: 0건
- 시스템 상관성: 1건 검출

AI (32b) 인사이트 생성:
1. 위험도 평가
   - 임계값 대비 최대 210% 초과
   - 열폭주 전조 증상 감지

2. 원인 분석
   - 고속 충전 시 냉각 불충분
   - BMS 제어 지연 가능성

3. 개선 방안
   - 충전 전류 20% 감소 권장
   - 냉각 팬 용량 증설 검토
   - BMS 펌웨어 업데이트
```

**특징:**
- ✅ 고품질 분석 (~30-60초)
- ✅ 전문가 수준 인사이트
- ✅ 구체적 개선 방안 제시

---

## 🔍 문제 해결

### 1. "Ollama is not installed" 오류

**원인**: Ollama 서버 미설치

**해결**:
```bash
# 다운로드 및 설치
https://ollama.com/download
```

---

### 2. "Connection refused [WinError 10061]" 오류

**원인**: Ollama 서버 미실행

**해결**:
```bash
# 옵션 1: 배치 파일
start_ollama.bat

# 옵션 2: 직접 실행
ollama serve
```

---

### 3. "Model not found" 오류

**원인**: 모델 미다운로드

**해결**:
```bash
# 일반 대화용
ollama pull qwen2.5:14b

# 인사이트용
ollama pull qwen2.5:32b
```

---

### 4. Ollama 서버 상태 확인

```bash
# 서비스 확인 (PowerShell)
Get-Service | findstr ollama

# 프로세스 확인
tasklist | findstr ollama

# 포트 확인
netstat -an | findstr 11434
```

**정상 출력**:
```
TCP    0.0.0.0:11434    0.0.0.0:0    LISTENING
```

---

## 📊 시스템 요구사항

### 최소 사양:
- **RAM**: 16GB 이상
- **디스크 공간**: 30GB 이상 (모델 저장)
- **CPU**: 8코어 이상 권장

### 권장 사양:
- **RAM**: 32GB 이상
- **GPU**: NVIDIA GPU (CUDA 지원 시 10배 빠름)
- **디스크**: SSD (모델 로딩 속도 향상)

---

## 🎯 성능 최적화

### 1. GPU 사용 (NVIDIA)

Ollama는 자동으로 NVIDIA GPU를 감지하여 사용합니다.

**확인**:
```bash
ollama run qwen2.5:14b "Hello"
```

출력에 GPU 정보가 표시되면 GPU 사용 중 ✅

---

### 2. 메모리 최적화

**config 파일 생성** (고급 사용자):
```bash
# ~/.ollama/config.json
{
  "num_ctx": 4096,
  "num_gpu": 1
}
```

---

## 📝 모델 전환 (선택사항)

### 더 작은 모델 사용 (속도 우선)

**main.py 수정**:
```python
# 일반 대화 (line 219)
model="qwen2.5:7b"  # 14b → 7b

# 인사이트 (line 473)
model="qwen2.5:14b"  # 32b → 14b
```

**다운로드**:
```bash
ollama pull qwen2.5:7b
```

---

### 다른 모델 사용

**추천 대안**:
- `llama3:8b` - Meta의 Llama 3 (8GB)
- `mistral:7b` - Mistral AI (4GB)
- `gemma:7b` - Google Gemma (5GB)

**변경 방법**:
1. 모델 다운로드: `ollama pull llama3:8b`
2. main.py에서 모델명 변경
3. 서버 재시작

---

## 🔄 업데이트

### Ollama 서버 업데이트
```bash
# Windows
winget upgrade Ollama.Ollama
```

### 모델 업데이트
```bash
ollama pull qwen2.5:14b
ollama pull qwen2.5:32b
```

---

## 📞 지원

### 공식 문서:
- https://github.com/ollama/ollama
- https://ollama.com/docs

### GEM 프로젝트:
- 이슈 보고: GitHub Issues
- 문의: 프로젝트 관리자

---

## ✅ 설치 완료 체크리스트

- [ ] Ollama 서버 설치 완료
- [ ] `ollama --version` 확인
- [ ] `qwen2.5:14b` 모델 다운로드
- [ ] `qwen2.5:32b` 모델 다운로드
- [ ] `ollama list` 확인 (2개 모델 표시)
- [ ] `ollama serve` 실행 확인
- [ ] http://localhost:11434 접속 확인
- [ ] GEM 웹 UI에서 대화 테스트
- [ ] Phase 3 인사이트 생성 테스트

**모두 완료되면 GEM 시스템을 사용할 준비가 완료되었습니다!** 🎉
