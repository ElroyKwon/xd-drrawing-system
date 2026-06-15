# 현장 도면 앱 3종 UX 벤치마크 — 우리 웹 MVP에 적용할 원칙

> **작성 시점**: 2026-04-21 (validated-watching-bunny Phase 0)
> **목적**: 사용자 지적 *"도면을 현장에서 더 많이 보기 때문에 웹 설계에도 참고 필요"*에 따른 현장 도면 앱 UX 해법 조사.
> **조사 대상**: Autodesk Fieldwire, Procore Mobile (iOS), Bluebeam Cloud iOS
> **보조 참고**: PlanGrid, PlanRadar, Dalux Field
> **조사 방법**: 공식 가이드·사용자 매뉴얼·G2/Capterra 리뷰·업계 블로그 — 2026년 4월 기준 최신

---

## 1. 현장 제약 × UX 해법 비교표

| 현장 제약 | Fieldwire (Hilti) | Procore Mobile (iOS) | Bluebeam Cloud iOS |
|---|---|---|---|
| **1. 오프라인/저대역폭** | 프로젝트 접속 시 도면·파일 자동 다운로드, 오프라인에서 주석·태스크·사진 작업 → 복귀 시 자동 큐 동기화. 버전 올려도 마크업이 자동 전이 | "한 번 본 것만 캐시". Discipline(설비/건축 등) 단위 수동 다운로드 버튼. 오프라인 작업은 재접속 시 수동 Sync로 병합 | 세션(Studio Session) 기반. 데스크톱/웹에서 만든 마크업이 모바일로 동기화. 회전된 마크업은 iOS에서 편집 불가 |
| **2. 장갑/큰 탭 타깃** | "quick taps, large touch targets for gloved hands" 명시 — P1/P2/P3 우선순위 버튼 같은 FAB 스타일 | 풀스크린 토글, 메뉴 아이콘으로 툴바 접기 → 도면 위 공간 확보 | Plus(+) FAB 하나로 마크업 진입. Tap = 기본 크기 배치, Tap&Drag = 크기 조정 (동작 이원화로 실수 줄임) |
| **3. 햇빛 가독성** | "screens readable in direct sunlight" 공식 문구. 자동 하이라이트 링크는 빨간색으로 고대비 | 명시 없음. iPad 전용 고휘도 기기 가정 | 명시 없음. PDF 흰 배경 유지 (마크업 색상만 구분) |
| **4. 저지연 터치/줌** | "fast HD plan viewer" — 타일 프리렌더로 핀치·스와이프 응답 | 탭/줌 시 툴바 자동 등장, 드로잉 간 스와이프 | Apple Pencil 지원, Tap&Drag 실시간 리사이즈 |
| **5. 회전/방향** | iPad 가로/세로 모두, 도면 간 스와이프 이동 | iPad 멀티컬럼 레이아웃(가로) vs iPhone 스택 | iOS 표준 회전 지원 |
| **6. 한 손 조작** | P1/P2/P3 + @멘션(@contractor, @plan, @priority)으로 한 손 엄지 입력 최소화 | 라쏘(lasso) 다중 선택 → 한 번에 Publish | Plus FAB + Tap 배치 (엄지 닿는 하단 집중) |
| **7. QR/NFC 빠른 진입** | 플랜의 **콜아웃(A-101, M-203 등) OCR 자동 하이퍼링크** — 도면 내부에서 즉시 점프. 외부 QR은 서드파티 | 드로잉→RFI/Observation/Punch 핀 링크 | 시트 링크는 데스크톱 Revu에서 생성 |
| **8. 음성 메모/검색** | 명시 없음 (사진·텍스트·스케치 위주) | 명시 없음 | 없음 |
| **9. 빠른 주석/원탭 마커** | 도면 위 **탭 한 번 → 태스크 핀 생성 → @멘션으로 담당·우선순위 지정** | 핀(Pin) 툴로 Punch/Observation/Photo 원탭 생성, 라쏘로 다중 일괄 발행 | Plus 탭 → 14종 마크업(사각/텍스트/화살표/구름/측정 등), Tap-to-place vs Tap-drag-to-size 이원화 |
| **10. 큰 폰트/접근성** | "stop-start rhythm of jobsite work"에 맞춘 워크플로우 | iOS 시스템 Dynamic Type 상속 | iOS 표준 상속 |
| **11. GPS/사진 첨부** | 카메라 롤·현장 촬영 사진을 태스크에 첨부, 사진 자체에 마크업 | 드로잉 핀에 사진·관찰·펀치 첨부 | 측정(Length/Area/PolyLength/Count) — 사진 첨부 제한 |
| **12. BIM/3D 연계** | 2D 평면 중심 | 도면↔RFI/Submittal/Observation 링크 | 데스크톱 Revu에 비해 축소판 |

---

## 2. 각 앱에서 우리 웹에 가져올 원칙

### Fieldwire (가장 현장 친화, 레퍼런스 최우선)
- **오프라인 자동 다운로드 + 복귀 시 자동 큐 동기화** — "사용자가 Sync 버튼 누르는 것 자체가 현장에선 부담"이라는 설계 철학
- **콜아웃 OCR 자동 하이퍼링크** — 시트 번호(A-101, M-203)를 인식해서 도면 내부 점프 링크로 변환. 우리 `doc-entity-links.json`의 "설비ID 역추적"과 정확히 같은 발상
- **탭 한 번 = 핀 생성 = @멘션 입력** — 도면 위 단일 탭으로 모든 워크플로우 진입. 현재 우리 `AnnotationLayer`가 이미 이 패턴
- **P1/P2/P3 우선순위 버튼** — 드롭다운 대신 3개 큰 버튼. 장갑 UX
- **사진 자체에도 마크업** — 핀에 첨부한 사진에도 주석 가능 (다음 단계 후보)

### Procore Mobile
- **Discipline 단위 오프라인 다운로드 선택** — 전체가 아니라 "건축/설비/전기" 같은 분류 단위 캐시. 대용량 현장에 현실적
- **라쏘 다중 선택 → 일괄 Publish** — "개인 레이어(Personal)" vs "공개 레이어(Published)" 분리. 우리도 "초안 주석 vs 공유 주석" 분리 고려
- **풀스크린 토글 + 툴바 자동 숨김/등장** — 도면이 주인공, UI는 탭 시에만 나타남
- **드로잉 → RFI/Observation/Punch 핀 링크** — 도면이 "다른 엔티티로 가는 허브"

### Bluebeam Cloud iOS
- **Plus FAB + Tap vs Tap-Drag 이원화** — 빠른 배치 vs 정밀 크기 조정을 같은 제스처 경로에서 분기
- **세션(Session) 기반 협업** — 실시간 공유 마크업 공간. Phase 2 후보
- **측정 도구(Length/Area/PolyLength/Count)** — 도면 위 거리/면적 계산. 건설·설비 현장 필수
- **Apple Pencil/스타일러스 지원** — 자유 주석은 손글씨가 빠름

---

## 3. 우리 웹 MVP 도입 후보 상위 원칙 (Next.js/PWA 범위 × 도면 지식관리 중요도)

1. **PWA 오프라인 셸 + IndexedDB에 PDF/PNG 저장** — Cache Storage는 정적 자원, IndexedDB는 도면 바이너리·주석 데이터. 현장 Wi-Fi 단절 대응의 기본기. (브라우저당 최대 60% 디스크 할당 가능)
2. **"한 번 본 도면은 캐시" + "복귀 시 자동 큐 플러시"** — Procore의 보수적 캐시 + Fieldwire의 자동 동기화를 결합. 우리 `annotations-store.ts`를 오프라인 큐로 확장
3. **도면 위 단일 탭 = 핀 생성 (현재 유지 강화)** — 추가로 **탭 & 드래그 = 영역 주석**으로 Bluebeam식 제스처 이원화
4. **장갑 대응 탭 타깃 최소 44×44px(iOS HIG) / 권장 48×48px(Material)** — 주석 핀·탭 아이콘·우선순위 버튼 전수 점검. 현재 8px 핀은 현장 부적합 — "시각적 작은 핀 + 히트박스 큰 영역" 패턴
5. **콜아웃 자동 하이퍼링크 (OCR 후일, 지금은 수동)** — `documents.json`에 `callout_refs: ["A-101", "M-203"]` 필드 추가하고 PDF 오버레이로 클릭 영역 생성. Fieldwire의 킬러 기능을 수동 메타데이터로 선이식
6. **Discipline 필터 칩(건축/설비/전기/소방)** — 좌측 도면 리스트 상단. 오프라인 다운로드 단위의 예비 작업
7. **다크 모드 토글 + 고대비 테마** — 시스템 설정 추종(`prefers-color-scheme`) + 헤더에 수동 토글. 햇빛 환경은 실측상 고대비 다크가 더 잘 읽히는 경우 다수
8. **FAB(Floating Action Button) — 한 손 엄지 Zone** — 화면 우하단 고정. "+주석", "+측정", "음성 메모"(Phase 2). Bluebeam Plus 패턴
9. **썸(thumb) 존 하단 툴바** — 도면 뷰어 하단에 자주 쓰는 3~4개 액션(핀/역추적/공유/전체화면). 상단 영역은 보기만
10. **풀스크린 모드(툴바 자동 숨김 + 탭 시 등장)** — `visibility: hidden` 타이머 + 도면 탭 시 복귀. Procore 패턴
11. **QR 코드로 설비ID 진입 (서버 엔드포인트 `/e/[equipmentId]`)** — 현장 스티커 QR 스캔 → `EntityToDocs` 결과 화면 직행. 서비스 1의 "설비 역추적"과 정확히 맞물림
12. **우선순위 P1/P2/P3 3버튼 + @멘션 자동완성** — 드롭다운 대신 큰 버튼. 장갑 + 빠른 입력 양립

### 보수적 제외 (웹 MVP 범위 밖)
- 음성 메모: Web Speech API로 가능하나 한국어 인식·노이즈·권한 UX 부담 → Phase 2
- Apple Pencil 압력 감지: PointerEvents로 기본은 가능하나 JS PDF 위에서 지연 문제 → Phase 2
- BIM 3D: 별도 트랙(AI 3D Builder)에 존재
- 실시간 협업 세션: Yjs/Liveblocks 필요 → Phase 2

---

## 4. 한국 건설·OT 현장 맥락 보강

- **청주/여수 같은 플랜트 현장은 Wi-Fi 음영이 광범위** → 오프라인 퍼스트가 "있으면 좋은 것"이 아니라 **기본 전제**. Layer 0 가설 검증 시점부터 IndexedDB 캐시를 쓰는 게 낫다
- **안전모 + 목장갑이 디폴트** → iOS 44px 가이드보다 여유 있게 48~56px, 탭 간격 최소 8px
- **설비 태그(CH-001, VCB-001)가 이미 우리 데이터에 있음** → Fieldwire 콜아웃 하이퍼링크를 "설비 태그 자동 링크"로 선이식하면 한국 플랜트 문법과 정확히 일치
- **감독관/작업자/설계자 3자가 같은 도면을 봄** → Procore의 "Personal vs Published" 레이어 분리가 현실적. 초안 주석은 본인만, 공유는 Publish 액션으로

---

## 출처

- [Fieldwire iPad 앱 공식](https://www.fieldwire.com/construction-apps/ipad/)
- [Fieldwire Plan 하이퍼링크 가이드](https://help.fieldwire.com/hc/en-us/articles/360000488886-Introduction-to-Plan-Sheet-Naming-and-Hyperlinks)
- [Fieldwire 태스크 사용 가이드](https://help.fieldwire.com/hc/en-us/articles/360017420132-How-to-use-Tasks-on-the-Fieldwire-Mobile-Apps-iOS-and-Android)
- [Procore iOS 드로잉 마크업](https://support.procore.com/procore-mobile-ios/user-guide/drawings-ios/tutorials/mark-up-a-drawing-ios)
- [Procore iOS 오프라인 드로잉 동기화](https://support.procore.com/procore-mobile-ios/user-guide/drawings-ios/tutorials/sync-and-download-drawings-ios)
- [Procore 오프라인 모드 FAQ](https://support.procore.com/faq/can-i-use-procores-mobile-application-offline)
- [Bluebeam Cloud iOS 마크업 생성/편집](https://support.bluebeam.com/bluebeam-cloud/how-to/create-and-edit-markups-ios.html)
- [Bluebeam Revu for iPad EOL 공지](https://www.bluebeam.com/revu-ipad-eol/)
- [NN/G 터치 타깃 사이즈 가이드](https://www.nngroup.com/articles/touch-target-size/)
- [Industrial UX: Sunlight Susceptible Screens (Medium)](https://medium.com/@callumjcoe/industrial-ux-sunlight-susceptible-screens-2e52b1d9706b)
- [web.dev — PWA 오프라인 데이터 전략](https://web.dev/learn/pwa/offline-data)
- [Addy Osmani — PWA 오프라인 스토리지](https://medium.com/dev-channel/offline-storage-for-progressive-web-apps-70d52695513c)
