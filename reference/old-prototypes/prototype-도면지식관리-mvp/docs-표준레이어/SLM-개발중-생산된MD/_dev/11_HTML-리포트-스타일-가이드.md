# HTML 리포트 스타일 가이드

**작성일:** 2025-12-13
**최종 업데이트:** 2025-12-23
**버전:** 1.1.0
**중요도:** ⚠️ **절대 변경 금지 (IMMUTABLE)**

---

## ⚠️ 중요 공지

**이 스타일 가이드는 모든 GEM 리포트에 적용되는 절대 표준입니다.**

- ✅ 누가 실행하든 동일한 스타일
- ✅ 색상, 폰트, 여백 모두 고정
- ✅ Chart.js 설정 고정
- ✅ 레이아웃 구조 고정

**스타일을 변경하려면:**
1. `config/global/styles/report_style.css` 수정
2. `config/global/styles/chart_config.yaml` 수정
3. HTML 템플릿 재생성
4. 이 문서 업데이트

---

## 📋 목차

1. [문서 개요](#문서-개요)
2. [리포트 구조](#리포트-구조)
3. [AI 인사이트 텍스트 작성 규칙](#ai-인사이트-텍스트-작성-규칙)
4. [색상 팔레트](#색상-팔레트)
5. [타이포그래피](#타이포그래피)
6. [여백](#여백)
7. [Chart 설정](#chart-설정)
8. [데이터 매핑 규칙](#데이터-매핑-규칙)
9. [HTML 구조](#html-구조)
10. [품질 체크리스트](#품질-체크리스트)

---

## 📁 문서 개요

본 문서는 GEM (Generative Engineering Module) 배터리 안전 분석 시스템에서 생성되는 HTML 리포트의 스타일 가이드입니다.

**목적**: Phase 3에서 생성되는 HTML 리포트의 일관된 품질과 전문성을 보장하기 위한 표준 가이드라인 제공

**적용 범위**:
- AI 인사이트 텍스트 생성 (Ollama qwen2.5:32b)
- HTML 템플릿 구조 (Jinja2)
- CSS 스타일링 (report_style.css)
- Chart.js 시각화

---

## 📁 스타일 가이드 파일 위치

### 1. CSS 스타일 (IMMUTABLE)
**파일:** `GEM/config/global/styles/report_style.css`

**내용:**
- CSS Variables (색상 팔레트)
- 레이아웃 (Container, Grid)
- 타이포그래피 (폰트, 크기)
- 컴포넌트 스타일 (Cards, Charts, Boxes)
- 반응형 (모바일, 인쇄)

### 2. Chart.js 설정 (IMMUTABLE)
**파일:** `GEM/config/global/styles/chart_config.yaml`

**내용:**
- 4개 차트별 설정
- 색상 팔레트
- 축 설정
- 범례, 툴팁 설정

### 3. HTML 템플릿
**파일:** `GEM/config/global/templates/battery_report.html`

**주의:** CSS는 인라인으로 임베드되지만, 원본은 `report_style.css`입니다.

---

## 1. 리포트 구조

### 1.1 전체 구성

```
[Header]
- 제목: "GEM 배터리 안전 분석 리포트"
- 분석 ID: {RUN_ID}
- 생성 시간: {timestamp}
- 배터리 프로파일: {battery_profile}

[Summary Dashboard]
- Critical/Warning/Normal 건수 표시
- 색상 구분: Red(Critical) / Orange(Warning) / Green(Normal)

[4대 핵심 분석 (탭 메뉴)]
1. 열적 안전성 분석 (Thermal Safety)
2. 셀 밸런싱 분석 (SPC Balance)
3. 센서 무결성 분석 (Data Integrity)
4. 시스템 상관성 분석 (System Correlation)

[종합 인사이트]
- 전체 시스템 요약
- 위험도 우선순위
- 종합 권장 조치사항
- 종합 평가

[Footer]
- 생성 시스템: GEM Framework
- Powered by Ollama
```

### 1.2 섹션별 레이아웃

**각 핵심 분석 섹션 구조:**

```
1. 분석 개요
   - 분석 기간
   - 배터리 프로파일
   - 검증 기준
   - 임계값

2. 검증 결과
   2.1 이상 감지 현황 (요약)
   2.2 Critical 등급 위험
   2.3 Warning 등급 주의

3. 권장 조치사항
   3.1 즉시 조치 (24시간 이내)
   3.2 단기 조치 (1주일 이내)
   3.3 장기 개선 계획
```

---

## 2. AI 인사이트 텍스트 작성 규칙

### 2.1 **절대 금지 사항**

❌ **Markdown 스타일 사용 금지**
```
# 제목 (X)
## 소제목 (X)
**굵은 글씨** (X)
- 리스트 (X)
```

❌ **이모지 사용 금지**
```
🔥 열적 위험 (X)
⚖️ 밸런싱 (X)
🔍 센서 (X)
✅ 정상 (X)
```

❌ **AI스러운 표현 금지**
```
"#### 1순위: RACK_05 (열적 위험 🔥)" (X)
"**CRITICAL**: RACK_05" (X)
```

### 2.2 **권장 작성 방식**

✅ **전문 리포트 스타일**

```
1. 분석 개요
분석 기간: 2025-12-13 10:00:00 ~ 2025-12-13 10:30:00
배터리 프로파일: NMC_LG
검증 기준: dT/dt (시간당 온도 변화율)
분석 임계값: Critical > 2.0°C/min, Warning > 1.0°C/min

2. 검증 결과

2.1 위험 감지 현황
총 3건의 열적 이상 징후가 감지되었습니다.
영향받은 설비: RACK_05, RACK_12, RACK_22

2.2 Critical 등급 위험
설비명: RACK_05
발생 시각: 2025-12-13 10:15:00
측정 온도: 50.1°C
온도 변화율: 4.8°C/min (임계값 2.0°C/min 초과)
위험도 판정: 열폭주(Thermal Runaway) 전조 증상
근거: 온도 상승 속도가 임계값의 2.4배에 달하며, 이는 배터리 내부 이상 발열을 의미합니다.
      방치 시 열폭주로 확대될 가능성이 있습니다.

3. 권장 조치사항

3.1 즉시 조치 (24시간 이내)
- RACK_05 냉각 시스템 점검 및 정상 작동 여부 확인
- RACK_05 전력 부하 감소 또는 운영 중단 검토
- 주변 Rack (RACK_04, RACK_06)에 대한 온도 모니터링 강화
```

### 2.3 용어 사용 규칙

| 분류 | 금지 용어 | 권장 용어 |
|------|----------|----------|
| 설비 | Rack-05, **RACK_05** | RACK_05 |
| 심각도 | **CRITICAL**, 🔥Critical | Critical 등급 |
| 시간 | 10:15, 10시 15분 | 2025-12-13 10:15:00 |
| 온도 | 50도, 50C | 50.1°C |
| 조치 | 1. 긴급, **긴급** | 3.1 즉시 조치 (24시간 이내) |

### 2.4 문장 스타일

**금지:**
- "발견되었습니다!!!" (과도한 강조)
- "매우매우 위험합니다" (중복 표현)
- "RACK_05가 위험해요" (구어체)

**권장:**
- "발견되었습니다." (간결하고 명확)
- "심각한 위험이 있습니다" (적절한 강도)
- "RACK_05에서 위험이 감지되었습니다" (전문적 표현)

---

## 🎨 색상 팔레트 (절대 변경 금지)

### 위험도 색상 (LG Energy Solution 표준)

| 구분 | 배경색 | 테두리 | 텍스트 | HEX 코드 |
|------|--------|--------|--------|----------|
| **CRITICAL** | 연한 빨강 | 진한 빨강 | 어두운 빨강 | `#fee2e2`, `#dc2626`, `#991b1b` |
| **WARNING** | 연한 노랑 | 진한 주황 | 어두운 주황 | `#fef3c7`, `#f59e0b`, `#92400e` |
| **NORMAL** | 연한 초록 | 진한 초록 | 어두운 초록 | `#d1fae5`, `#10b981`, `#065f46` |
| **SENSOR FAULT** | 회색 | 회색 | 어두운 회색 | `#f3f4f6`, `#6b7280`, `#374151` |

### Chart.js 색상

| 용도 | 색상 | HEX 코드 |
|------|------|----------|
| 정상 선 (Thermal) | 초록 | `#22C55E` |
| 경고 선 (Thermal) | 빨강 | `#DC2626` |
| 정상 바 (SPC) | 파랑 | `#3B82F6` |
| 이상치 바 (SPC) | 빨강 | `#DC2626` |
| 유효 데이터 (Donut) | 초록 | `#22C55E` |
| 센서 고착 (Donut) | 주황 | `#F97316` |
| 범위 이탈 (Donut) | 빨강 | `#DC2626` |
| DC 버스 (Correlation) | 검정 | `#1E293B` |
| 연결 끊김 (Correlation) | 보라 | `#8B5CF6` |
| 정상 Rack (Correlation) | 회색 | `#CBD5E1` |

### Primary Colors (브랜드 색상)

```css
/* Primary Colors */
--primary-blue: #2563EB;     /* Tailwind blue-600, 메인 브랜드 색상 */
--deep-navy: #1E3A8A;        /* Tailwind blue-900, 헤더/강조 */
--vibrant-orange: #F97316;   /* Tailwind orange-500, 경고 */
--alert-red: #DC2626;        /* Tailwind red-600, 긴급 */
--success-green: #16A34A;    /* Tailwind green-600, 정상 */

/* Background Colors */
--bg-gradient-start: #1E3A8A;  /* Deep Navy */
--bg-gradient-end: #2563EB;    /* Primary Blue */
--bg-light: #F3F4F6;           /* Gray-100, 본문 배경 */
--bg-white: #FFFFFF;           /* 카드 배경 */

/* Text Colors */
--text-primary: #1F2937;       /* Gray-800, 본문 */
--text-secondary: #6B7280;     /* Gray-500, 부가 정보 */
--text-white: #FFFFFF;         /* 헤더 텍스트 */
```

---

## 📏 타이포그래피 (절대 변경 금지)

### 폰트

**기본 폰트:** `'Noto Sans KR', 'Malgun Gothic', sans-serif`
**코드 폰트:** `'Consolas', monospace`

### 폰트 크기

| 요소 | 크기 | 용도 |
|------|------|------|
| H1 | 28px | 리포트 제목 |
| H2 | 22px | 섹션 제목 |
| H3 | 18px | 하위 제목 |
| Body | 14px | 본문 |
| Small | 12px | 메타 정보, Footer |
| Large | 16px | Chart 제목 |

---

## 📐 여백 (절대 변경 금지)

| 크기 | 값 | 용도 |
|------|-----|------|
| XS | 5px | 최소 간격 |
| SM | 10px | 작은 간격 |
| MD | 15px | 중간 간격 |
| LG | 20px | 큰 간격 |
| XL | 30px | 섹션 간격 |

---

## 📊 Chart 설정 (절대 변경 금지)

### Chart 공통 설정

| 속성 | 값 |
|------|-----|
| **높이** | 350px (고정) |
| **최대 너비** | 700px |
| **반응형** | true |
| **Aspect Ratio** | false (높이 고정) |
| **애니메이션** | 750ms |

### Chart 종류 및 용도

| 분석 종류 | Chart 타입 | 설명 |
|-----------|------------|------|
| Thermal Safety | Line Chart | 시간별 온도 변화 추이 |
| SPC Balance | Bar Chart | Rack별 Z-Score 분포 |
| Data Integrity | Donut Chart | 센서 상태 비율 |
| System Correlation | Multi-Line Chart | DC 버스와 Rack 전압 비교 |

### Chart 1: 열적 안전성 (Line Chart)

**타입:** `line`

**데이터:**
- 정상 Rack: 녹색 선 (`#22C55E`), 굵기 2px
- 경고 Rack: 빨간색 선 (`#DC2626`), 굵기 3px, 배경 채움

**축:**
- Y축: "온도 (°C)"
- X축: "시간"

**데이터 소스:** Phase 2 `thermal_safety.json`의 `events[]`

**색상 규칙:**
```javascript
datasets: [
  {
    label: '정상 온도',
    borderColor: '#16A34A',        // Green
    backgroundColor: 'rgba(22, 163, 74, 0.1)'
  },
  {
    label: '위험 온도',
    borderColor: '#DC2626',        // Red
    backgroundColor: 'rgba(220, 38, 38, 0.1)'
  }
]
```

### Chart 2: SPC 밸런싱 (Bar Chart)

**타입:** `bar`

**데이터:**
- Z-Score > ±3: 빨간색 바 (`#DC2626`)
- Z-Score ≤ ±3: 파란색 바 (`#3B82F6`)

**축:**
- Y축: "시그마 (σ)", 범위 -4 ~ 4
- X축: Rack ID

**데이터 소스:** Phase 2 `spc_balance.json`의 `events[]`

**색상 규칙:**
```javascript
// Z-Score 값에 따라 동적 색상 적용
backgroundColor: z_scores.map(z =>
  Math.abs(z) > 3.0 ? '#DC2626' :  // Critical
  Math.abs(z) > 2.0 ? '#F97316' :  // Warning
  '#16A34A'                         // Normal
)
```

### Chart 3: 센서 무결성 (Donut Chart)

**타입:** `doughnut`

**데이터:**
- 유효 데이터: 녹색 (`#22C55E`)
- 센서 고착: 주황 (`#F97316`)
- 범위 이탈: 빨강 (`#DC2626`)

**Cutout:** 70% (도넛 구멍 크기)

**데이터 소스:** Phase 2 `data_integrity.json`의 `statistics`

**색상 규칙:**
```javascript
backgroundColor: [
  '#16A34A',  // 정상 (Green)
  '#F97316',  // 경고 (Orange)
  '#DC2626'   // 오류 (Red)
]
```

### Chart 4: 시스템 상관성 (Multi-Line Chart)

**타입:** `line`

**데이터:**
- 메인 DC 버스: 검정 점선 (`#1E293B`)
- 연결 끊김 Rack: 보라색 (`#8B5CF6`)
- 정상 Rack: 회색 (`#CBD5E1`)

**축:**
- Y축: "전압 (V)"
- X축: "시간"

**데이터 소스:** Phase 2 `system_correlation.json`의 `events[]`

### Chart 표준 설정 (chart_config.yaml)

```yaml
responsive: true
maintainAspectRatio: true
aspectRatio: 2
plugins:
  legend:
    display: true
    position: 'top'
  tooltip:
    enabled: true
    mode: 'index'
    intersect: false
scales:
  x:
    grid:
      display: true
      color: 'rgba(0, 0, 0, 0.1)'
  y:
    grid:
      display: true
      color: 'rgba(0, 0, 0, 0.1)'
    beginAtZero: true
```

---

## 🔧 데이터 매핑 규칙

### Phase 2 JSON → Chart.js 변환

**파일:** `config/global/html/markdown_converter.py`
**함수:** `prepare_chart_data(phase2_json_data)`

**변환 로직:**

1. **Thermal Chart:**
   - `thermal_safety.json` → `events[]` 최대 10개
   - `timestamp` → labels
   - `temperature` → warning_temps
   - 정상 기준선: 25.0 + (index * 0.1)

2. **SPC Chart:**
   - `spc_balance.json` → `events[]` 최대 6개
   - `rack_id` → labels
   - `z_score` → data

3. **Integrity Chart:**
   - `data_integrity.json` → `statistics`
   - `total_data_points`, `sensor_frozen_count`, `out_of_range_count` → 퍼센트 계산

4. **Correlation Chart:**
   - `system_correlation.json` → `events[]` 최대 6개
   - `timestamp` → labels
   - `dc_voltage`, `rack_voltage` → data

**중요:** 데이터가 없으면 기본 샘플 데이터 사용 (fallback)

---

## 📄 HTML 구조 (절대 변경 금지)

### 파일 위치

```
GEM/
├── config/global/
│   ├── templates/
│   │   └── battery_report_final.html  (메인 템플릿)
│   ├── styles/
│   │   ├── report_style.css           (CSS 스타일)
│   │   └── chart_config.yaml          (Chart 설정)
│   └── html/
│       └── markdown_converter.py      (MD → HTML 변환)
```

### Jinja2 변수

**필수 변수:**

```jinja2
{{ analysis_id }}              # RUN_ID
{{ timestamp }}                # 생성 시간
{{ battery_profile }}          # 배터리 프로파일
{{ critical_count }}           # Critical 건수
{{ warning_count }}            # Warning 건수
{{ normal_count }}             # 정상 건수
{{ chart_data_json }}          # Chart.js 데이터 (JSON)
{{ thermal_insights_html }}    # 열적 안전성 인사이트 (HTML)
{{ spc_insights_html }}        # SPC 인사이트 (HTML)
{{ integrity_insights_html }}  # 무결성 인사이트 (HTML)
{{ correlation_insights_html }}# 상관성 인사이트 (HTML)
{{ comprehensive_insights_html }}# 종합 인사이트 (HTML)
```

### 템플릿 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>GEM 배터리 안전 분석 리포트 - {{ analysis_id }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <style>
        /* CSS 임베드 */
        :root {
            --primary-blue: #2563EB;
            --alert-red: #DC2626;
            /* ... */
        }
    </style>
</head>
<body>
    <!-- Hero Header -->
    <header class="hero-header">
        <h1>GEM 배터리 안전 분석 리포트</h1>
        <p>분석 ID: {{ analysis_id }}</p>
        <p>생성 시간: {{ timestamp }}</p>
    </header>

    <!-- Summary Dashboard -->
    <section class="summary-dashboard">
        <div class="summary-card critical">
            <h3>Critical</h3>
            <p class="count">{{ critical_count }}</p>
        </div>
        <div class="summary-card warning">
            <h3>Warning</h3>
            <p class="count">{{ warning_count }}</p>
        </div>
        <div class="summary-card normal">
            <h3>Normal</h3>
            <p class="count">{{ normal_count }}</p>
        </div>
    </section>

    <!-- Tab Navigation -->
    <div class="tab-container">
        <button class="tab-btn active" onclick="openTab('thermal')">열적 안전성</button>
        <button class="tab-btn" onclick="openTab('spc')">셀 밸런싱</button>
        <button class="tab-btn" onclick="openTab('integrity')">센서 무결성</button>
        <button class="tab-btn" onclick="openTab('correlation')">시스템 상관성</button>
        <button class="tab-btn" onclick="openTab('comprehensive')">종합 인사이트</button>
    </div>

    <!-- Tab Content -->
    <div id="thermal" class="tab-content active">
        <canvas id="thermalChart"></canvas>
        <div class="insights">
            {{ thermal_insights_html | safe }}
        </div>
    </div>

    <div id="spc" class="tab-content">
        <canvas id="zscoreChart"></canvas>
        <div class="insights">
            {{ spc_insights_html | safe }}
        </div>
    </div>

    <div id="integrity" class="tab-content">
        <canvas id="integrityChart"></canvas>
        <div class="insights">
            {{ integrity_insights_html | safe }}
        </div>
    </div>

    <div id="correlation" class="tab-content">
        <canvas id="correlationChart"></canvas>
        <div class="insights">
            {{ correlation_insights_html | safe }}
        </div>
    </div>

    <div id="comprehensive" class="tab-content">
        <div class="insights">
            {{ comprehensive_insights_html | safe }}
        </div>
    </div>

    <!-- Footer -->
    <footer class="report-footer">
        <p>Generated by GEM Framework | Powered by Ollama</p>
    </footer>

    <script>
        const chartData = {{ chart_data_json | safe }};
        // Chart.js 렌더링 로직
        // ... (4개 Chart 생성 코드)
    </script>
</body>
</html>
```

---

## ✅ 품질 체크리스트

### 생성 전 체크

- [ ] Phase 2 JSON 데이터 존재 확인
- [ ] Ollama 서버 정상 동작 확인
- [ ] 템플릿 파일 존재 확인
- [ ] CSS 파일 존재 확인
- [ ] Chart 설정 파일 존재 확인

### 생성 후 체크

- [ ] HTML 파일 정상 생성 (results/{RUN_ID}/phase4_report/report.html)
- [ ] 브라우저에서 정상 렌더링
- [ ] Chart 4개 모두 표시
- [ ] 탭 메뉴 정상 동작
- [ ] 인사이트 텍스트에 Markdown/이모지 없음
- [ ] 색상 팔레트 정상 적용
- [ ] 반응형 디자인 동작 확인

### 스타일 일관성

- [ ] 모든 CSS가 `report_style.css`와 일치
- [ ] 4개 Chart가 `chart_config.yaml` 설정 사용
- [ ] Phase 2 실제 데이터 사용 (하드코딩 X)
- [ ] 오프라인 뷰어 작동 (Chart.js CDN만 필요)
- [ ] 반응형 동작 (모바일/데스크톱)
- [ ] 인쇄 최적화 (A4 용지)
- [ ] 색상이 팔레트와 정확히 일치
- [ ] 폰트 크기가 가이드와 정확히 일치
- [ ] 여백이 가이드와 정확히 일치
- [ ] Chart 높이 350px 고정

### 전문성 체크

- [ ] 문체가 전문 기술 리포트 수준
- [ ] 근거 기반 분석 포함
- [ ] 구체적인 수치 및 시간 명시
- [ ] 조치사항이 실행 가능하고 구체적
- [ ] 우선순위가 명확히 표시

---

## 🚫 절대 하지 말아야 할 것

1. **CSS 직접 수정 금지** - `report_style.css`만 수정
2. **색상 변경 금지** - 팔레트 고정
3. **Chart 크기 변경 금지** - 350px 고정
4. **데이터 하드코딩 금지** - Phase 2 JSON 사용
5. **구조 변경 금지** - Header → Cards → Content → Footer 순서 고정
6. **Markdown/이모지 사용 금지** - 전문 리포트 형식 유지

---

## 🔄 스타일 수정 프로세스

스타일 변경이 **정말 필요한 경우:**

1. `config/global/styles/report_style.css` 수정
2. `config/global/styles/chart_config.yaml` 수정
3. 이 문서 업데이트
4. Phase 3 재실행하여 HTML 재생성
5. 샘플 확인
6. Git commit with "BREAKING CHANGE: Style Guide Update"

---

## 📝 예시 비교

### 잘못된 예시 (Before)

```markdown
# 🔥 열적 안전성 분석

## 주요 발견사항
**RACK_05**에서 급격한 온도 상승(dT/dt = 4.8°C/min)이 감지되었습니다.

### CRITICAL 위험
- **RACK_05**: dT/dt = 4.8°C/min, 온도 50.1°C
- **조치 필요**: 긴급 냉각 시스템 점검!!!

### 권장 조치
1. **긴급**: RACK_05 점검
2. **주의**: 주변 Rack 모니터링 강화
```

**문제점:**
- Markdown 문법 사용 (#, ##, ###, **, -)
- 이모지 사용 (🔥)
- 과도한 강조 (!!!)
- 비전문적인 표현

### 올바른 예시 (After)

```
1. 분석 개요
분석 기간: 2025-12-13 10:00:00 ~ 2025-12-13 10:30:00
배터리 프로파일: NMC_LG
검증 기준: dT/dt (시간당 온도 변화율)
분석 임계값: Critical > 2.0°C/min, Warning > 1.0°C/min

2. 검증 결과

2.1 위험 감지 현황
총 3건의 열적 이상 징후가 감지되었습니다.
영향받은 설비: RACK_05, RACK_12, RACK_22

2.2 Critical 등급 위험
설비명: RACK_05
발생 시각: 2025-12-13 10:15:00
측정 온도: 50.1°C
온도 변화율: 4.8°C/min (임계값 2.0°C/min 초과)
위험도 판정: 열폭주(Thermal Runaway) 전조 증상
근거: 온도 상승 속도가 임계값의 2.4배에 달하며, 이는 배터리 내부 이상 발열을 의미합니다.
      방치 시 열폭주로 확대될 가능성이 있습니다.

3. 권장 조치사항

3.1 즉시 조치 (24시간 이내)
- RACK_05 냉각 시스템 점검 및 정상 작동 여부 확인
- RACK_05 전력 부하 감소 또는 운영 중단 검토
- 주변 Rack (RACK_04, RACK_06)에 대한 온도 모니터링 강화
```

**장점:**
- 번호 체계 명확 (1., 1.1, 2., 2.1, ...)
- Markdown/이모지 없음
- 구체적인 수치 및 시간 명시
- 근거 기반 분석 제공
- 전문적이고 명확한 문체

---

## 🔧 유지보수 가이드

### 스타일 변경 시 수정 위치

| 변경 사항 | 파일 위치 |
|----------|----------|
| 색상 변경 | `config/global/styles/report_style.css` |
| Chart 설정 변경 | `config/global/styles/chart_config.yaml` |
| 템플릿 구조 변경 | `config/global/templates/battery_report_final.html` |
| 인사이트 형식 변경 | `scripts/phase3_generate_insights.py` (프롬프트) |
| Markdown 변환 로직 | `config/global/html/markdown_converter.py` |

### 버전 관리

```
v1.1.0 (2025-12-23)
- IMMUTABLE 강조 추가
- 두 버전 통합 (간결함 + 상세 설명)
- 예시 비교 섹션 추가

v1.0.0 (2025-12-13)
- 초기 스타일 가이드 수립
- LG Energy Solution 색상 팔레트 적용
- 전문 리포트 형식 도입 (Markdown/이모지 제거)
- 4대 핵심 분석 탭 구조 구현
```

---

## 📞 문의

스타일 가이드 관련 문의:
- **담당자:** GEM Development Team
- **문서 위치:** `_dev/11_HTML-리포트-스타일-가이드.md`
- **CSS 위치:** `config/global/styles/report_style.css`
- **Chart 설정:** `config/global/styles/chart_config.yaml`

---

## 📚 참고 자료

### 내부 문서
- `_dev/10_AI-프롬프트-가이드.md`: AI 인사이트 생성 프롬프트
- `_dev/12_종합-인사이트-생성-로직.md`: Phase 3 AI 인사이트 생성 방법론

### 외부 표준
- NFPA 855: 에너지 저장 시스템 설치 표준
- UL9540A: 배터리 에너지 저장 시스템 안전성 테스트
- 한국 정부 ESS 안전성 평가 기준

### 기술 스택
- Chart.js 4.4.0: https://www.chartjs.org/
- Jinja2: https://jinja.palletsprojects.com/
- Tailwind CSS Colors: https://tailwindcss.com/docs/customizing-colors
- Ollama qwen2.5:32b: Local LLM for AI insights

---

**마지막 업데이트:** 2025-12-23
**버전:** 1.1.0
**작성자:** GEM Development Team
