---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - 웹CAD
  - Threejs
  - SVG
  - 하이브리드검색
  - Git_like
aliases:
  - 웹 CAD 뷰어 상세 설계 명세
  - CCD 상세 지침
created: 2026-06-11
updated: 2026-06-11
related:
  - "[[design_documents_map]]"
  - "[[04_API_Pipeline/README]]"
  - "[[01_Requirements/03_functional_requirements]]"
---

# 05. 웹 CAD 뷰어 상세 설계서 (CCD)

## 1. 하이브리드 검색 세션 연동 파트 (URL & State Receiver)
* **목적**: 글로벌 검색창이나 채팅 세션에서 특정 설비를 지목하여 신규 도면으로 진입했을 때, 뷰어가 로딩 완료 이벤트 직후 해당 객체를 자동 줌인 및 하이라이트하도록 구현합니다.
* **구현 명세**:
```javascript
class CADViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.initThreeJs();
    this.checkSessionParams();
  }

  // 1. URL 쿼리 파라미터 분석
  checkSessionParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const highlightHandle = urlParams.get('highlight');
    const autoFocus = urlParams.get('focus') === 'true';

    if (highlightHandle) {
      // 뷰어 도면 로딩 완료 콜백 등록
      this.on('documentLoaded', () => {
        this.highlightAndFocus(highlightHandle, autoFocus);
      });
    }
  }

  // 2. 외부 Handle 수신 시 하이라이트 및 카메라 이동 실행
  highlightAndFocus(handleId, triggerFocus = true) {
    const dbId = this.getDbIdByHandle(handleId);
    if (!dbId) return;

    // 객체 선택 및 색상 하이라이트 (파란색 점멸)
    this.selectObject(dbId, '#00a8ff');

    if (triggerFocus) {
      // 해당 객체 바운딩 박스를 기준으로 카메라 줌 앤 피팅
      this.fitCameraToObject(dbId, 50); // padding: 50
    }
  }
}
```

---

## 2. Auto Diff 오버레이 렌더링 엔진 (Version Diff Rendering)
* **목적**: V2 도면을 띄운 채 V1 버전과의 기하학적 차이점 비교 모드 진입 시, Diff 데이터를 로드하여 오버랩 렌더링을 처리합니다.
* **렌더링 셰이더 및 재질(Material) 제어**:
    * **추출된 추가 객체 (Added)**: 뷰어 엔진은 Diff API로부터 수신한 추가된 객체 목록(`added`)의 좌표를 렌더링하고, **초록색 실선 재질**(`color: #00ff00`, `linewidth: 2`)을 적용하여 씬에 덧그립니다.
    * **추출된 삭제 객체 (Deleted)**: 삭제된 객체 목록(`deleted`)은 현재 도면 V2에는 없으나, 화면상에는 점선 재질(`color: #ff0000`, `dashSize: 3`, `gapSize: 3`)을 적용하여 **빨간색 점선**으로 씬에 오버랩 렌더링합니다.
    * **토글 컨트롤**: `showDiff(visible)` 스위치 토글 시, 해당 Diff 메시 객체들을 담은 `THREE.Group`의 `.visible` 속성을 제어하여 브라우저 리드로우 없이 고속으로 화면을 대조합니다.

---

## 3. Git-like 마크업 레이어 오버레이 (Markup Overlay)
* **목적**: 도면 기하 구조(WebGL) 위에 투명한 SVG 레이어를 한 층 얹고, 줌/팬 이벤트 수신 시 이 오버레이를 실시간 연동하여 스케일링함으로써 사용자들의 수동 마크업 커밋을 동적으로 입혀줍니다.

```
┌──────────────────────────────────────────────┐
│  [SVG 마크업 레이어] (Markup Commit Paths)    │ ◄── 마우스 드로잉 좌표 보관 (S3 JSON)
├──────────────────────────────────────────────┤
│  [Three.js WebGL 도면 씬] (CAD Geometry)      │ ◄── 기본 도면 벡터 캐시 (WCS RTC 좌표)
└──────────────────────────────────────────────┘
```

* **마크업 뷰어 동기화**:
    * 뷰어의 `Camera` 줌인/팬 이벤트 발생 시, Three.js의 `viewMatrix`와 `projectionMatrix`를 SVG 레이어의 `transform` 속성(Matrix3D)에 1:1로 매핑 업데이트하여 도면 기하 구조와 마크업 낙서가 한 몸처럼 밀리지 않고 일치하여 작동하도록 처리합니다.
    * 사용자가 특정 마크업 커밋 버전을 체크하면, 해당 커밋의 JSON 파일(/static/markups/{id}.json)을 비동기 패치하여 SVG 패스(`d` 속성)로 실시간 복원해 줍니다.
