---
tags:
  - 도면관리시스템
  - 데이터설계
  - 도면기하JSON
  - DWG파싱
  - 2D뷰어
aliases:
  - 도면 기하 JSON 모델
  - Drawing Geometry JSON Model
created: 2026-06-12
related:
  - "[[03-1_데이터모델-개요]]"
  - "[[04_백엔드-DWG파싱-파이프라인]]"
  - "[[05_2D뷰어-렌더링설계]]"
  - "[[_ACC-Build-화면분석-재현설계]]"
---

# 도면 기하 JSON 모델

## ① 목적
- [[DWG]] 원본 파싱 결과를 웹 [[2D뷰어]]가 렌더링할 수 있는 **기하 JSON 규격** 단일 정의(SoT).
- 이 문서가 소유하는 주제 = **"파싱 산출물의 데이터 형태"** 그 자체뿐. 파싱 *방법*은 [[04_백엔드-DWG파싱-파이프라인]], 렌더링 *방법*은 [[05_2D뷰어-렌더링설계]]로 위임.
- 전제: DWG는 **편집하지 않는다**. 흐름 = DWG → 백엔드 파싱 → **기하 JSON(본 문서)** → 웹 렌더 → 마크업/이슈 오버레이. 본 JSON은 **읽기 전용 렌더 소스**.

## ② 배경 / 전제
- 1차 범위 = **2D 시트 한정** (3D BIM 범위 밖).
- 정밀 CAD 편집(osnap, 좌표 편집, [[SHX]] 폰트 정밀 렌더)은 범위 밖 → JSON은 "근사 렌더 + 식별자 보존"에 최적화.
- 차별점: 각 엔티티에 DWG **Handle ID**를 보존 → 향후 [[TypeDB]] 온톨로지의 **설비 엔티티 ID** 바인딩 키로 사용(핀/마크업/이슈를 픽셀이 아닌 엔티티에 묶기). 매핑 자체는 본 문서 범위 밖, 키 보존만 책임.
- Phase 0 파싱 산출물(분야·도면번호·태그)과 정합 → metadata 절에서 참조.

## ③ 상세 목차

## metadata (축척 / BBox)
> 시트 1장당 1개 메타 블록. 뷰어 초기 fit/zoom 및 좌표 변환 기준.

### 식별 필드
> sheetId, dwgHandle(파일 단위), 도면번호, 분야(discipline), 버전 — Phase 0 산출물과 키 정합.

### 단위 / 축척
> `units`(mm/inch), `scale`(예 1:100), `insUnits`(DWG 원본 단위코드). ❓ 축척 미기재 도면 처리 규칙 TBD.

### 경계 상자 (BBox)
> `extMin{x,y}`, `extMax{y,y}` (DWG EXTMIN/EXTMAX). 뷰어 viewBox 산출 근거.
#### 좌표계 메모
> DWG는 Y-up, 웹 캔버스는 Y-down → 변환 책임 위치 명시(파싱 단계 vs 렌더 단계). ❓ 결정 TBD.

## layers
> 레이어 목록 + 가시성/색상. 뷰어 레이어 토글 UI 소스(ACC "레이어 패널" 대응).

### 레이어 레코드
> `name`, `color`(ACI 또는 RGB), `visible`, `frozen`, `lineweight`. geometry는 layer를 name 참조.

### 레이어-분야 매핑(선택)
> 레이어명 규칙 → 분야 추론 가능 시 메모. 본격 매핑은 [[온톨로지-엔티티-바인딩]]으로 위임.

## geometry (line / arc / text + Handle ID)
> 렌더 대상 엔티티 배열. **공통 필드 + 타입별 필드** 구조.

### 공통 엔티티 필드
> `handle`(DWG Handle, 필수·불변 식별자), `type`, `layer`, `color`(override 시). handle = 오버레이/온톨로지 바인딩 키.

### line
> `{x1,y1,x2,y2}`. polyline은 vertices 배열로 평탄화(line 세그먼트화) 여부 ❓ TBD.

### arc / circle
> arc: `center{x,y}`, `radius`, `startAngle`, `endAngle`. circle: 각도 생략. ellipse 지원 여부 ❓ TBD.

### text / mtext
> `position{x,y}`, `value`, `height`, `rotation`. SHX 정밀 렌더 제외 → 폰트는 웹 기본 폰트 근사. ❓ MTEXT 서식 코드 제거 규칙 TBD.

### 미지원 / 폴백 엔티티
> hatch, dimension, block insert(INSERT) 등 → Phase 1 처리 방침(생략 / bbox 박스 폴백 / 추후) 메모. ❓ TBD.

#### block(INSERT) 처리
> 블록 참조를 펼칠지(explode) 참조로 둘지 — 설비 심볼이 블록인 경우가 많아 온톨로지 바인딩과 연관. ❓ 결정 TBD.

## 상대좌표 (RTC) 규칙
> 절대 DWG 좌표를 0~1 정규화(또는 BBox 기준 상대)로 변환하는 규칙. 마크업/이슈 핀 좌표 저장 형식과 직접 연결.

### RTC 정의
> Relative-To-Canvas: `(x - extMin.x) / (extMax.x - extMin.x)` 식. 핀/마크업이 줌·해상도 독립이 되도록.

### 적용 대상
> geometry 자체는 절대좌표 유지(렌더 변환은 뷰어), **오버레이(핀/마크업/이슈)** 저장 시에만 RTC 사용. 경계 명확화.

### 버전 간 좌표 안정성
> 시트 비교(버전 오버레이 diff)에서 두 버전 BBox가 다를 때 RTC 정합 문제. ❓ 정규화 기준(공통 BBox vs 각자) TBD → [[06_시트비교-diff설계]]와 협의.

## ④ 결정 대기 항목 (TBD / ❓)
- ❓ Y축 뒤집기(좌표 변환)를 파싱 단계 vs 렌더 단계 중 어디서?
- ❓ polyline → line 세그먼트 평탄화 여부 / arc·ellipse 곡선 보존 정밀도.
- ❓ block(INSERT) explode 정책 (설비 심볼 온톨로지 바인딩과 직결).
- ❓ hatch/dimension 등 미지원 엔티티 폴백 방식.
- ❓ 버전 간 RTC 정규화 기준 BBox.
- ❓ JSON 파일 크기 상한 / 대형 도면 청크·스트리밍 필요 여부 (성능은 [[05_2D뷰어-렌더링설계]] 소유, 여기선 데이터 형태 영향만).
- ❓ 축척 미기재 도면의 scale 기본값 규칙.

## ⑤ 관련 문서
- [[03-1_데이터모델-개요]] — 전체 데이터 엔티티 맵
- [[04_백엔드-DWG파싱-파이프라인]] — 본 JSON을 **생성**하는 파이프라인
- [[05_2D뷰어-렌더링설계]] — 본 JSON을 **소비**하는 렌더러
- [[06_시트비교-diff설계]] — 버전 오버레이 시 좌표 정합
- [[온톨로지-엔티티-바인딩]] — Handle ID → 설비 엔티티 ID 매핑(Phase 2)
- [[_ACC-Build-화면분석-재현설계]] — 벤치마크(레이어 패널·뷰어 동작 참조)
