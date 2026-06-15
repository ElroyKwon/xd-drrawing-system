---
tags:
  - 데이터지식스튜디오
  - 수집자료
  - 인덱스
aliases:
  - 수집자료 인덱스
created: 2026-06-11
updated: 2026-06-12
related:
  - "[[README]]"
  - "[[autodesk_cloud_research]]"
  - "[[dwg_parsing_and_web_cad_strategy]]"
  - "[[design_documents_map]]"
---

# 수집자료 폴더 인덱스

> **종합 요약**: 본 폴더는 [[데이터 지식 스튜디오]] (DKS) 구축 및 설계 프로세스에서 참조하는 대외 기술 조사 보고서, API 연동 가이드라인, 리서치 수집 자료들을 보관하는 아카이브 영역입니다. 각 하위 폴더별로 특정 외부 기술의 레퍼런스를 체계적으로 구조화하여 관리합니다.

---

## 1. 수집자료 목록

| 분류 | 자료명 | 경로 및 바로가기 | 설명 |
| :--- | :--- | :--- | :--- |
| **Autodesk Cloud** | Autodesk 클라우드 서비스 및 API 상세 조사 보고서 | [[autodesk_cloud_research]] | Autodesk Platform Services (APS) API 상세 분석 및 DKS 통합 아키텍처 연안 제안서 |
| **독자 웹 CAD** | 독자적 웹 CAD 도면관리 및 뷰어 시스템 구축 전략 보고서 | [[dwg_parsing_and_web_cad_strategy]] | 타사 DWG 파싱 원리 분석, 자체 웹 뷰어 아키텍처, 스냅/측정 및 AI 연동 개발 로드맵 |
| **개발 설계 (초안)** | 자체 웹 CAD 도면관리 플랫폼 개발 설계 문서 맵 | [[design_documents_map]] | 시스템 구축에 필요한 개발 설계 문서들의 종합 목록 및 목차 정의서 (선행 초안 — 아래 상세설계셋으로 승계) |
| **★ 상세설계 (현행)** | 도면관리 시스템 상세설계 (ACC Build 재현) | [[도면관리시스템_상세설계/00_개요-PMO/README]] | 청주 납품용 도면관리 시스템 13섹션·92문서 대기업급 설계 트리. **DWG 비편집·뷰어+오버레이** 전제. 벤치마크 = [[_ACC-Build-화면분석-재현설계]] |
| **ACC 화면분석** | Autodesk Construction Cloud Build 37화면 분석 | [[_ACC-Build-화면분석-재현설계]] | ACC Build 실제 화면 37장 한 장씩 분석 + 재현 컴포넌트 인벤토리·정보구조·로드맵 (`screenshot/`) |

---

## 2. 문서 업데이트 및 관리 지침
* **신규 자료 추가 시**:
    1. 관련 주제의 하위 폴더를 생성하고 해당 하위 폴더 내에 자료를 추가합니다.
    2. 본 `README.md`에 분류, 자료명, 링크 및 설명을 추가하여 최신 인덱스를 유지합니다.
    3. 본 문서 상단 YAML Frontmatter의 `updated` 날짜를 갱신합니다.
* **폴더 구조의 일관성**:
    * 모든 수집자료 마크다운 문서는 상단의 YAML Frontmatter 형식 규칙과 개념 첫 등장 시 `[[링크]]` 처리 규칙을 준수합니다.
