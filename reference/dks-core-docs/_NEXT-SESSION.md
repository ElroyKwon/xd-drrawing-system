---
tags:
  - next-session
  - phase1
  - stage6
  - 진입점
  - 모델결정필요
created: 2026-05-03
---

# 다음 세션 진입 노트 (Stage 6 풀 실행 모델 결정 필요)

> 본 파일은 다음 세션 첫 작업의 빠른 진입 노트.
> 상세는 `_Python_code/SESSION-CLOSE-20260503h.md`.

---

## 현재 위치

```
Phase 1 진행:
  Stage 0.5 ✅ → Stage 1 ✅ → Stage 2 ✅ → Stage 3A ✅ → Stage 3B ✅
  → Stage 4 ✅ + 4-E ✅
  → Stage 5 ✅ + 5-E ✅ (X-P1-003/004/005 풀 방어, regression 96 PASS)
  → Stage 6 코드 ✅ (4개 신규) + 스모크 A/A2/B 완료
       └─ ★ mini 정보 손실 22건 + invariant 버그 + 아키텍처 의문 발견
       └─ 풀 실행 모델 결정 보류
  → Stage 7 generic 골격 ✅ + D-P1-21 추론 검증 설계 메모 ✅
  → Stage 6 풀 ⏳ (모델 결정 후 진입)
  → Stage 6-E ⏳
  → Stage 7 본 ⏳
```

---

## 복귀 첫 명령 (그대로 입력 가능)

```
다음 세션 SESSION-CLOSE-20260503h.md 읽고 진입. 첫 작업은 invariant 버그 수정 (필수, 모델 선택 무관).
그 후 풀 실행 모델 결정.

옵션:
  4. Sonnet × 40 풀 ($37.8 / 42분) — 가장 빠름, 옵션 A 무손실 입증
  2변형. mini × 2 + overhead 감소 재설계 ($7~10 / 16분) — 1~2h 재설계 + 옵션 B 재검증
  5신규. per-entity atomic 재설계 ($13~16 / 23분) — 본질 패턴 정착, 2~3h 재설계

내 결정: <옵션 번호>
```

---

## 다음 세션 작업 순서

### 공통 (모델 무관 필수)

1. **invariant validate_chunk_output 버그 수정**
   - 현 상태: `chunk_results.cr["parsed"].get("_chunk_skeleton")`이 항상 None → fallback empty → coverage=1.0 false PASS
   - 수정: chunk_jobs[i]["user_inputs"]를 chunk_results 매핑으로 직접 전달
   - 검증: 옵션 B 산출물(`stage6_modular_smoke_B_mini/openai/discipline_elec_sld/chunk_01`)로 손실 22건 정상 BLOCK 떠야

2. (선택) mini namespace 혼동 prompt 보강 — `core:ControlPanel` 같은 외부 IRI 변형 금지 강조

### 옵션 4 선택 시 (Sonnet × 40 풀)

```
3. Sonnet 풀 실행 (1656 entity, 9개 모듈, 42 chunks, $37.8 / 42분)
4. Stage 6-E OWL 빌드 (모듈러 v3 + project_imports_v3 + HermiT)
5. Stage 7 코드 검증 (CQ DL Query + invariant 7종)
6. Stage 7 추론 검증 본 설계·구현 (D-P1-21 design memo 기반)
   - spot-check / cross-property / Sonnet+Opus 합의 측정
7. 박제 + 메모리 + CONCEPT-MAP
```

### 옵션 2 변형 또는 5 선택 시 (재설계)

```
3. prompt overhead 감소
   - cross_module_individual_index를 모듈 관련 tag만 필터
   - decision_catalog 본 stage 항목만
   - external IRIs 자주 참조분만
   - 목표: 108K → 30~40K
4. (옵션 5만) stage6_instances.py 재구조화
   - entity loop + 즉시 검증 + 재시도 메커니즘
   - 코드가 종합/분류 책임 (naming/novel/absorbed)
5. 옵션 B 재검증 (정보 손실 0% 확인)
6. 풀 실행
7. Stage 6-E + Stage 7 (옵션 4와 동일)
```

---

## 핵심 입력 경로 (확정)

```
package    = projects/청주사업장신축/phase1/run_20260502/stage0_5/project_integrated_package.yaml
stage1     = projects/청주사업장신축/phase1/run_20260502/stage1/openai/stage1_domain_definition.yaml
stage4     = projects/청주사업장신축/phase1/run_20260503/stage4_modular_F_FULL/anthropic/
stage5     = projects/청주사업장신축/phase1/run_20260503/stage5_modular_F_FULL/anthropic/
stage5_owl = projects/청주사업장신축/phase1/run_20260503/stage5e_owl_v3_3/
drawings   = projects/청주사업장신축/건축도면
output     = projects/청주사업장신축/phase1/run_20260503/stage6_modular_FULL/{provider}/
```

청주 entity_details 분포 (실측):
- arch 183 / struct 189 / civil 173 / mech 94 / elec_sld 78 / elec 283 / telecom 209 / fp_mech 293 / fp_elec 154
- **총 1,656 entities**

---

## 비용 + 안정성 비교 표 (참고)

| 옵션 | 모델 | chunk | 비용 | 시간 | 안정성 |
|---|---|---:|---:|:---:|:---:|
| 1 | mini | 1 | $47.7 | 23분 | ★★★★★ |
| 2 | mini | 2 | $25.3 | 16분 | ★★★★ |
| **2변형** | **mini + overhead↓** | 2 | **$7~10** | 16분 | ★★★★ (재설계 후 재검증) |
| 3a | GPT-5.5 대형 | 10 | $116 | 12분 | ★★★★ (탈락) |
| 3b | mini | 10 | $7.5 | 12분 | ★★ (손실 위험) |
| **4** | **Sonnet** | 40 | **$37.8** | 42분 | ★★★★★ (입증) |
| 4b | Sonnet | 10 | $77.7 | 50분+ | ★★★★★ (비추) |

---

## 핵심 진입 명령

```bash
cd "G:/내 드라이브/_Obsidian/지식관리/00. XD-AI 플랫폼/데이터 지식 스튜디오/_Python_code"

# 본 세션 종료 + 발견된 버그/문제
cat SESSION-CLOSE-20260503h.md

# 추론 검증 설계 메모 (Stage 7 본 작성 시 참조)
cat ../docs-표준-typedb-v1/D-P1-21-stage7-validation-design-memo.md

# Stage 6 신규 코드
ls phase1/stage6_instances.py phase1/stage6e_owl_builder.py phase1/skeleton/stage6_instance_skeleton.py

# 옵션 B 손실 사례 (invariant 수정 후 검증용)
ls projects/청주사업장신축/phase1/run_20260503/stage6_modular_smoke_B_mini/openai/discipline_elec_sld/

# 회귀 96 PASS 확인 (Stage 5 회귀 유지 확인)
python -m pytest tests/phase1/regression/
```

---

## Stage 7 추론 검증 설계 (D-P1-21 design memo)

> 사용자 강조 (2026-05-03h): "코드 검증 + 제대로 추론이 되는지도 검증해야 한다"

| 갈래 | 무엇을 보는가 | 도구 |
|---|---|---|
| 1. 코드 검증 | 구조 형식상 올바름 | HermiT + invariant + DL Query |
| 2. 추론 검증 | 도메인 의미상 정답 | LLM judge (Sonnet/Opus spot-check + 합의) |

상세: `docs-표준-typedb-v1/D-P1-21-stage7-validation-design-memo.md`
본 작성 시점: Stage 6 풀 실행 + Stage 6-E 완료 후

---

## 핵심 박제 일체

- `_Python_code/SESSION-CLOSE-20260503h.md` — **본 세션 종료**
- `docs-표준-typedb-v1/D-P1-21-stage7-validation-design-memo.md` — **★ 검증 설계**
- `_Python_code/phase1/stage6_instances.py` (메인)
- `_Python_code/phase1/stage6e_owl_builder.py` (OWL 빌더)
- `_Python_code/phase1/stage7_validation.py` (검증 generic 골격)
- `_Python_code/phase1/skeleton/stage6_instance_skeleton.py`
- `_Python_code/prompts/phase1/stage_6_instances.yaml` (신 프롬프트)
- 옛 prompt 백업 (`.legacy_v1_20260503g`)
- 메모리: `project_phase1_stage6_smoke_complete_20260503h.md`

---

수고 많으셨습니다. **Stage 6 코드 작성 + 스모크 3회 데이터 확보 완료**.
다음 세션 첫 작업은 **invariant 버그 수정 → 모델 결정 → 풀 실행**.
