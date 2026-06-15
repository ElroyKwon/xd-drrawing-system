# W4 — 통합·시연·인터뷰 (~32h)

> **선행**: W3 전체 완료
> **목표**: 인터뷰 4명 × 90분 진행 + 결과 종합 + 8주 백로그 후보

---

## W4-T1. 시연 대본 3종 + 녹화 (~6h)

### 선행
W3 전체

### 신규 파일
- `docs/upgrade-plan/verification.md` 보강 (시연 5/10/20분 단계별 — 이미 1차 작성됨, 실제 시간 측정 후 미세 조정)
- `docs/upgrade-plan/recordings/W4-demo-5min.mp4`
- `docs/upgrade-plan/recordings/W4-demo-10min.mp4`
- `docs/upgrade-plan/recordings/W4-demo-20min.mp4`

### 녹화 도구
- OBS Studio 또는 Loom (W1-T6에서 설치 완료 가정)
- 1920×1080 + 한국어 마이크
- 화면 + 시스템 사운드 + 마이크 동시

### 녹화 절차
1. dev 서버 부팅 (`npm run dev`)
2. 18 PDF 시드 확인
3. mock 모드 LLM (안정적 시연용)
4. Chrome 시크릿 창 (LS 깨끗) → 시연 시작
5. 5분 → 10분 → 20분 순서로 녹화 (10분은 5분 시나리오 포함, 20분은 10분 포함)

### 완료 기준
1. 3 mp4 파일 정상 재생
2. 5분 시나리오가 5분 ±30초 안에 끝남
3. 각 시나리오의 모든 클릭 단계가 verification.md와 일치

---

## W4-T2. 통합 회귀 (~8h)

### 선행
W3 전체

### 신규 파일
- `docs/upgrade-plan/regression-checklist-W4.md` (체크리스트 30~40 항목)

### 체크리스트 영역
1. **보존 6항목 회귀** (각 1회)
   - PDF→이미지 fallback (실 PDF + 더미 PDF + 이미지 only 도면)
   - 핀 생성·편집·삭제·LS 영속
   - hydrated 플래그 (LS 비어있을 때 빈 배열 안 덮어쓰기)
   - doubleClick:disabled (더블클릭 줌 차단)
   - PdfViewer key 패턴 (문서 전환 시 totalPages 잔존 X)
   - data-loader toUpperCase 정규화

2. **18 PDF 모두 렌더**
   - 전기 9 / 통신 5 / 건축·기계·소방 4

3. **LLM 양 모드 동작**
   - mock 모드: SSE 스트리밍, evidence 정확
   - live 모드: Anthropic API 응답 + evidence 강제

4. **URL 규약 모든 파라미터 조합**
   - `/drawings/dwg-elec-001` (기본)
   - `?page=3` (페이지 점프)
   - `?highlight=VCB-001` (강조)
   - `?from=insight&query_id=test` (브레드크럼)
   - 4가지 조합

5. **모바일 회귀**
   - 375px 탭바 [리스트|뷰어|사이드]
   - 핀치줌 동작
   - 더블탭 줌 안 됨

6. **vitest 단위**
   - url-builder 5 케이스
   - regression-annotations 5 케이스

7. **빌드**
   - `npm run build` 성공
   - `npm run start`로 production 모드 부팅 확인

### 완료 기준
1. 30~40개 체크 100% green
2. P1 버그 0건 (P2 이하 백로그에 기록)
3. mp4 3종 + verification.md 보강 완료

---

## W4-T3. 인터뷰 4세션 (~12h)

### 선행
W4-T2 완료 + W1-T6의 캘린더 확정

### 일정
- 화 오전 (영업 1)
- 화 오후 (영업 2)
- 수 오전 (운영자 1)
- 수 오후 (운영자 2)

각 90분: 시연 20분 (스펙 §14.10 + §15.11 20분판) + 질문지 §10 50분 + 마무리 20분

### 산출물
- `docs/upgrade-plan/interviews/W4-results-{role-name}.md` × 4건
- 각 세션 화면+음성 mp4 (선택, 동의 받은 경우만)

### 결과 .md 형식
```markdown
# W4 인터뷰 결과 — {역할} {이름}
- 일시: 2026-XX-XX HH:MM
- 시연 통과: ☐ 5분 ☐ 10분 ☐ 20분
- 리커트 평가 (1~5):
  - 빠르게 찾았나: ☐
  - 신뢰할 수 있었나: ☐
  - 매뉴얼 없이 사용: ☐
  - 모바일 경험: ☐
  - 매일 쓸 것 같은가: ☐
- 정성 답변:
  - 가장 인상적: ...
  - 없으면 안 되는: ...
  - 빠져서 아쉬운: ...
- 가격 감지: ...
- 발견 버그/이슈: ...
- 후속 ISS 후보: ...
```

### 완료 기준
1. 4세션 진행 완료
2. 4건 결과 .md 작성
3. P1 버그 발견 시 즉시 fix → 다음 세션 전 반영

---

## W4-T4. 결과 종합 + 8주 백로그 (~6h)

### 선행
W4-T3

### 신규 파일
- `docs/upgrade-plan/post-W4-summary.md`

### 종합 내용
1. **공통 인사이트**: 4명 답변에서 반복된 키워드 (예: "주석 공유 필요", "권한 부족", "엑셀로 export")
2. **가장 강한 가치**: 시연 후 4명 모두 동의한 1~2개 기능
3. **가장 약한 가치**: 4명 중 2+명이 미온적이었던 기능
4. **가격 감지 종합**: 4명의 월/년 지불 의사 평균
5. **8주차 1순위 백로그**: F-006~F-011 / G-006~G-010 중 어느 것을 8주차에
6. **차후 인터뷰 대상**: 추가 검증 필요 페르소나

### 완료 기준
1. post-W4-summary.md 1장 (5~10페이지)
2. 사용자 검토 후 8주차 plan 1장 (이건 별도 plan 모드)
3. STATUS.md 모든 W4 작업 ✅
