---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - 카메라행렬
  - SVG오버레이
  - 좌표변환
  - 마크업
created: 2026-06-12
related:
  - "[[README]]"
  - "[[01_threejs_rendering_pipeline]]"
  - "[[01_Requirements/03_functional_requirements]]"
---

# 05-3. 카메라 변환 행렬 및 마크업 오버레이 동기화 명세

> **목적**: 2D 도면에 완벽하게 들어맞는 카메라 투영(Orthographic) 모델을 설정하고, WebGL 도면 캔버스 위에 얹힌 투명 SVG 레이어(마크업 피드백용)가 패닝/줌 이벤트에도 흔들림 없이 밀착 연동되도록 행렬 변환 수학을 설계합니다.

---

## 1. 정투영 카메라(Orthographic Camera) 모델

일반 3D 게임용 카메라(PerspectiveCamera)는 멀리 있는 객체가 작게 보이는 원근 왜곡이 있어 치수와 평행이 중요한 CAD 뷰어에는 사용할 수 없습니다.

* **설정**: `THREE.OrthographicCamera`를 채택합니다. 카메라의 좌/우/상/하 절두체(Frustum) 경계값을 브라우저 뷰포트 크기에 맞춰 1:1로 설정합니다.
* **마우스 휠 Zoom-in/out 로직**:
  휠 델타(`wheelDelta`) 값을 받아 카메라의 `camera.zoom` 속성을 조절한 뒤 `camera.updateProjectionMatrix()`를 호출합니다.
  줌인/줌아웃 시 화면 중심이 아닌 **마우스 포인터가 위치한 곳**을 향해 확대되도록, 확대 전후의 마우스 월드 좌표 편차를 계산하여 `camera.position`을 보정 이동시킵니다.

---

## 2. SVG 마크업 레이어 행렬 동기화 메커니즘

협업의 핵심 기능인 '펜 마크업'은 무거운 WebGL 내부 요소로 다루지 않고, HTML5 DOM 위에 투명한 `<svg>` 태그 레이어를 덮어씌워 가볍게 구현합니다. 문제는 줌/팬 시 WebGL 씬은 움직이는데 SVG가 따로 노는 현상을 막는 것입니다.

### 2.1 CSS 3D Matrix 바인딩 공식
Three.js의 카메라는 내부적으로 $4 \times 4$ 투영 행렬(`projectionMatrix`)과 뷰 행렬(`matrixWorldInverse`)을 갖습니다. 카메라가 이동할 때마다, 이 두 행렬과 화면 해상도 보정값을 곱해 SVG 레이어의 CSS `transform` 속성으로 전송합니다.

```javascript
// WebGL 렌더 루프 내부의 카메라 동기화 로직
const camera = this.camera;
camera.updateMatrixWorld();

// 1. 카메라의 역행렬(뷰 행렬) 추출
const viewMatrix = camera.matrixWorldInverse;

// 2. 줌(Scale) 및 팬(Translate) 요소 추출
const scale = camera.zoom;
const tx = viewMatrix.elements[12];
const ty = viewMatrix.elements[13];

// 3. SVG 컨테이너의 CSS Transform 업데이트 (2D Matrix: a, b, c, d, tx, ty)
const svgContainer = document.getElementById("markup-svg-layer");
svgContainer.style.transform = `matrix(${scale}, 0, 0, ${-scale}, ${tx * scale}, ${-ty * scale})`;
svgContainer.style.transformOrigin = "0 0";
```
*(실제 브라우저 구현 시에는 Y축 반전 및 화면 정중앙 오프셋 보정이 추가로 필요합니다.)*

---

## 3. World to Screen 상호 좌표 역투영(Unproject)

챗봇 AI가 특정 `Handle ID`를 반환하여 하이라이트를 요구할 때(`Zoom-to-fit`), 해당 객체의 World 좌표 Bounding Box를 화면 중앙에 꽉 차게 피팅해야 합니다.

1. 타겟 기하 객체의 Bounding Box `min(x,y)`와 `max(x,y)`를 추출합니다.
2. 중심점 $Center_X = \frac{min_X + max_X}{2}$을 계산하여 `camera.position`의 타겟으로 삼습니다.
3. Box의 너비/높이 중 화면 가로세로 비율(Aspect Ratio) 대비 가장 긴 변을 찾아, 그 길이가 화면에 80% 여백으로 찰 수 있도록 `camera.zoom` 계수를 역산하여 세팅합니다.
4. 애니메이션 라이브러리(`GSAP` 또는 `TWEEN`)를 물려 0.5초 동안 부드럽게 카메라가 날아가도록 보간(Interpolation) 합니다.
