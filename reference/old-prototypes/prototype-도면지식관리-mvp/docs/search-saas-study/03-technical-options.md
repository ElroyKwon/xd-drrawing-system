# 03 · 클릭 이벤트 구현 3종 + 현 스택 적합도

> **문서 성격**: 02에서 정리한 **Click-to-Search** 패턴을 실제로 웹에 구현할 때의 3가지 기술 옵션을 비교. 현 프로젝트 스택(Next.js 15 + React 19 + react-pdf + zoom-pan-pinch)에 어떻게 얹을 수 있는지까지 끌고 간다.

---

## 1. 3가지 접근 요약

| 옵션 | 요지 | 입력 도면 형식 | 정확도 | 구축 비용 | 런타임 비용 |
|---|---|---|:---:|:---:|:---:|
| **A. SVG 오버레이** | 벡터화된 도면에 `id/data-tag`를 주입, DOM 이벤트 | DWG/DXF → SVG | ◎ | 중 (변환 파이프라인) | 저 |
| **B. Canvas 바운딩박스** | OCR/Vision으로 좌표 DB 선구축, 투명 hit-area | PNG/PDF(이미지) | ○ | 저~중 (사전 1회) | 저 |
| **C. 동적 비전 추론** | 클릭 지점 크롭 → LVM(비전 LLM)이 추론 | 임의 이미지 | △~○ | 저 (사전 없음) | 고 (매 클릭 API) |

**원칙**: 하나만 쓰지 말고 **하이브리드**. 사전 구축된 B로 80% 커버, 미매칭 시 C로 폴백, 장기적으로는 A로 승격.

---

## 2. 옵션 A — SVG 오버레이

### 작동 방식
1. CAD 원본(DWG/DXF)을 SVG로 변환하면서 각 객체에 `id="eq_CH-001"` 또는 `data-tag="CH-001"` 주입.
2. 브라우저는 SVG를 DOM으로 받고, `<g data-tag>`에 onClick 바인딩.
3. 클릭 시 `event.currentTarget.dataset.tag` 추출 → 검색 API 호출.

### 장점
- **픽셀이 아니라 객체**가 이벤트 주체라 줌/팬 후에도 정밀.
- 외곽선을 따라 정확히 선택(hit-test 완벽).
- 접근성(ARIA) 붙이기 쉬움.

### 단점
- **변환 파이프라인**이 필요. DWG→SVG는 LibreDWG, Autodesk APS(Model Derivative), `ODA File Converter`+Inkscape 등 선택지. 모두 도메인 엔지니어링 필요.
- 레이어·좌표·심볼 라이브러리가 많은 도면은 파일 크기 문제.
- 이미지/스캔 도면엔 적용 불가.

### 현 프로젝트 적합도
- `(s1)`의 8건 도면 중 **벡터 PDF는 일부**, 이미지 fallback도 섞여 있음. SVG 변환 자산이 없으므로 **현재 MVP에서 옵션 A 단독은 비현실적**.
- 미래에 실 DWG이 공급되면 우선순위 1.

---

## 3. 옵션 B — Canvas/Div 바운딩박스 매핑

### 작동 방식
1. 사전에 도면을 OCR + Object Detection(YOLO 계열 또는 `layoutparser`, Azure AI Document Intelligence)으로 돌려 `{tag, x, y, w, h, page}` 리스트 생성.
2. JSON을 로드한 뒤 이미지/PDF 위에 **투명 `<div>` 또는 SVG `<rect>`** 레이어를 좌표대로 배치.
3. 각 영역에 onClick 바인딩. 실제 그림 위에는 아무 그림도 얹지 않음 (투명).

### 장점
- 기존 이미지/PDF 그대로 재활용.
- 현 `AnnotationLayer`의 0–1 정규화 좌표 패턴과 **구조 동일** — 코드 재사용 가능.
- 좌표만 있으면 어떤 뷰어든 얹을 수 있음.

### 단점
- 사전 추출 정확도에 결과가 묶임 (잘못 뽑힌 bbox는 영영 클릭 안 됨).
- 심볼이 겹치거나 작은 글자는 추출 실패 빈도 높음.
- 도면 개정(Rev) 시 좌표 재생성 필요.

### 현 프로젝트 적합도
- **가장 현실적**. `AnnotationLayer`가 이미 `x, y ∈ [0,1]` 정규화 좌표를 쓰고, zoom-pan-pinch도 여기 맞춰 동작한다.
- 프로토타입 단계에선 **수동으로** `data/doc-hotspots.json`을 몇 개만 찍어도 시연 가능.
- 실운영에서는 Azure Document Intelligence / Google Document AI / 오픈소스 `layoutparser`가 표준.

### 코드 골격 (현 스택)
```ts
// data/doc-hotspots.json
// [{ doc_id, page, tag, x, y, w, h }]
<HotspotLayer
  hotspots={hotspots.filter(h => h.doc_id === selected.doc_id && h.page === pageNumber)}
  width={renderedWidth} height={renderedHeight}
  onClick={(tag) => setQuery(tag)}  // → Search-to-Highlight과 양방향 연결
/>
```
기존 `AnnotationLayer`와 동일한 `renderOverlay` 슬롯에 합성 가능. **보존 6항목의 pointer-events 분리 패턴 그대로**.

---

## 4. 옵션 C — 동적 비전 추론

### 작동 방식
1. 사용자가 도면 임의 좌표 클릭.
2. 해당 지점 주변 256×256 crop을 비전 LLM(GPT-4V/Gemini Vision/Claude Vision)에 전송.
3. "이 영역의 장비 태그는 무엇인가? 가장 가까운 텍스트는?" 프롬프트.
4. 응답을 검색 쿼리로 변환.

### 장점
- **사전 인덱싱 0** — 아무 도면에나 즉시 적용.
- 도면 개정에 무관.
- 수기 도면, 스캔본, 낙서까지도 가능.

### 단점
- **매 클릭이 API 호출** — 지연 1~3초, 과금 누적.
- 정확도 가변. 특히 비슷한 심볼이 조밀한 P&ID에서 취약.
- 네트워크 실패 시 fallback 없으면 UX 파탄.

### 현 프로젝트 적합도
- **B의 폴백**으로 쓰기 좋음. 사전 구축된 bbox에 클릭이 안 맞으면 C를 호출.
- 시연용 wow-factor 요소지만, 기본 경로로 삼기엔 비용·지연 모두 부담.
- 현 Insight Lab의 Gemini 연동이 이미 있으므로, 같은 키로 프로토타입 가능.

---

## 5. 옵션 간 조합 전략

```
[사용자가 도면 클릭]
       │
       ▼
[B: 사전 bbox 매칭 시도] ──(hit)──► 태그 확정 → 검색
       │
       └─(miss)─► [C: Vision LLM 추론] → 태그 후보 → 사용자 확인 → 검색
                           │
                           └── 신뢰도 낮으면 [수동 태그 입력 모달]
```

- 운영 단계에 **B의 bbox를 A(SVG)로 승격**. 신규 도면은 DWG으로 받고 변환 파이프라인에서 SVG+bbox 동시 생산.
- 데이터 플라이휠: C가 맞춘 결과를 사용자가 confirm하면 B의 bbox JSON에 추가 학습.

---

## 6. 현 스택에서의 구현 장소 지도

| 레이어 | 현 파일 | 신규 트랙 변경 |
|---|---|---|
| 페이지 라우트 | `src/app/(s1)/page.tsx` | **건드리지 않음** |
| 페이지 라우트 | — | `src/app/(s3)/concept/page.tsx` 신설 |
| 뷰어 | `src/components/PdfViewer.tsx` | 재사용 (보존 6항목, `renderOverlay` 그대로) |
| 오버레이 | `src/components/AnnotationLayer.tsx` | 참조만, 새로 `HotspotLayer.tsx` 작성 |
| 데이터 | `data/doc-entity-links.json` | 참조 + 신규 `data/concept/hotspots.json` |
| 스토어 | `src/lib/annotations-store.ts` | 참조만 |

핵심 원칙: **보존 6항목 불변 + 신규 코드는 `(s3)/concept`와 `data/concept/`에만**. 기존 (s1), (s2) 동작 제로 영향.

---

## 7. 의사결정 체크리스트

- [ ] 시연까지 실 DWG을 확보할 가능성? (→ 없으면 A 탈락)
- [ ] Vision API 키(Gemini) 시연 시 온라인 사용 가능? (→ 없으면 C 탈락, 결정론 mock 필요)
- [ ] 8건 도면에 수동으로 각 3~5개 hotspot 찍을 여력? (→ 있으면 B 단독으로 프로토타입 충분)
- [ ] "클릭하면 연결 문서·영향 하위 나오는" 시연만 돼도 회의 목적 달성인가?

이 체크리스트의 답이 다음 문서(04)에서 권장 조합을 결정한다 → [04-decisions-for-this-project.md](./04-decisions-for-this-project.md).

---

## 참고

- [Complete guide to PDF.js — Nutrient](https://www.nutrient.io/blog/complete-guide-to-pdfjs/)
- [Custom PDF Rendering with PDF.js — SitePoint](https://www.sitepoint.com/custom-pdf-rendering/)
- [OpenSeadragon](https://openseadragon.github.io/)
- [Your Comprehensive Guide to SVG in PDF — Devzery](https://www.devzery.com/post/your-comprehensive-guide-to-svg-in-pdf)
- [PDF to HTML5 or SVG — IDR Solutions BuildVu](https://www.idrsolutions.com/buildvu/)
- [Viewer SDK — Autodesk Platform Services](https://aps.autodesk.com/viewer-sdk)
- [Adding custom meta-properties to viewer property panel — ADN Dev Blog](https://adndevblog.typepad.com/cloud_and_mobile/2015/05/adding-custom-meta-properties-to-the-viewer-property-panel.html)
