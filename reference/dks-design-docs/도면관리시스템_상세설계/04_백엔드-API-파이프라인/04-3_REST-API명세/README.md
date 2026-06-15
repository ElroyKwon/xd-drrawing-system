---
tags:
  - REST-API
  - API명세
  - 백엔드
  - 도면관리시스템
  - 표준규약
aliases:
  - REST API 명세 개요
  - API 인덱스
created: 2026-06-12
related:
  - "[[04_백엔드-API-파이프라인]]"
  - "[[ACC-Build-화면분석-재현설계]]"
  - "[[데이터-지식-스튜디오]]"
---

# REST API 명세 개요

## ① 목적
- 청주 도면관리 시스템 백엔드의 **리소스별 REST API 인덱스 + 전사 표준 규약**을 한 곳에 고정
- 이 문서 = "API 카탈로그 + 공통 계약". 개별 엔드포인트의 상세 요청/응답 스키마는 각 리소스 하위 문서로 위임 (DRY)
- 프런트(앱셸·데이터테이블·인스펙터)와 백엔드가 동일한 [[표준 response 포맷]]·에러·페이지네이션 규약을 공유하도록 단일 계약 수립

## ② 배경/전제
- 핵심 스코프 = **뷰어 + 주석/이벤트 오버레이** ([[DWG]] 비편집). 흐름: DWG → 백엔드 파싱 → 기하 JSON → 웹 2D 뷰어 → 마크업/이슈/이벤트 오버레이
- 따라서 API는 "도면 편집"이 아니라 **읽기(기하·시트) + 오버레이 CRUD(마크업·이슈·이벤트)** 중심
- 1차 범위 = 2D 시트 한정. 3D/[[BIM]] 리소스 없음
- 통신: REST 기본 + 실시간 협업 채널은 [[WebSocket]]로 분리 위임 ([[04-4_실시간-협업채널]]에서 소유, 본 문서는 REST만)
- 차별점: 핀/마크업/이슈는 픽셀 좌표뿐 아니라 **설비 엔티티 ID**([[TypeDB]] 온톨로지)에도 바인딩 가능 → 관련 리소스 스키마에 `entity_id` 선택 필드 예약 (Phase 2 활성화)

## ③ 상세 목차

## 표준 response 포맷
- 전 엔드포인트 공통 응답 봉투(envelope) 정의. 프로젝트 CLAUDE.md §5 표준 따름
- 채울 내용: 성공/실패 양쪽 동일 골격, `meta` 확장 규칙

### 성공 응답
- 채울 내용: `{ success: true, data, error: null, meta }` 형태. 단일 리소스 vs 컬렉션(`data` = 배열 + `meta.pagination`) 구분
```json
{ "success": true, "data": {}, "error": null, "meta": { "timestamp": "ISO8601" } }
```

### 실패 응답
- 채울 내용: `{ success: false, data: null, error: { code, message }, meta }`. HTTP status와 `error.code` 매핑 표

### meta 필드 규약
- 채울 내용: `timestamp`(필수), `pagination`, `request_id`(추적용), `version`(API 버전) — 어떤 상황에 무엇이 들어가는지

## 에러코드 체계
- 도메인 무관 공통 코드 + 리소스별 코드의 네이밍 컨벤션 정의
- 채울 내용: 코드 문자열 규칙(예: `RESOURCE_REASON`), HTTP status 대응

### 공통 에러코드
- 채울 내용: 인증(`AUTH_*`), 검증(`VALIDATION_*`), 권한(`FORBIDDEN`), 404(`NOT_FOUND`), 충돌(`CONFLICT`), 서버(`INTERNAL`) 표
- 형식: | code | HTTP | 의미 | 발생 리소스 |

### 리소스별 에러코드
- 채울 내용: 파싱 실패(`SHEET_PARSE_FAILED`), 버전 비교 불가(`COMPARE_VERSION_MISMATCH`), 엔티티 미해결(`ENTITY_UNRESOLVED`) 등 — 각 리소스 문서에서 정의, 여기선 네임스페이스만 예약

### 검증 에러 상세 포맷
- 채울 내용: 필드 단위 검증 실패 시 `error.details[]` 배열 구조(field·rule·message). 모달폼 인라인 에러 표시와 연동

## 페이지네이션/필터 규약
- 데이터테이블(시트목록·이슈목록·파일목록·사진) 공통 쿼리 규약. 정렬·컬럼토글·필터·내보내기 UI를 한 규약으로 지원
- ❓TBD: offset 방식 vs cursor 방식 — 이슈/사진 대량 스크롤 고려해 결정 대기

### 페이지네이션
- 채울 내용: 쿼리파라미터(`page`/`size` 또는 `cursor`/`limit`), 응답 `meta.pagination`(total·page·size·has_next)
- ❓TBD: 기본 page size, 최대 size 상한

### 필터링
- 채울 내용: 필터 쿼리 문법(`filter[field]=value`, 범위/다중값), 리소스별 허용 필터 화이트리스트는 각 문서로 위임
- 채울 내용: 이슈 모듈 필터(상태·담당·분야·시트) → 데이터테이블 필터 UI 매핑

### 정렬
- 채울 내용: `sort=field`, `sort=-field`(내림차순), 다중 정렬 표기

### 내보내기
- 채울 내용: 데이터테이블 "내보내기" → 동일 필터 적용한 CSV/엑셀 응답 규약(별도 엔드포인트 vs `?format=csv`)
- ❓TBD: 동기 다운로드 vs 비동기 작업(job) 방식

## 리소스 목록
- 모듈→리소스→엔드포인트 인덱스 표. ACC Build 37화면 모듈과 1:1 정렬. 각 행은 상세 문서로 링크
- 인덱스 표 형식: | 리소스 | 베이스 경로 | 주요 메서드 | 상세 문서 |

### 시트 / 도면 (Sheets)
- 채울 내용: 시트 목록 조회, 단일 시트 메타, **기하 JSON 조회**(뷰어 렌더 원천), 버전 목록. 모두 읽기 전용(DWG 비편집)
- 엔드포인트 후보: `GET /sheets`, `GET /sheets/{id}`, `GET /sheets/{id}/geometry`, `GET /sheets/{id}/versions`
- 위임: 기하 JSON 스키마는 [[04-1_도면-파싱-파이프라인]] / 뷰어 렌더는 [[02_프런트-2D뷰어]]

### 마크업 (Markups)
- 채울 내용: 시트 위 펜·도형·화살표 오버레이 CRUD. 좌표계 = 뷰어 도면 좌표(픽셀 아님)
- 엔드포인트 후보: `GET/POST /sheets/{id}/markups`, `PATCH/DELETE /markups/{id}`
- 채울 내용: `entity_id` 선택 바인딩 필드 (Phase 2)

### 이슈 (Issues)
- 채울 내용: 핀 좌표 + 상세폼(제목·상태·담당·분야) + 목록/필터. ACC 이슈 모듈 동등
- 엔드포인트 후보: `GET/POST /issues`, `GET/PATCH /issues/{id}`, `GET /sheets/{id}/issues`(핀 오버레이용)
- 채울 내용: 핀의 `entity_id` 바인딩 → 향후 영향도/AI채팅 연결고리 (우리 차별점)

### 시트 비교 (Compare)
- 채울 내용: 두 버전 오버레이 diff 결과 조회. 서버 사전계산 vs 온디맨드
- 엔드포인트 후보: `GET /sheets/{id}/compare?base=&target=`
- ❓TBD: diff 산출을 백엔드가 하는지 뷰어가 하는지 (경계 결정 대기)

### 파일 / CDE (Files)
- 채울 내용: 폴더형 [[CDE]] 트리·파일 메타·업로드. DWG 원본 보관 + 파싱 트리거 진입점
- 엔드포인트 후보: `GET /folders/{id}`, `GET/POST /files`, `GET /files/{id}`
- 위임: 업로드→파싱 잡 트리거는 [[04-1_도면-파싱-파이프라인]]

### 사진 (Photos)
- 채울 내용: 현장 사진 목록·메타·시트/이슈 연결
- 엔드포인트 후보: `GET/POST /photos`, `GET /photos/{id}`

### 홈 / 대시보드 위젯 (Dashboard)
- 채울 내용: 홈 위젯 카드용 집계 데이터(이슈 카운트·최근 활동). 읽기 전용 집계 엔드포인트
- 엔드포인트 후보: `GET /dashboard/widgets`, `GET /activities`

### 프로젝트 / 앱셸 메타 (Projects)
- 채울 내용: 프로젝트 스위처·모듈 사이드바 구성에 필요한 프로젝트 목록·권한·멤버
- 엔드포인트 후보: `GET /projects`, `GET /projects/{id}/members`

### (Phase 2) 온톨로지 / AI 질의
- 채울 내용: 엔티티 검색·영향도·AI채팅 바인딩 엔드포인트 — **범위 밖(향후)**. 골격만 예약, 상세는 [[06_온톨로지-AI연동]]로 위임
- ❓TBD: REST vs 전용 채널 — Phase 2 착수 시 결정

## ④ 결정 대기 항목
- ❓ 페이지네이션 방식: offset vs cursor (대량 이슈/사진 기준)
- ❓ 내보내기: 동기 다운로드 vs 비동기 job
- ❓ 시트 비교 diff 계산 위치: 백엔드 사전계산 vs 뷰어 온디맨드
- ❓ API 버전 표기 위치: URL prefix(`/v1`) vs 헤더 vs `meta.version`
- ❓ 인증 방식 상세: 토큰 종류·갱신 (보안 문서로 위임할지 여부 포함) → [[04-5_인증-권한]] 신설 여부 TBD
- ❓ `entity_id` 바인딩 필드를 Phase 1 스키마에 미리 넣을지(예약) vs Phase 2에서 추가할지

## ⑤ 관련 문서
- [[04_백엔드-API-파이프라인]] — 상위 인덱스
- [[04-1_도면-파싱-파이프라인]] — DWG→기하 JSON 산출(시트 기하 원천)
- [[04-4_실시간-협업채널]] — WebSocket 실시간(본 문서는 REST만 소유)
- [[02_프런트-2D뷰어]] — 기하 JSON 렌더·오버레이 좌표계
- [[ACC-Build-화면분석-재현설계]] — 모듈/화면 벤치마크
- [[06_온톨로지-AI연동]] — Phase 2 엔티티 바인딩·AI 질의
