# 도면지식관리 Layer 0 MVP

기존 `D:\_Project\prototype-도면지식관리\`의 페르소나 검증 결과를 받아, **검색 + PDF + 주석 + 설비 역추적** 4요소만 남긴 Layer 0 가설 검증용 프로토타입.

**세션 진입점**: 본 저장소를 여는 Claude는 먼저 [`CLAUDE.md`](./CLAUDE.md)를 읽는다. 의사결정 근거와 핸드오프 상태가 거기에 있다.

## Quick start

```bash
npm install   # 최초 1회
npm run dev   # http://localhost:3000
```

## 스택

- Next.js 14.2.15 (App Router, src/)
- TypeScript, Tailwind CSS 3
- Fuse.js (검색)
- react-pdf 10 + react-zoom-pan-pinch (뷰어/줌)
- localStorage (주석 영속, Phase 0)

## 검증 시나리오

1. "냉동기" 검색 → doc-003/004 선택 → 뷰어 표시
2. 뷰어 클릭 → 메모 저장 → 새로고침 후 핀 유지
3. 우측 탭 "설비 역추적"에 `CH-001` → 관련 도면 리스트 → 클릭 점프

상세한 컨텍스트·파일 지도·미해결 결정 사항은 `CLAUDE.md` 참조.
