# Prompts — AI 도면 분석 프롬프트 모음

이 폴더의 프롬프트는 **Claude Advisor API** (Haiku executor + Opus advisor) 기반 테스트용.

## 설계 원칙

1. **물리 도면만 3D 대상**. 논리 도면(결선도·단선도·일람표·목록)은 00-classifier에서 스킵 판정
2. **분야 라우팅**: 00에서 `route_to` 필드로 다음 전용 프롬프트 지정
3. **출력은 JSON 강제**. 자연어 설명 금지
4. **불확실성 명시**: null, `confidence` 필드 허용. 추측 금지

## 프롬프트 인덱스

| 번호 | 파일 | 역할 | 입력 |
|---|---|---|---|
| 00 | [00-standard-classifier.md](00-standard-classifier.md) | 분야·뷰타입·3D가능여부 판별 + 라우팅 | 도면 이미지 1장 |
| 10 | [10-architectural-plan.md](10-architectural-plan.md) | 건축 평면도 → 3D 재구성용 구조화 데이터 | 도면 이미지 1장 + 00 결과 |

11번대 이후(구조·기계·전기·소방 등)는 00+10 검증 후 순차 추가.

## 실행

```bash
python docs/ai-3d-builder/scripts/test_advisor.py <image_path>
```

결과는 `docs/ai-3d-builder/outputs/<timestamp>/`에 저장.
