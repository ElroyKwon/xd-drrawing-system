# PROGRESS — 실동작 빌드아웃 루프

> 매 재진입 시 `LOOP.md` → `PLAN.md` → 이 파일 순으로 읽고 이어받는다.

## 현재 상태 (2026-06-25, 세션 3 — S2 시트 레지스터 DONE)

- **단계**: **S2 DONE.** PDF 페이지 분할→시트 목록 실데이터 완전 교체 + 타이틀블록 휴리스틱(번호/제목/공종+폴백) + paperspace 다중 분리. 메타프롬프트 `prompts/03-s2-sheet-register.md` FROZEN, acceptance **C1~C8 전부 MET**(EVIDENCE 하단 S2 섹션). **커밋 `877518d`.**
- **구현 요약**: backend `sheet_meta.py`(휴리스틱 추출), `conversion.py`(PDF 페이지 분할 메타·paperspace 분리·Sheet 메타필드), `GET /api/drawings` `_with_urls`(png_url 부여·png_path 제거). 프론트 `BuildSheetsView`(실데이터 fetch+poll·정적 시드 제거·공종 필터·자연정렬), `drawingsToSheets`, `SheetDisciplineCode` string화.
- **검증**: build PASS · npm test **57** · backend pytest **15** · git diff clean · 브라우저 e2e(8p PDF→8시트 C1·EE-01-006 추출 C2·실데이터 교체 C3·공종필터 C4·시트열기 실 PDF 렌더 C6·콘솔 0 C8, 스크린샷 `evidence/s2-*.png`).
- **독립 검증팀 3렌즈 통과**: 백엔드 적대적(C1·C2·C5·C7)·프론트 비기능(C3·C4·C6·C7·C8)·Done-When 비평가(C1~C8 MET). BLOCKER 0. MAJOR 1(휴리스틱 장비태그 노이즈) + MINOR(png_path 노출·select name·stale 필터) **수리·재검증 완료**(pytest 15).
- **버그 수정**: 목록 API png_url 누락→뷰어 정적폴백(브라우저 적발) `_with_urls`로 수정.
- **남은 위험**: 멀티페이지 번들 대부분 Page N 폴백(휴리스틱 취약, freeze 수용) · 빈 paperspace=modelspace 단일(자동분할 후속) · 버전 S3 · TypeDB 직접쿼리 후속.

### 세션 3 진입점 (S2 메타프롬프트)
- `prompts/03-s2-sheet-register.md` FROZEN(공동설계 3결정: 순수레지스터+paperspace·실데이터 완전교체·타이틀블록 휴리스틱).

---

## 이전 상태 (2026-06-25, 세션 3 — S1.5 렌더 bake-off DONE)

- **단계**: **S1.5 DONE.** 2-way 렌더 bake-off(①하이브리드 래스터 PNG vs ②오픈소스 벡터 canvas2D) 풀 구현 + 승자(②벡터) 채택 전환. 메타프롬프트 `prompts/02-s1_5-render-bakeoff.md` FROZEN, acceptance **B1~B7 전부 MET**(EVIDENCE 하단 S1.5 섹션). **커밋 `2284512`.**
- **구현 요약**: backend `vector.py`(ezdxf recording 백엔드로 폭넓은 엔티티 추출→JSON: LINE/LWPOLYLINE/ARC/CIRCLE/ELLIPSE/TEXT/MTEXT/INSERT 중첩/HATCH/DIMENSION) + `/api/drawings/{id}/vector`(캐시·FileResponse·traversal 방어·PDF 400) + `dxf_path` 영속. 프론트 `VectorCanvas.tsx`(canvas2D 무손실 줌·팬·핏·레이어 토글·어두운 CAD 배경) + `SheetViewerShell` 엔진 토글(승자=벡터 기본, ①래스터 보존).
- **검증**: `npm run build` PASS · `npm test` **56 PASS** · backend `pytest` **6 PASS** · `git diff --check` clean · 브라우저 end-to-end(벡터 기본 렌더·무손실 줌·레이어 토글·래스터 토글·콘솔 0, 스크린샷 `evidence/s15-*.png`).
- **독립 검증팀 3렌즈 통과**: 백엔드 적대적(B1·B2·B4·B6 PASS)·프론트 비기능(B3·B5·B6·B7 PASS)·Done-When 비평가(B1~B7 MET, Q1~Q3 준수, narrowing 0). BLOCKER/MAJOR 0. 검증 부채 3건(B2 회귀 강화·500 경로노출·비원자 캐시) **수리·재검증 완료**.
- **bake-off 결론**: ②벡터 승자(무손실 줌+레이어 토글+벡터 인터랙션, 둘 다 비종속이라 채택이 게이트 무관). ③APS는 사용자 결정으로 **전략상 배제**(평가 안 함).
- **남은 위험**: 벡터 JSON ~8.5MB(텍스트 path 多) 최적화 후속 · 벡터 위 마크업/측정 좌표연동 = S4 · canvas2D 초대형 도면 offscreen 캐시 후속.

### 세션 3 진입점 (S1.5 메타프롬프트)
- `prompts/02-s1_5-render-bakeoff.md` FROZEN(공동설계 3결정: APS 제외 2-way·폭넓은 커버리지·승자 채택 전환).

---

## 이전 상태 (2026-06-25, 세션 2 — S1 walking skeleton 동작 완료)

- **단계**: **S1 업로드→변환→뷰어 walking skeleton 동작 완료.** 실 dwg/pdf 업로드→변환→뷰어 실 도면 렌더 end-to-end 입증. `npm run build` PASS · `npm test` **54 PASS** · backend `pytest` **2 PASS** · 브라우저 콘솔 0 · `git diff --check` clean. 메타프롬프트 A1~A8 전부 MET(증거 `EVIDENCE.md`). **미커밋.**
- **S1 구현 요약**: `backend/`(FastAPI+DrawingStore 추상화+ODA/ezdxf/PyMuPDF 변환, Study_TypeDB 이식·런타임 비의존) + 프론트(`src/api/drawings.ts`·FilesView 실업로드·MarkupCanvas 실PNG·Sheet.imageUrl).
- **독립 검증팀(2렌즈) 통과**: 적대적 엣지 + 코드리뷰가 2 BLOCKER(JSON store race 카탈로그 유실 / project_name traversal) + #7(TypeDB 미러 누락) 적발 → **전부 수정·재검증**(동시10→10/10·index valid, traversal 400, pytest 4 PASS).
- **TypeDB 활성화 완료**: typedb/typedb:3.7.3 Docker + typedb-driver 3.7.0 고정 → `store_backend=typedb`, 스키마 적용, drawing_file 실 적재·조회 확인.
- **커밋**: S1 walking skeleton=`e146fc8`. 검증 수정+TypeDB=후속 커밋.
- **남은 위험**: 나머지 2엔진(오픈소스·APS) 충실화 = S1.5. TypeDB 조회 직접 쿼리화 = S2+. paperspace 빈 DWG 시트분리 = S2.

### 세션 1 (계획 수립)
- 루프 **계획 수립 완료, S1 메타프롬프트 FROZEN**.
- **확정된 4결정**(`LOOP.md` Frozen decisions):
  1. 목표 = ACC 실기능 전체 구현(외관은 appearance-loop DONE).
  2. 백엔드 = xd 소유 독립 로컬 풀스택(Study_TypeDB 코드 이식, 런타임 비의존).
  3. 도면 렌더 = 하이브리드·오픈소스·APS 3-way bake-off 비교.
  4. 첫 슬라이스 = S1 업로드→변환→뷰어.
- **선행 근거**:
  - 현 앱 = 100% 정적 외관(의존성에 dxf/dwg/pdf/three 없음, `type=file`+FileReader 없음, viewerData 주석 "실제 드로잉/영속/연산 없음").
  - `Study_TypeDB`(`D:\_Project\Study_TypeDB`) = 동작 백엔드(FastAPI+TypeDB 3.7.3+ezdxf, 250 test PASS). 도면 API/서비스/온톨로지(`04-drawings.tql`)가 S1과 거의 일치 → **이식 소스**.
  - 변환 도구체인 검증됨: ODA File Converter(설치), ezdxf, PyMuPDF(fitz), matplotlib, Pillow.
  - 테스트 도면: `D:\_Project` 전역 dwg 822·pdf 901·dxf 25. xd 레포 내 `reference/old-prototypes/.../dwg/`에 다분야 도면.

## 다음 작업 — S1·S1.5·S2 DONE, 다음은 S3

**S1 완료**(e146fc8+f7b1a99). **S1.5 완료**(`2284512`). **S2 완료**(`877518d`, C1~C8 MET, 3렌즈 검증). 다음 진입:
- **S3 파일/폴더 관리 + 버전 + 권한**: ACC Files(카탈로그 I). `buildFilesData` 11폴더 정적 시드 → 실 폴더트리 CRUD + 업로드 + **버전 히스토리**(S2에서 연기) + 다운로드/삭제 + 폴더 권한. → `prompts/04-*.md` 공동설계·freeze 후 ai-loop.
- (참고) S2 후속 부채: 멀티페이지 타이틀블록 강추출 개선·빈 paperspace modelspace 자동분할·TypeDB 직접쿼리화 — 별도 요구 시.

### ⚙️ 다음 세션 재기동 방법 (중요)
1. **TypeDB 컨테이너**: `docker ps`로 `typedb-server`(typedb/typedb:3.7.3, 포트 1729) 확인. 없으면 `docker start typedb-server`(또는 Study_TypeDB README의 run 명령).
2. **백엔드**: `cd backend && XD_STORE=auto .venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000` (venv=64bit, typedb-driver==3.7.0 고정). `XD_STORE=json`이면 TypeDB 없이 폴백.
3. **프론트**: `npm run dev` (vite, 5173/5174). 백엔드 URL은 `src/api/drawings.ts` BACKEND_BASE=http://127.0.0.1:8000.
4. **검증**: `npm test`(57) · `cd backend && .venv/Scripts/python.exe -m pytest tests/`(15) · 브라우저 Build→파일→업로드→시트목록(실데이터)→시트 열기.
5. **주의**: 활성 `python`은 32비트(matplotlib 없음) — backend는 반드시 `backend/.venv/Scripts/python.exe`(64bit) 사용.

## 미해결 / 메모

- 외관 17화면 브라우저 스크린샷 전수 점검은 fork가 미완(audit 폴더 빈 상태). 외관 자체는 appearance-loop에서 DONE·52 test PASS·전 항목 MET로 검증됨. 사용자가 원하면 직접 재점검 가능.
- 마일스톤 체크리스트는 `PLAN.md` 참조. S1만 메타프롬프트 작성, S2~S8은 해당 마일스톤 진입 시 작성.
