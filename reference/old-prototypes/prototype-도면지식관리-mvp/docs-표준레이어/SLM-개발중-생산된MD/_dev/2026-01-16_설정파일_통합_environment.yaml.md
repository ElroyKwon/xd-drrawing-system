# 설정 파일 통합 완료 (environment.yaml)

## 작업 일시
2026-01-16

## 작업 목적
GEM 시스템의 AI 모델 설정이 여러 파일에 중복 분산되어 있어 관리가 어려웠음.
- `config/ai/models.yaml` - AI 모델 설정
- `config/environment.yaml` - 환경 설정 (사용 안됨)
- `.env` - Ollama 서버 주소

**목표**: 모든 설정을 `config/environment.yaml` 하나로 통합

## 변경 사항

### 1. config/environment.yaml 수정
GPU 설정을 `ai_server.ollama.gpu` 섹션으로 추가:

```yaml
ai_server:
  ollama:
    enabled: true
    host: "10.255.255.70"
    port: 11434
    base_url: "http://10.255.255.70:11434"

    # 현재 사용 중인 모델
    active_models:
      chat: "qwen3-coder:30b"
      insight: "qwen3-coder:30b"

    # GPU 설정 (통합)
    gpu:
      use_gpu: true
      gpu_layers: -1
      num_gpu: 1
      main_gpu: 1
      low_vram: false
      numa: false

    # 타임아웃 설정
    timeout:
      connect: 10
      read: 300

    # 재시도 설정
    retry:
      max_attempts: 3
      backoff_factor: 2
```

### 2. config/config_loader.py 수정
`load_ai_model_config()` 함수가 `environment.yaml`에서 읽도록 수정:

**기존**:
```python
def load_ai_model_config() -> Dict[str, Any]:
    """AI 모델 설정 로드"""
    models_file = Path(__file__).parent / "ai" / "models.yaml"
    # ...
```

**변경**:
```python
def load_ai_model_config() -> Dict[str, Any]:
    """AI 모델 설정 로드 (environment.yaml에서)"""
    env_file = Path(__file__).parent / "environment.yaml"

    with open(env_file, 'r', encoding='utf-8') as f:
        env_config = yaml.safe_load(f)

    ollama_config = env_config.get('ai_server', {}).get('ollama', {})
    active_models = ollama_config.get('active_models', {})
    gpu_config = ollama_config.get('gpu', {})

    model_config = {
        'chat_model': active_models.get('chat', 'qwen3-coder:30b'),
        'insight_model': active_models.get('insight', 'qwen3-coder:30b'),
        'use_gpu': gpu_config.get('use_gpu', True),
        'gpu_layers': gpu_config.get('gpu_layers', -1),
        'num_gpu': gpu_config.get('num_gpu', 1),
        'main_gpu': gpu_config.get('main_gpu', 1),
        'low_vram': gpu_config.get('low_vram', False),
        'numa': gpu_config.get('numa', False),
    }

    return model_config
```

### 3. main.py 수정
`.env` 파일 대신 `environment.yaml`에서 Ollama 서버 주소 읽기:

**기존**:
```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Ollama 설정
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://10.255.255.70:11434")
```

**변경**:
```python
from config.config_loader import load_environment_config

# 환경 설정 로드
env_config = load_environment_config()
ollama_config = env_config.get('ai_server', {}).get('ollama', {})
OLLAMA_BASE_URL = ollama_config.get('base_url', "http://10.255.255.70:11434")
```

**삭제된 import**:
- `import os`
- `from dotenv import load_dotenv`

### 4. 파일 삭제
```bash
rm GEM/config/ai/models.yaml
```

기존 `models.yaml` 파일 제거 (더 이상 사용하지 않음)

## 최종 설정 파일 구조

```
GEM/
├── config/
│   ├── environment.yaml       ← 모든 환경/AI 설정 통합 (✅ 사용 중)
│   ├── config_loader.py       ← environment.yaml 로드
│   ├── ai/
│   │   ├── commands.yaml      ← AI 명령어 정의
│   │   └── prompts/           ← AI 프롬프트 템플릿
│   ├── battery/
│   │   └── profiles/          ← 배터리 프로파일
│   └── analysis/
│       └── thresholds/        ← 분석 임계값
└── .env                        ← 삭제 예정 (더 이상 사용 안함)
```

## 설정 변경 방법

**이제 모든 설정은 `config/environment.yaml`에서 변경**:

### AI 모델 변경
```yaml
ai_server:
  ollama:
    active_models:
      chat: "qwen3-coder:30b"     # 채팅 모델
      insight: "qwen3-coder:30b"  # 인사이트 모델
```

### GPU 설정 변경
```yaml
ai_server:
  ollama:
    gpu:
      use_gpu: true      # GPU 사용 여부
      gpu_layers: -1     # -1 = 전체 GPU 사용
      num_gpu: 1         # GPU 개수
      main_gpu: 1        # 주 GPU 인덱스 (0부터 시작)
      low_vram: false    # VRAM 부족 시 true
```

### 서버 주소 변경
```yaml
ai_server:
  ollama:
    host: "10.255.255.70"
    port: 11434
    base_url: "http://10.255.255.70:11434"
```

**⚠️ 변경 후 서버 재시작 필요!**

## 테스트 방법

1. **서버 시작**:
   ```bash
   cd GEM
   python main.py
   ```

2. **AI 모델 로드 확인**:
   - 서버 시작 시 로그에서 `qwen3-coder:30b` 모델 로드 확인
   - GPU 1번 사용 확인

3. **채팅 테스트**:
   - 웹 인터페이스에서 "배터리 프로파일" 명령어 실행
   - AI 응답 정상 동작 확인

## 장점

### 1. 단일 설정 소스
- 모든 환경 설정이 `environment.yaml` 한 곳에
- 설정 충돌 방지
- 관리 간소화

### 2. 명확한 구조
```yaml
ai_server:          # AI/LLM 서버
web_server:         # 웹 서버
storage:            # 스토리지
api_collection:     # API 수집
notifications:      # 알림
logging:            # 로깅
performance:        # 성능
environment:        # 환경 정보
security:           # 보안
```

### 3. 환경별 관리 용이
- 개발/스테이징/프로덕션 환경별로 `environment.yaml` 분리 가능
- Git에서 환경별 브랜치 관리 용이

### 4. 문서화
- `environment.yaml` 자체에 상세한 주석 포함
- 어떤 설정을 어디서 변경하는지 명확

## 주의사항

1. **서버 재시작 필수**: 설정 변경 후 반드시 서버 재시작
2. **.env 파일 제거 예정**: 더 이상 사용하지 않으므로 향후 삭제 가능
3. **GPU 설정 확인**: `main_gpu: 1`이 GPU 1번을 의미 (0부터 시작)

## 파일 변경 목록

- ✅ `config/environment.yaml` - GPU 설정 추가
- ✅ `config/config_loader.py` - environment.yaml에서 로드
- ✅ `main.py` - dotenv 제거, environment.yaml 사용
- ✅ `config/ai/models.yaml` - 삭제 (obsolete)
