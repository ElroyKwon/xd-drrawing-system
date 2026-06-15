# 검증 — 시연 5/10/20분 + 회귀 체크리스트

## Quick smoke (각 작업 후 5분)

```bash
cd "D:/_Project/prototype-도면지식관리-mvp"
npm run dev          # 부팅 확인
npx tsc --noEmit     # 타입 체크
npm run lint         # ESLint
npm run test         # vitest (W2-T3 이후)
```

브라우저: `/` 진입 → CLAUDE.md 정의 시나리오 A·B·C 통과
- A (검색): "냉동기" → doc-003/doc-004 → 클릭 → 뷰어
- B (주석): 뷰어 클릭 → 메모 저장 → 새로고침 → 핀 유지
- C (역추적): 우측 "설비 역추적" 탭 → CH-001 → doc-003·doc-004 리스트

---

## W4 통합 시연 — 5분 (시나리오 1·2·5 핵심)

| # | 행위 | 화면/URL | 기대 |
|--:|------|----------|------|
| 1 | `/` 진입 → 검색바에 "전기 단선도" | `/(s1)/` 또는 `/(s1)/search` | 결과 9건 (EE-01-XXX) |
| 2 | 첫 결과 클릭 | `/drawings/dwg-elec-001` | PDF 1페이지 렌더 (≤ 3초) |
| 3 | 우측 사이드 "설비 역추적" 탭 → "VCB-001" 입력 | 동일 | 1+개 도면 매칭 표시 |
| 4 | 매칭 도면 클릭 | `/drawings/dwg-elec-001?page=1` | 페이지 점프 |
| 5 | 뷰어 본문 클릭 → "정비 시 우선 잠금" 입력 → 저장 | Popover open → close | 핀 표시 + LS 저장 |
| 6 | SideNav "인사이트" → "알람" | `/insight/alarms` | 10건 리스트, critical 3건 |
| 7 | CHW-T-HI-007 → [AI 물어보기] | `/insight/answers/<id>` | AnswerCard 5섹션 스트리밍 |
| 8 | EvidenceList "도면 dwg-mech-002 [열기]" 클릭 | `/drawings/dwg-mech-002?page=N&highlight=AHU-3F-01&from=insight&query_id=<id>` | 도면 + 태그 강조 + 브레드크럼 "← 인사이트로" |
| 9 | 브레드크럼 클릭 | `/insight/answers/<id>` 복귀 | 답변 그대로 |

**총 5분. 포인트**: NAS+엑셀 vs 본 서비스 시간 압축 + 답+근거 자연 흐름.

---

## W4 통합 시연 — 10분 (5분 + 시나리오 4·근본원인)

10. SideNav "검색" → 한글 "옥상 통신" 입력 → 결과 (`disciplineKo` Fuse 가중)
11. 핀 3개 추가 → AnnotationList에서 검색·삭제·수정 회귀
12. AnswerCard FollowUpSuggestions "근본원인 보기" → `/insight/root-cause/ahu-3f-01`
13. Cytoscape 그래프 + 후보 3개 + 1순위 "도면으로" 클릭 → 도면 이동

---

## W4 통합 시연 — 20분 (10분 + 모바일·보고서·크로스오버)

14. Chrome DevTools 375×812 토글 → `/drawings/dwg-elec-001` → 탭바 [리스트|뷰어|사이드] 표시
15. 사이드 탭 → 역추적 → 뷰어 탭 자동 복귀
16. SideNav "보고서" → `/insight/reports/report-daily-20260417`
17. 좌Python 수치 / 우SLM 해석 분할 → 우측 편집 → status reviewed
18. "확정" → finalized
19. Header GlobalSearchBar 탭 전환으로 서비스 1↔2 자유 이동
20. NotificationBell 배지 "3" 확인 → 클릭 → `/insight/alarms`

**총 20분. 포인트**: 두 서비스 한 쉘 자연 흐름 + Dual Engine 철학 + 근거 병기.

---

## 회귀 체크리스트 (W4-T2, 30~40 항목)

### 보존 6항목
- [ ] B-1: PdfViewer pickMode (실 PDF / 더미 PDF / 이미지 only 3 도면 각 1회)
- [ ] B-1: PdfViewer key 패턴 (문서 전환 시 totalPages 잔존 X)
- [ ] B-2: AnnotationLayer pointer-events (뷰어 클릭 시 핀 생성, 핀 클릭 시 popover)
- [ ] B-3: AnnotationPopover Escape 닫기
- [ ] B-3: 빈 텍스트 disabled
- [ ] B-4: hydrated 플래그 (LS 비어있을 때 빈 배열 안 덮어쓰기)
- [ ] B-4: LS_KEY="mvp-annotations-v1" 기존 주석 보존
- [ ] B-5: data-loader toUpperCase (소문자 entity_tag 검색 → 대문자로 매칭)
- [ ] B-6: TransformWrapper doubleClick (더블탭 줌 안 됨)

### 18 PDF 렌더
- [ ] 전기 9건 모두 1페이지 렌더 (≤ 3초)
- [ ] 통신 5건 모두 렌더
- [ ] 건축·기계·소방 4건 모두 렌더
- [ ] 페이지 네비게이션 (다음/이전)

### LLM 양 모드
- [ ] mock 모드: SSE 스트리밍 + 50ms 토큰
- [ ] mock 모드: evidence 비어있지 않음
- [ ] live 모드: Anthropic API 응답
- [ ] live 모드: ANTHROPIC_API_KEY 누락 시 명확한 에러
- [ ] mock↔live 토글 즉시 전환

### URL 규약
- [ ] `/drawings/dwg-elec-001` (기본)
- [ ] `?page=3` (페이지 점프)
- [ ] `?highlight=VCB-001` (강조)
- [ ] `?from=insight&query_id=test` (브레드크럼)
- [ ] 4가지 동시 (`?page=3&highlight=VCB-001&from=insight&query_id=test`)

### 모바일
- [ ] 375px 탭바 표시
- [ ] 리스트 → 뷰어 탭 자동 활성
- [ ] 사이드 → 뷰어 page override
- [ ] 핀치줌 동작
- [ ] 더블탭 줌 안 됨

### 인사이트 통합
- [ ] 10 알람 표시
- [ ] severity 색상 (rose/amber/sky)
- [ ] [AI 물어보기] → AnswerCard 5섹션
- [ ] EvidenceList → 도면 이동 + highlight
- [ ] Breadcrumb "← 인사이트로" 복귀
- [ ] FollowUp → 근본원인 그래프
- [ ] 보고서 좌우분할 + 편집 + 확정

### 빌드
- [ ] `npm run build` 성공 (warning 0 또는 known)
- [ ] `npm run start` production 부팅
- [ ] `npx tsc --noEmit` 통과
- [ ] `npm run lint` 통과
- [ ] `vitest run` 모든 테스트 green
