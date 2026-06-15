# Phase 3 인사이트 개선 계획

## 날짜: 2026-03-10

---

## 1. 현재 문제점 분석 (15:00 생성 리포트 기준)

### 🔴 심각한 문제들

#### 1.1 CH_01만 분석되고 나머지 채널 누락
**현상:**
```markdown
# Z-Score 균형성 분석

## CH_01 채널
(내용...)

## 끝
```

- CH_02, CH_03, CH_04, CH_05, CH_06 **완전 누락**
- 324개 랙 중 54개(CH_01)만 분석
- 5/6 = **83%의 데이터가 버려짐**

#### 1.2 고정 텍스트 / 템플릿 응답
**ISC 분석 예시:**
```markdown
### 분석 결과: Critical X건 (샘플링: Y건), Warning Z건 (샘플링: W건)

**중요:** summary.warning_sampled가 true면 반드시...
```

- **실제 값 대신 변수명(X, Y, Z)이 그대로 출력됨**
- 프롬프트의 예시를 그대로 복사
- LLM이 데이터를 전혀 분석하지 않음

#### 1.3 초딩 수준의 분석
**Thermal 분석 예시:**
```markdown
**전문가 분석:**
이상은 배터리 팩 내부 열역학적 불균형을 나타내며, 발열량(Q=I²R)과 냉각 능력(Q=h·A·ΔT)의 균형이 깨진 증거입니다.
```

- **일반론적인 수식 나열**
- 실제 측정값과 연결 안 됨
- "~의 가능성을 제기합니다" 같은 애매한 표현

#### 1.4 의미 없는 권장 조치
**Comprehensive 요약:**
```markdown
1. [즉시] RACK_03을 격리하고, 해당 배터리를 즉시 폐기.
2. [30분] RACK_ID 를 격리하고, 추가적인 조치를 취함.
```

- "RACK_ID"라는 변수명이 그대로 출력
- 구체적인 랙 번호 없음
- 실행 불가능한 지침

---

## 2. 근본 원인 분석

### 2.1 데이터 구조 문제

**Phase2 출력:**
```json
{
  "CH_01": {...},
  "CH_02": {...},
  "CH_03": {...},
  ...
}
```

**Phase3 입력 (추정):**
- 채널별로 별도 API 호출하지 않음
- 첫 번째 채널(CH_01)만 처리하고 종료
- 반복문 로직 오류

### 2.2 프롬프트 설계 문제

#### 문제 1: 예시와 실제 출력이 혼재
```markdown
### 분석 결과: Critical X건...
```
→ LLM이 이걸 **예시가 아니라 실제 출력 형식**으로 인식

#### 문제 2: 금지 사항이 제대로 작동 안 함
```markdown
## 절대 금지 사항
1. ❌ "이 JSON 데이터는..." 금지
```
→ 실제 출력에 여전히 나타남

#### 문제 3: 데이터 사용 지침 불명확
```markdown
**사용 가능:** Z-Score, v_avg(전압)...
**사용 금지:** 셀 개별 용량...
```
→ LLM이 실제 데이터를 무시하고 일반론만 작성

### 2.3 데이터 품질 문제

**Phase2에서 Phase3로 전달되는 데이터:**
- Rack별 상세 정보가 있는가?
- 시간대별 통계가 정확한가?
- 샘플링 정보가 명확한가?

→ 확인 필요

---

## 3. 업계 Best Practice (검색 결과 기반)

### 3.1 최신 AI 기술 동향 (2024-2025)

#### BatteryAgent (Dec 2025)
- **Physics-Informed + LLM Reasoning** 결합
- AUROC **0.986** 달성
- Binary detection → **Multi-type interpretable diagnosis**

**핵심 개념:**
```
물리 지식(센서 데이터, 임계값) + LLM 추론(패턴 인식, 설명 생성)
```

#### TimeSeries2Report (Jan 2026)
- 시계열 데이터 → **구조화된 의미론적 리포트** 변환
- **Expert knowledge injection** via prompting or RAG
- Specialized task (fault diagnosis)에 최적화

**핵심 개념:**
```
Raw Data → Semantic Report → LLM Reasoning → Actionable Insights
```

#### GPT4Battery (Jan 2024)
- **Zero-shot cross-battery SOH estimation**
- Generalization capability 활용
- State-of-the-art accuracy

### 3.2 ESS 진단 리포트 표준 구조

**NREL, UL 9540A, IEC 62619 기준:**

1. **System Description**
   - 배터리 타입, 용량, 채널 구성
   - 테스트 기간, 환경 조건

2. **Performance Metrics (KPI)**
   - Availability (% up-time)
   - Performance Ratio (PR)
   - Efficiency
   - Demonstrated Capacity

3. **Health Assessment**
   - State of Health (SOH)
   - Capacity loss
   - Resistance growth

4. **Fault Detection Results**
   - 이상 유형 분류 (Thermal, Voltage, ISC)
   - 심각도 레벨 (Critical, Warning, Normal)
   - 위치 식별 (Channel, Bank, Rack)
   - 시간 정보 (First detection, Last detection, Frequency)

5. **Root Cause Analysis**
   - 물리적 원인 (Physics-based)
   - 통계적 근거 (Data-driven)
   - 전문가 판단 (Expert interpretation)

6. **Recommendations**
   - Immediate actions (0-1시간)
   - Short-term actions (1-24시간)
   - Long-term actions (1주-1개월)
   - 우선순위 및 근거

7. **Supporting Data**
   - 그래프 (시계열, 히스토그램, 분포)
   - 표 (상위 10개 이상 랙)
   - 참조 링크 (O&M 자료)

---

## 4. 개선 전략

### 4.1 아키텍처 개선

#### Before (추정):
```
Phase2 Output → LLM (single call) → insights_xxx.md
```

#### After:
```
Phase2 Output
  → Data Preparation (채널별 분리, 통계 계산)
  → Per-Channel Analysis (LLM × 6 calls)
  → Cross-Channel Synthesis (LLM × 1 call)
  → Final Report Generation
```

### 4.2 데이터 파이프라인 개선

#### Step 1: Structured Data Extraction
**Phase2 JSON → Semantic Summary**

```python
# 각 채널별로
channel_summary = {
    "channel_id": "CH_01",
    "total_racks": 54,
    "analysis_period": "2026-03-09 00:00 ~ 23:59",
    "thermal": {
        "critical_racks": ["RACK_01", "RACK_03"],
        "warning_racks": ["RACK_02"],
        "max_dtdt": -1.5,  # 실제 값
        "threshold_critical": -1.2,
        "exceedance_ratio": 1.25,  # -1.5 / -1.2
        "time_pattern": "12:00~13:00 집중 (14%)",
        "temp_range": {"min": 21.5, "max": 26.0, "avg": 23.9}
    },
    "spc": {
        "critical_count": 100,
        "warning_count": 20,
        "max_z_score": 5.1,
        "affected_racks": {
            "RACK_06": {"count": 56, "max_z": 5.1, "first_time": "00:47"},
            ...
        }
    },
    "isc": {...},
    "integrity": {...}
}
```

#### Step 2: Context-Rich Prompting
**Before:**
```
당신은 배터리 전문가입니다.
{JSON data}
분석하세요.
```

**After:**
```
# 역할
당신은 20년 경력의 배터리 안전 진단 전문가입니다.

# 상황
- 분석 대상: NMC LG 배터리, CH_01 채널, 54개 Rack
- 기간: 2026-03-09 (24시간 모니터링)
- 목적: Critical fault 조기 발견 및 열폭주 예방

# 제공 데이터
## Thermal Safety
- Critical: 0건
- Warning: 20건 (샘플링: 100건 중 20건 제공)
- 최대 dT/dt: -1.5°C/min (임계값 -1.2°C/min 대비 125%)
- 온도 범위: 21.5~26.0°C (평균 23.9°C)
- 주요 시간대: 12:00~13:00 (14%)
- 이상 랙:
  1. RACK_01: dT/dt -1.5°C/min, 7회, 최초 00:05
  2. RACK_02: dT/dt 1.5°C/min, 8회, 최초 11:26
  3. RACK_03: dT/dt 1.5°C/min, 7회, 최초 11:51

# 전문가 분석 요구사항
1. **물리적 근거**: 실제 측정값(-1.5°C/min, 25% 초과)을 기반으로 발열 메커니즘 설명
2. **시스템 영향**: 54개 Rack 중 3개(5.5%) 이상 → 국소적 문제 vs 시스템 전체 문제 판단
3. **시간 패턴**: 12시~13시 집중 → 피크 부하 시간대 추정, 충전/방전 프로파일 고려
4. **우선순위**: RACK_01이 가장 빠른 변화율 → 1순위 점검 대상

# 출력 형식
## Thermal Safety Analysis

### CH_01 Channel Summary
- **Status**: Warning (3 racks affected, 5.5% of total)
- **Severity**: dT/dt up to -1.5°C/min (125% of threshold)
- **Time Pattern**: Concentrated in 12:00-13:00 (peak load period)

### Root Cause Analysis

**Measurement-Based Evidence:**
The detected cooling rate of -1.5°C/min exceeds the critical threshold (-1.2°C/min) by 25%, indicating insufficient heat dissipation relative to Joule heating (Q = I²R). At an average temperature of 23.9°C and assuming a current of X A (from load profile), the estimated heat generation rate is Y W.

**Thermal Modeling:**
Using the lumped capacitance method (Q = m·Cp·dT/dt), the observed cooling rate suggests...

[계속...]

# 금지 사항
- ❌ "데이터를 분석하면..." 같은 메타 설명
- ❌ 측정되지 않은 값을 단정 (예: "전류는 50A입니다" → 측정 안 됨)
- ❌ 일반론 나열 (예: "배터리는 열에 민감합니다" → 당연한 얘기)
```

### 4.3 프롬프트 엔지니어링 Best Practices

#### 1. Few-Shot Learning
**Good Example:**
```markdown
## CH_02 Channel

### Analysis Result: Critical 15 racks (28% of total)

**Detection Data:**
- Total: 54 racks, Normal: 39 racks
- Max Z-Score: 7.2σ (RACK_12, 68 violations)
- Voltage range: 3.45~3.62V (avg 3.54V)
- Critical threshold: 3.0σ

**Expert Analysis:**

**Statistical Interpretation:**
Z-Score of 7.2σ represents a probability of 99.9999999% abnormality in normal distribution, indicating RACK_12's voltage is statistically extreme. This 18.7% voltage deviation from channel average suggests significant cell capacity imbalance or internal resistance increase.

**Physical Mechanism:**
The voltage imbalance arises from differential aging across cells. High Z-Score racks likely contain cells with higher internal resistance (ΔR ≈ +X%), leading to voltage sag under load. Using Ohm's law (V = I·R), a 10% resistance increase causes Y mV voltage drop at Z A discharge current.

**System Impact:**
With 15/54 racks (28%) showing critical imbalance, this is a **system-level degradation**, not isolated failures. BMS balancing appears insufficient to compensate for this magnitude of cell variance. Long-term effects include:
- Accelerated capacity fade (estimated -X%/year)
- Reduced usable energy (Y% loss in SOC window)
- Risk of over-discharge in weak cells → Cu dissolution

**Recommended Actions:**
1. [Immediate] Reduce discharge rate by 20% to minimize voltage sag
2. [4 hours] Activate extended balancing cycle (8h continuous)
3. [24 hours] Capacity test on top 5 critical racks to quantify degradation
4. [1 week] Consider cell replacement if capacity < 80% of nominal

---
```

**Bad Example:** (현재 출력)
```markdown
## CH_01 채널

이 JSON 데이터는 전압 측정치와 SPC 관련 정보를 포함하고 있습니다...
```

#### 2. Chain-of-Thought Prompting
```
# 분석 절차 (단계별로 명시)
Step 1: 데이터 검증
- Critical count = X, Warning count = Y
- 샘플링 여부 확인: summary.warning_sampled = true/false
- 전체 대비 비율 계산: X/total_racks = Z%

Step 2: 통계 분석
- 최대 Z-Score = A (어떤 랙?)
- 임계값 대비 배율 = A / threshold = B배
- 시간 분포: {time_statistics}에서 패턴 추출

Step 3: 물리적 해석
- Z-Score A는 정규분포에서 P(Z>A) = X% 의미
- 전압 편차 = (v_avg - channel_mean) = Y mV
- 내부저항 추정: ΔR ≈ Y mV / current

Step 4: 권장 조치 도출
- 심각도에 따라 조치 시간 결정
- 구체적인 랙 ID와 값 명시
- 측정 가능한 개선 목표 제시
```

#### 3. Constraint Specification
```
# 출력 제약 조건
- 길이: 500-800 단어
- 문장: 서술형, 능동태
- 숫자: 소수점 1자리 (예: 3.5°C, 4.1σ)
- 시간: HH:MM 형식 (예: 12:30)
- Rack ID: 정확한 형식 (예: CH_01.BANK_02.RACK_11)
- 확신도: 측정값 기반 = "입니다", 추정 = "~로 판단됩니다", 불확실 = "~의 가능성"
```

### 4.4 코드 구조 개선 (pseudo-code)

```python
def generate_insights_v3(phase2_results, config):
    """Phase 3: AI 인사이트 생성 (v3 개선 버전)"""

    # Step 1: 채널별 데이터 분리 및 전처리
    channels_data = extract_channels(phase2_results)
    # {
    #   "CH_01": {thermal: {...}, spc: {...}, isc: {...}, integrity: {...}},
    #   "CH_02": {...},
    #   ...
    # }

    # Step 2: 각 채널별로 분석 (병렬 처리 가능)
    channel_insights = {}
    for channel_id, data in channels_data.items():
        # 2.1 구조화된 요약 생성
        summary = create_semantic_summary(data, channel_id)

        # 2.2 도메인별 인사이트 생성 (LLM 호출)
        insights = {}
        for domain in ["thermal", "spc", "isc", "integrity"]:
            prompt = build_expert_prompt(
                domain=domain,
                summary=summary[domain],
                channel_id=channel_id,
                examples=load_few_shot_examples(domain)
            )
            insights[domain] = call_llm(prompt, temperature=0.3)

        channel_insights[channel_id] = insights

    # Step 3: 전체 시스템 종합 분석 (Cross-channel)
    comprehensive = generate_comprehensive_summary(
        channel_insights=channel_insights,
        rankings=phase2_results["rankings"]  # 전체 랭킹
    )

    # Step 4: 마크다운 파일 저장
    save_insights_per_domain(channel_insights, comprehensive)

    return {
        "status": "success",
        "channels_analyzed": len(channels_data),
        "insights_generated": sum(len(v) for v in channel_insights.values())
    }


def create_semantic_summary(channel_data, channel_id):
    """Phase2 JSON → Structured Semantic Summary"""
    return {
        "thermal": {
            "status": "warning" if channel_data["thermal"]["warning_count"] > 0 else "normal",
            "critical_racks": extract_critical_racks(channel_data["thermal"]),
            "max_value": find_max_violation(channel_data["thermal"]["detections"]),
            "threshold_exceedance": calculate_exceedance_ratio(...),
            "time_pattern": analyze_time_distribution(channel_data["thermal"]["time_statistics"]),
            "temperature_stats": {...}
        },
        "spc": {...},
        "isc": {...},
        "integrity": {...}
    }


def build_expert_prompt(domain, summary, channel_id, examples):
    """Context-Rich Prompt 생성"""
    template = load_template(f"prompts/{domain}_expert_v3.txt")

    # 실제 데이터로 변수 치환
    context = {
        "channel_id": channel_id,
        "status": summary["status"],
        "critical_count": len(summary["critical_racks"]),
        "max_value": summary["max_value"],
        "threshold": summary["threshold"],
        "exceedance_pct": summary["threshold_exceedance"] * 100,
        "time_pattern": summary["time_pattern"],
        "critical_racks_detail": format_rack_list(summary["critical_racks"]),
        # ... 모든 필요한 값
    }

    prompt = template.format(**context)

    # Few-shot examples 추가
    if examples:
        prompt += "\n\n# Examples\n" + "\n\n".join(examples)

    return prompt
```

---

## 5. 단계별 실행 계획

### Phase 1: 긴급 수정 (1-2시간)
**목표:** CH_01만 분석되는 버그 수정

1. ✅ Phase3 스크립트에서 채널 반복 로직 확인
2. ✅ 6개 채널 모두 처리되도록 수정
3. ✅ 테스트 (2026-03-09 데이터로 검증)

### Phase 2: 프롬프트 개선 (2-3시간)
**목표:** 고정 텍스트 제거, 실제 값 출력

1. ✅ 프롬프트에서 변수 예시 (X, Y, Z) 제거
2. ✅ Few-shot examples 추가
3. ✅ Constraint specification 명확화
4. ✅ 테스트

### Phase 3: 데이터 파이프라인 개선 (4-6시간)
**목표:** Semantic summary 생성

1. ✅ `create_semantic_summary()` 함수 구현
2. ✅ Phase2 JSON → Structured data 변환
3. ✅ 통계 계산 (exceedance ratio, time pattern 등)
4. ✅ 테스트

### Phase 4: 전문가 수준 분석 (6-8시간)
**목표:** 물리 기반 + 데이터 기반 융합 분석

1. ✅ Physics-informed prompting 적용
2. ✅ Chain-of-Thought 구조화
3. ✅ 측정값 기반 계산 로직 추가
4. ✅ 전체 통합 테스트

### Phase 5: 검증 및 배포 (2-3시간)
**목표:** 실제 데이터로 품질 확인

1. ✅ 2026-03-09 배치 재실행
2. ✅ 생성된 인사이트 리뷰
3. ✅ 배터리 전문가 검토 요청
4. ✅ 서버 배포

---

## 6. 성공 기준

### 정량적 지표
- ✅ 6개 채널 모두 분석 (100% coverage)
- ✅ 고정 텍스트 0개 (변수명 X, Y, Z 등 제거)
- ✅ 실제 측정값 인용 100% (예: "dT/dt -1.5°C/min")
- ✅ 구체적인 Rack ID 명시 100%

### 정성적 지표
- ✅ 물리적 메커니즘 설명 (Joule heating, thermal runaway 등)
- ✅ 통계적 근거 명시 (Z-Score 확률, exceedance ratio 등)
- ✅ 실행 가능한 권장 조치 (시간, 대상, 방법 구체화)
- ✅ 전문가 검토 통과 ("배터리 전문가답다")

---

## 7. 참고 자료

### 논문
- BatteryAgent (arXiv:2512.24686)
- TimeSeries2Report (arXiv:2512.16453)
- GPT4Battery (arXiv:2402.00068)

### 표준
- UL 9540A (BESS Fire Testing)
- IEC 62619 (Stationary Li-ion Batteries)
- NREL Performance Testing Protocol

### 업계 Best Practice
- DEKRA BESS Testing Guidelines
- DOE Battery Evaluation Method (2023)

---

## 작성자
- 작성일: 2026-03-10
- 작성자: Claude (Anthropic)
- 검토자: 사용자 (RFS 프로젝트)
