---
tags:
  - 데이터지식스튜디오
  - 개발설계
  - WebGL
  - Threejs
  - 렌더링
  - 성능최적화
created: 2026-06-12
related:
  - "[[README]]"
  - "[[02_spatial_indexing_and_osnap]]"
  - "[[03_camera_matrix_and_markup]]"
---

# 05-1. Three.js 기반 WebGL 렌더링 파이프라인 설계 명세

> **목적**: 100MB 이상의 대용량 플랜트 계통도(P&ID)를 웹 브라우저에서 60fps로 끊김 없이 렌더링하기 위해, Three.js의 하위 레벨 API를 활용한 극한의 메모리 통제 및 드로우 콜(Draw Call) 최적화 전략을 정의합니다.

---

## 1. 드로우 콜(Draw Call) 병목의 해소 원칙

브라우저 렌더링의 최대 적은 객체의 개수입니다. 선분 10만 개를 10만 개의 `THREE.Line` 객체로 `scene.add()` 하면 1프레임을 그리는 데 수 초가 걸립니다. 이를 우회하기 위한 2대 핵심 전략을 적용합니다.

### 1.1 BufferGeometry 단일 병합 (Merge Strategy)
도면 파이프라인에서 추출된 JSON을 파싱할 때, 동일한 색상(Layer Color)과 선 두께를 가진 모든 LINE, ARC, POLYLINE을 하나의 거대한 `Float32Array` 버퍼로 몰아넣습니다.
* **구현체**: `THREE.LineSegments` 와 `THREE.BufferGeometry`
* **효과**: 수만 개의 선분들을 단 1개의 드로우 콜로 GPU에 전송하여 메인 스레드 오버헤드를 0에 가깝게 만듭니다.

### 1.2 InstancedMesh 활용 (블록 객체 GPU 인스턴싱)
도면에는 펌프, 밸브 등 동일한 형상의 기호(CAD Block)가 수십~수백 번 반복(INSERT)됩니다.
* **구현체**: `THREE.InstancedMesh`
* **원리**: 밸브의 기하 형상(Geometry)은 메모리에 단 1번만 올리고, $N$개의 밸브가 놓일 위치의 변환 행렬(Translation/Rotation Matrix)만 $N$크기의 행렬 배열로 묶어 GPU에 전달합니다.
* **효과**: GPU 레벨에서 복제 렌더링을 처리하므로, 밸브 1만 개를 띄워도 메모리 점유율과 드로우 콜은 1개어치에 불과합니다.

---

## 2. 커스텀 셰이더 적용 (Custom ShaderMaterial)

CAD의 고유한 표현 방식(특히 점선, 쇄선)을 CPU에서 쪼개어 그리면 정점의 수가 기하급수적으로 늘어납니다. 이를 WebGL의 프래그먼트 셰이더(Fragment Shader) 단에서 수학적으로 처리합니다.

* **선종류(Linetype) 셰이더**: 
  `THREE.LineBasicMaterial` 대신 `THREE.ShaderMaterial`을 상속받아 커스텀 셰이더를 작성합니다. 정점 간의 누적 길이(Distance)를 계산하고, 셰이더 내에서 `mod(distance, dashSize + gapSize)` 연산을 수행하여 gap 구간에 해당하는 픽셀을 `discard;` 처리합니다.
  
```glsl
// Fragment Shader (Dashed Line Core)
uniform float dashSize;
uniform float gapSize;
varying float vLineDistance;

void main() {
    float totalSize = dashSize + gapSize;
    if (mod(vLineDistance, totalSize) > dashSize) {
        discard; // gap 영역은 픽셀을 버림 (투명화)
    }
    gl_FragColor = vec4( diffuse, opacity );
}
```

---

## 3. MSDF (웹폰트 렌더러) 적용

도면 내 수만 개의 텍스트를 `THREE.TextGeometry`로 생성하면 엄청난 수의 폴리곤이 생성되어 메모리가 터집니다.

* **MSDF (Multi-channel Signed Distance Field)** 전략:
  텍스트를 3D 폴리곤으로 파싱하지 않고, 각 문자의 외곽선 거리 정보를 담은 특수 텍스처(MSDF Font Atlas)를 생성하여 평면 Quad 폴리곤에 맵핑합니다.
* **효과**: 뷰어를 수백 배 줌인(Zoom-in) 해도 픽셀 깨짐이나 계단 현상(Aliasing)이 없는 완벽히 날카로운 벡터 텍스트를, 최소한의 메모리로 렌더링할 수 있습니다. 
* **한글 처리**: 도면 텍스트에서 한글이 포함될 경우를 대비해, 필요한 경량화된 한글 완성형 MSDF 폰트 에셋을 동적 로딩하여 적용합니다.
