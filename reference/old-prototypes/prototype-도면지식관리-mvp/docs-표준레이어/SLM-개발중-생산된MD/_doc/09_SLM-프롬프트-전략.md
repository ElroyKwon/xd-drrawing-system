# SLM 프롬프트 전략

**문서 번호:** 09
**작성일:** 2025-12-11
**최종 업데이트:** 2025-12-13

---

## 📝 표준 프롬프트 템플릿 (2025-12-13 추가)

### 개요
Phase 3에서 일관된 AI 인사이트 생성을 위한 **5가지 표준 프롬프트 템플릿**이 추가되었습니다.

### 템플릿 위치
```
config/prompts/
├── thermal_safety.txt           # 열적 안전성 분석
├── spc_balance.txt              # SPC 밸런싱 분석
├── data_integrity.txt           # 센서 무결성 검증
├── system_correlation.txt       # 시스템 상관성 분석
└── comprehensive.txt            # 종합 인사이트
```

### 일관성 보장
- **모델**: qwen2.5:32b
- **Temperature**: 0.1 (결정론적 출력)
- **결과**: 동일 입력 → 동일 결과

### 사용 방법
```python
import ollama
import json

# 프롬프트 템플릿 로드
with open("config/prompts/thermal_safety.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# Phase 2 검증 결과 로드
with open(f"results/{run_id}/phase2_validate/thermal_safety.json") as f:
    detection_data = json.load(f)

# AI 인사이트 생성
response = ollama.chat(
    model="qwen2.5:32b",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(detection_data, ensure_ascii=False)}
    ],
    options={"temperature": 0.1}
)

# 인사이트 저장
with open(f"results/{run_id}/phase3_insights/insights_thermal.md", "w", encoding="utf-8") as f:
    f.write(response['message']['content'])
```

### Custom Prompt 지원
사용자가 추가 분석을 요청할 경우:
1. 표준 프롬프트 + Custom 지시사항 결합
2. `results/{RUN_ID}/custom_prompts.yaml`에 기록

```yaml
- timestamp: "2025-12-13T17:00:00Z"
  analysis_type: "thermal_safety"
  prompt: "RACK_05 주변 Rack에 미치는 영향을 분석해주세요."
```

자세한 내용은 `_dev/10_AI-프롬프트-가이드.md` 참조

---

## 🎯 프롬프트 프레임워크 선정

### 최종 권장: **DSPy**

| 프레임워크 | 장점 | 단점 | GEM 적합도 |
|-----------|------|------|-----------|
| **DSPy** | - 자동 프롬프트 최적화<br>- Signature 기반 타입 안전<br>- 최저 오버헤드 (3.53ms) | 학습 곡선 존재 | ⭐⭐⭐⭐⭐ |
| LangChain | 성숙한 에코시스템 | 복잡함, 느림 (8.02ms) | ⭐⭐⭐ |
| LlamaIndex | RAG 강력 | 프롬프트 제어 약함 | ⭐⭐ |

**선정 이유:**
1. **타입 안전성**: Pydantic 스키마 연동으로 출력 검증
2. **자동 최적화**: 수동 프롬프트 튜닝 불필요
3. **성능**: 오버헤드 3.53ms (LangChain 대비 2.3배 빠름)
4. **Guardrail 통합**: 물리 법칙 검증과 자연스럽게 결합

---

## 📐 DSPy Signature 정의

### 1. 기본 Signature 구조

```python
# modules/intelligence/dspy_prompts.py
import dspy
from pydantic import BaseModel, Field
from typing import Literal

class BatteryAnalysisSignature(dspy.Signature):
    """배터리 안전 위험 분석 및 리포트 생성

    역할:
    - Python 계산 엔진이 제공한 수치 결과를 해석
    - 물리 법칙 검증 결과를 반영
    - 한국어로 명확한 리포트 작성
    """

    # === 입력 필드 ===
    summary_data: str = dspy.InputField(
        desc="Python 계산 결과 요약 (YAML 형식, 상위 5개 위험 Rack 포함)"
    )

    physics_validation: str = dspy.InputField(
        desc="물리 법칙 검증 결과 (센서 오류 감지 포함)"
    )

    # === 출력 필드 ===
    risk_assessment: str = dspy.OutputField(
        desc="위험도 평가 (CRITICAL/WARNING/NORMAL 중 하나)",
        prefix="## 위험도 평가\n"
    )

    technical_analysis: str = dspy.OutputField(
        desc="기술 분석 (원인 메커니즘, 물리 현상 설명)",
        prefix="## 기술 분석\n"
    )

    recommendations: str = dspy.OutputField(
        desc="조치 권고 사항 (우선순위 순서)",
        prefix="## 조치 권고\n"
    )


class BatteryAnalyzer(dspy.Module):
    """배터리 분석 모듈 (Chain of Thought 적용)"""

    def __init__(self):
        super().__init__()
        self.generate_report = dspy.ChainOfThought(BatteryAnalysisSignature)

    def forward(self, summary_data: str, physics_validation: str):
        """분석 실행

        Args:
            summary_data: YAML 형식 요약 데이터
            physics_validation: 물리 검증 결과

        Returns:
            dspy.Prediction with risk_assessment, technical_analysis, recommendations
        """
        return self.generate_report(
            summary_data=summary_data,
            physics_validation=physics_validation
        )
```

---

## 🔧 Semantic YAML 컨텍스트 생성

### 2. Context Builder 구현

```python
# modules/intelligence/context_builder.py
import yaml
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class RackRisk:
    rack_id: str
    risk_type: str  # "THERMAL" | "SPC" | "ISC" | "INTEGRITY"
    dtdt: float = None
    z_score: float = None
    isc_prob: float = None
    physics_valid: bool = True


def build_semantic_context(
    total_racks: int,
    success_rate: float,
    top_risks: List[RackRisk],
    physics_issues: List[str]
) -> str:
    """SLM이 이해하기 쉬운 YAML 구조 생성

    Args:
        total_racks: 전체 Rack 수
        success_rate: 분석 성공률 (0.0~1.0)
        top_risks: 상위 5개 위험 Rack 리스트
        physics_issues: 물리 검증 실패 항목

    Returns:
        YAML 형식 문자열
    """

    context = {
        "시스템_상태": {
            "총_Rack_수": total_racks,
            "분석_성공_Rack": int(total_racks * success_rate),
            "분석_실패_Rack": int(total_racks * (1 - success_rate)),
            "데이터_신뢰도": "높음" if success_rate > 0.8 else "낮음"
        },

        "위험_감지_결과": {
            "긴급_대응_필요_CRITICAL": [],
            "주의_관찰_필요_WARNING": [],
        },

        "상위_5개_위험_Rack": []
    }

    # Top 5 위험 Rack 추가
    for rack in top_risks[:5]:
        rack_info = {
            "Rack_ID": rack.rack_id,
            "위험_유형": _translate_risk_type(rack.risk_type),
            "수치": {}
        }

        # 수치 데이터 추가 (존재하는 것만)
        if rack.dtdt is not None:
            rack_info["수치"]["열_변화율_dTdt"] = f"{rack.dtdt:.2f}°C/min"
            rack_info["수치"]["임계값_초과"] = rack.dtdt > 2.0

        if rack.z_score is not None:
            rack_info["수치"]["Z_Score"] = f"{rack.z_score:.2f}σ"
            rack_info["수치"]["정상범위_이탈"] = abs(rack.z_score) > 3.0

        if rack.isc_prob is not None:
            rack_info["수치"]["ISC_확률"] = f"{rack.isc_prob:.1%}"

        # 물리 검증 결과
        rack_info["물리_검증"] = "통과" if rack.physics_valid else "⚠️ 센서 오류 의심"

        context["상위_5개_위험_Rack"].append(rack_info)

        # 위험도별 분류
        if rack.dtdt and rack.dtdt > 5.0:  # 매우 위험
            context["위험_감지_결과"]["긴급_대응_필요_CRITICAL"].append(rack.rack_id)
        elif rack.dtdt and rack.dtdt > 2.0:
            context["위험_감지_결과"]["주의_관찰_필요_WARNING"].append(rack.rack_id)

    # 물리 검증 이슈
    if physics_issues:
        context["물리_검증_경고"] = physics_issues

    return yaml.dump(context, allow_unicode=True, sort_keys=False)


def _translate_risk_type(risk_type: str) -> str:
    """영어 위험 유형을 한국어로 번역"""
    translations = {
        "THERMAL": "열적 안전성 (Thermal Runaway 위험)",
        "SPC": "셀 밸런싱 이상 (Statistical Process Control)",
        "ISC": "내부 단락 의심 (Internal Short Circuit)",
        "INTEGRITY": "데이터 무결성 문제"
    }
    return translations.get(risk_type, risk_type)
```

---

## 🛡️ Guardrail + Fallback 통합

### 3. 검증 및 Fallback 처리

```python
# modules/intelligence/guardrails.py
import asyncio
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class GuardrailValidator:
    """SLM 출력 검증 및 Fallback 처리"""

    def __init__(self, timeout: int = 60):
        """
        Args:
            timeout: SLM 응답 대기 시간 (초)
        """
        self.timeout = timeout

    async def validate_and_execute(
        self,
        analyzer: 'BatteryAnalyzer',
        context: str,
        physics_validation: str
    ) -> str:
        """분석 실행 + 검증 + Fallback

        Args:
            analyzer: DSPy BatteryAnalyzer 인스턴스
            context: YAML 컨텍스트
            physics_validation: 물리 검증 결과

        Returns:
            Markdown 리포트 (AI 생성 또는 Fallback)
        """
        try:
            # 1. Timeout 적용
            result = await asyncio.wait_for(
                self._run_analysis(analyzer, context, physics_validation),
                timeout=self.timeout
            )

            # 2. 출력 형식 검증
            if not self._is_valid_output(result):
                raise ValueError("Invalid SLM output format")

            # 3. 물리 법칙 재검증 (SLM이 비현실적 값 생성 방지)
            if not self._physics_sanity_check(result):
                logger.warning("Physics sanity check failed - using fallback")
                return self._generate_fallback_report(context)

            # 4. 성공
            return self._format_markdown_report(result)

        except asyncio.TimeoutError:
            logger.error(f"SLM timeout ({self.timeout}s) - using fallback")
            return self._generate_fallback_report(context)

        except Exception as e:
            logger.error(f"SLM error: {e} - using fallback")
            return self._generate_fallback_report(context)

    async def _run_analysis(self, analyzer, context, physics_validation):
        """비동기 분석 실행"""
        # DSPy는 동기 함수이므로 executor 사용
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            analyzer.forward,
            context,
            physics_validation
        )

    def _is_valid_output(self, result) -> bool:
        """필수 섹션 포함 여부 확인"""
        required_sections = ["위험도 평가", "기술 분석", "조치 권고"]

        # DSPy Prediction 객체에서 텍스트 추출
        full_text = (
            result.risk_assessment +
            result.technical_analysis +
            result.recommendations
        )

        return all(section in full_text for section in required_sections)

    def _physics_sanity_check(self, result) -> bool:
        """SLM이 물리적으로 불가능한 내용 생성했는지 확인

        예시:
        - dT/dt > 100°C/min (비현실적)
        - 전압 > 5V (LFP 배터리 범위 초과)
        """
        full_text = (
            result.risk_assessment +
            result.technical_analysis +
            result.recommendations
        )

        # 비현실적 온도 변화율 체크
        dtdt_matches = re.findall(r'(\d+(?:\.\d+)?)\s*°C/min', full_text)
        for match in dtdt_matches:
            if float(match) > 100:  # 100°C/min 초과는 비현실적
                logger.warning(f"Unrealistic dT/dt detected: {match}°C/min")
                return False

        # 비현실적 전압 체크
        voltage_matches = re.findall(r'(\d+(?:\.\d+)?)\s*V', full_text)
        for match in voltage_matches:
            if float(match) > 5.0:  # LFP 셀 전압 범위 초과
                logger.warning(f"Unrealistic voltage detected: {match}V")
                return False

        return True

    def _format_markdown_report(self, result) -> str:
        """DSPy 결과를 Markdown으로 포맷팅"""
        return f"""# 배터리 안전 분석 리포트

{result.risk_assessment}

{result.technical_analysis}

{result.recommendations}

---
*Generated by GEM AI Analysis Engine*
"""

    def _generate_fallback_report(self, context: str) -> str:
        """AI 없이 수치 기반 리포트 생성"""
        return f"""# 배터리 안전 분석 리포트 (자동 생성)

## ⚠️ AI 모델 응답 지연

AI 모델이 응답하지 않아 수치 기반 요약본을 제공합니다.

## 분석 데이터

```yaml
{context}
```

## 권고 사항

1. **즉시 조치**: CRITICAL 위험 Rack 현장 점검
2. **모니터링 강화**: WARNING 위험 Rack 주의 관찰
3. **AI 재분석**: 상세 해석이 필요하면 재실행 권장

---
*Fallback Report - AI 응답 없음*
"""
```

---

## 🚀 프롬프트 자동 최적화 (선택 사항)

### 4. DSPy Optimizer 활용

```python
# scripts/optimize_prompts.py
"""
DSPy 프롬프트 자동 최적화 스크립트

실행:
    python scripts/optimize_prompts.py
"""

import dspy
from dspy.teleprompt import BootstrapFewShot
from modules.intelligence.dspy_prompts import BatteryAnalyzer
from modules.intelligence.context_builder import build_semantic_context, RackRisk


def create_training_dataset():
    """학습 데이터셋 생성 (20개 샘플)"""

    trainset = []

    # 예시 1: CRITICAL 열폭주 위험
    example1 = dspy.Example(
        summary_data=build_semantic_context(
            total_racks=160,
            success_rate=0.95,
            top_risks=[
                RackRisk("RACK_042", "THERMAL", dtdt=7.5, z_score=4.2),
            ],
            physics_issues=[]
        ),
        physics_validation="모든 센서 정상",
        expected_risk="CRITICAL"  # 정답 레이블
    ).with_inputs("summary_data", "physics_validation")

    trainset.append(example1)

    # 예시 2: WARNING 셀 밸런싱 이상
    example2 = dspy.Example(
        summary_data=build_semantic_context(
            total_racks=160,
            success_rate=0.88,
            top_risks=[
                RackRisk("RACK_105", "SPC", z_score=3.5),
            ],
            physics_issues=[]
        ),
        physics_validation="모든 센서 정상",
        expected_risk="WARNING"
    ).with_inputs("summary_data", "physics_validation")

    trainset.append(example2)

    # 추가 18개 샘플 생성...
    # (실제 운영 데이터 기반으로 작성)

    return trainset


def risk_accuracy(example, prediction, trace=None):
    """평가 메트릭: 위험도 정확도"""
    # 예상 위험도가 AI 출력에 포함되어 있는지 확인
    return example.expected_risk in prediction.risk_assessment


def optimize_battery_analyzer():
    """배터리 분석기 프롬프트 최적화"""

    # 1. SLM 설정 (Qwen2.5 32B)
    lm = dspy.OpenAI(
        model="qwen2.5:32b-instruct",
        api_base="http://localhost:11434/v1",  # Ollama 개발 환경
        api_key="ollama"  # Dummy key
    )
    dspy.settings.configure(lm=lm)

    # 2. 학습 데이터 로드
    trainset = create_training_dataset()

    # 3. 최적화 실행
    print("🔧 프롬프트 최적화 시작...")
    optimizer = BootstrapFewShot(
        metric=risk_accuracy,
        max_bootstrapped_demos=3  # Few-shot 예시 3개
    )

    optimized_analyzer = optimizer.compile(
        BatteryAnalyzer(),
        trainset=trainset
    )

    # 4. 최적화된 모델 저장
    optimized_analyzer.save("models/optimized_battery_analyzer.json")
    print("✅ 최적화 완료! 저장 위치: models/optimized_battery_analyzer.json")

    return optimized_analyzer


if __name__ == "__main__":
    optimize_battery_analyzer()
```

---

## 🔌 메인 파이프라인 통합

### 5. Phase 3에서 사용

```python
# modules/intelligence/llm_client.py
import dspy
from modules.intelligence.dspy_prompts import BatteryAnalyzer
from modules.intelligence.guardrails import GuardrailValidator
from modules.intelligence.context_builder import build_semantic_context
import logging

logger = logging.getLogger(__name__)


class SLMClient:
    """SLM 클라이언트 (환경변수 기반 자동 설정)"""

    def __init__(self, use_optimized: bool = False):
        """
        Args:
            use_optimized: 최적화된 프롬프트 사용 여부

        환경변수에서 자동으로 모델/엔진 선택:
        - .env의 SLM_MODEL_ACTIVE 사용
        - USE_OLLAMA / USE_VLLM로 엔진 자동 선택

        자세한 설정 방법은 12_모델-설정-가이드.md 참조
        """
        # 환경변수에서 설정 로드 (config/settings.py 필요)
        from config.settings import get_model_config

        config = get_model_config()
        logger.info(f"🤖 SLM 초기화: {config['engine']} - {config['model_name']}")

        # DSPy 설정
        lm = dspy.OpenAI(
            model=config['model_name'],
            api_base=config['api_base'],
            api_key="ollama" if config['engine'] == "Ollama" else "EMPTY"
        )
        dspy.settings.configure(lm=lm)

        # Analyzer 로드
        if use_optimized:
            self.analyzer = BatteryAnalyzer()
            try:
                self.analyzer.load("models/optimized_battery_analyzer.json")
                logger.info("✅ 최적화된 프롬프트 로드")
            except FileNotFoundError:
                logger.warning("⚠️ 최적화 파일 없음, 기본 프롬프트 사용")
        else:
            self.analyzer = BatteryAnalyzer()

        # Guardrail 설정
        self.validator = GuardrailValidator(timeout=60)

    async def analyze_battery_risks(
        self,
        summary_data: str,
        physics_validation: str
    ) -> str:
        """배터리 위험 분석

        Args:
            summary_data: YAML 요약 데이터
            physics_validation: 물리 검증 결과

        Returns:
            Markdown 리포트
        """
        return await self.validator.validate_and_execute(
            self.analyzer,
            summary_data,
            physics_validation
        )


# === 사용 예시 ===
async def example_usage():
    # 1. SLM 클라이언트 생성 (환경변수 자동 적용)
    # .env 파일에서 SLM_MODEL_ACTIVE, USE_OLLAMA/USE_VLLM 읽음
    client = SLMClient(use_optimized=True)

    # 2. 컨텍스트 생성
    from modules.intelligence.context_builder import RackRisk

    context = build_semantic_context(
        total_racks=160,
        success_rate=0.92,
        top_risks=[
            RackRisk("RACK_042", "THERMAL", dtdt=5.2, z_score=3.8),
            RackRisk("RACK_105", "SPC", z_score=4.1),
        ],
        physics_issues=["RACK_007: 전압 센서 이상"]
    )

    # 3. 분석 실행
    report = await client.analyze_battery_risks(
        summary_data=context,
        physics_validation="2개 센서 이상 감지"
    )

    print(report)
```

---

## 📊 프롬프트 성능 비교

| 접근 방식 | 프롬프트 작성 | 타입 안전 | 오버헤드 | 최적화 |
|----------|-------------|----------|---------|--------|
| **수동 프롬프트** | 개발자가 직접 작성 | ❌ | 0ms | ❌ |
| **LangChain** | 템플릿 기반 | ⚠️ 부분적 | 8.02ms | ❌ |
| **DSPy (비최적화)** | Signature 정의 | ✅ | 3.53ms | ❌ |
| **DSPy (최적화)** | 자동 Few-shot | ✅ | 3.53ms | ✅ |

---

## ✅ 체크리스트

### 개발 단계
- [ ] DSPy 설치 (`pip install dspy-ai`)
- [ ] BatteryAnalysisSignature 정의
- [ ] context_builder.py 구현
- [ ] guardrails.py 구현
- [ ] Ollama 개발 환경 테스트

### 운영 배포 전
- [ ] 학습 데이터셋 20개 작성
- [ ] 프롬프트 최적화 실행
- [ ] vLLM 프로덕션 서버 구축
- [ ] Fallback 시나리오 테스트
- [ ] 응답 시간 60초 SLA 확인

---

**이전 문서:** [08_FAQ-및-트러블슈팅.md](./08_FAQ-및-트러블슈팅.md)
**다음 문서:** [10_성능-최적화-가이드.md](./10_성능-최적화-가이드.md)
