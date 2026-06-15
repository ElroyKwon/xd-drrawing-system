# 채널별 필수 태그 전체 리스트

**작성일:** 2025-12-23
**채널 수:** 6개 (BSC_CH_01 ~ BSC_CH_06)
**총 태그 수:** 4,860개
**채널당 평균:** 810개

---

## 시스템 구조

- **채널(CH):** BSC_CH_01 ~ BSC_CH_06 (6개)
- **뱅크(BANK):** BANK_01 ~ BANK_04 (각 채널당 4개)
  - BANK_01, BANK_03: RACK 14개
  - BANK_02, BANK_04: RACK 13개
- **필수 패턴:** 15개 (온도 6 + 전압 6 + 전류/상태 3)

---

## 필수 태그 패턴 (15개)

**온도 관련 (6개):**

1. `MOD_AVG_TEMP` - 평균 온도
2. `MOD_MAX_TEMP` - 최고 온도
3. `MOD_MIN_TEMP` - 최저 온도
4. `MOD_MIN_TEMP_NO` - 최저 온도 위치
5. `MAX_DEVI_TEMP` - 온도 편차
6. `MOD_MAX_TEMP_NO` - 최고 온도 위치

**전압 관련 (6개):**

7. `CELL_SUM_V` - 셀 총 전압
8. `CELL_AVG_V` - 셀 평균 전압
9. `CELL_MAX_V` - 셀 최고 전압
10. `CELL_MIN_V` - 셀 최저 전압
11. `CELL_MAX_V_MOD_NO` - 최고 전압 모듈 위치
12. `CELL_MIN_V_MOD_NO` - 최저 전압 모듈 위치

**전류 및 상태 (3개):**

13. `CELL_DC_TOTAL_A` - 총 전류
14. `SOC` - 충전 상태
15. `SOH` - 배터리 건강도

---

## 생성된 파일

각 채널별로 전체 태그가 포함된 텍스트 파일이 생성됩니다:

- `GEM/data/bsc_ch_01_tags.txt` - 810개 태그
- `GEM/data/bsc_ch_02_tags.txt` - 810개 태그
- `GEM/data/bsc_ch_03_tags.txt` - 810개 태그
- `GEM/data/bsc_ch_04_tags.txt` - 810개 태그
- `GEM/data/bsc_ch_05_tags.txt` - 810개 태그
- `GEM/data/bsc_ch_06_tags.txt` - 810개 태그

- `GEM/data/all_channels_tags.json` - 전체 통합 JSON (4,860개)

---

**문서 버전:** 2.0.0
**생성 스크립트:** `GEM/tests/create_channel_tag_lists.py`
