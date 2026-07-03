# backend/ai — AI 챗 사이드카 (8001)

기존 8000 백엔드와 **완전 격리된 독립 FastAPI 프로세스**. 8000을 한 줄도 수정하지 않고,
8000의 공개 HTTP API만으로 프로젝트 실데이터를 읽어 AI 그라운딩에 쓴다.

- **격리 불변식**: `backend/ai/` 소스는 기존 backend 모듈(`store`/`routes_*`/`auth`/...)을
  import하지 않는다(테스트로 강제). 자체 venv·자체 requirements.
- **순수 클라이언트**: 8000 신규 라우트 0. 오직 GET.

## 최초 설정 (venv)

```powershell
# backend/ai 에서
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## 기동

```powershell
# backend/ai 에서 (8000과 별개 프로세스)
./run.ps1
# 또는
.venv/Scripts/python.exe -m uvicorn main_ai:app --host 127.0.0.1 --port 8001
```

- 베이스 8000 URL 재정의: 환경변수 `XD_BACKEND_BASE`(기본 `http://127.0.0.1:8000`).
- 8000이 꺼져 있어도 8001은 기동된다(lazy). `GET /api/chat/health`가 degraded로 응답.

## 확인

```powershell
# 8000 도달 + 현재 사용자
curl http://127.0.0.1:8001/api/chat/health
```

## 테스트

```powershell
# backend/ai 에서
.venv/Scripts/python.exe -m pytest tests -q
```

## 엔드포인트 (S8.0)

- `GET /` — 서비스 식별.
- `GET /api/chat/health` — 8001 상태 + 8000 도달성/현재 사용자(연결성만, 그라운딩 데이터 아님).

## 툴 (S8.0, 오직 HTTP 그라운딩)

- `tools.search(project, query)` → `GET /api/search`
- `tools.list_sheets(project, discipline=None)` → `GET /api/drawings`

전체 툴 카탈로그·대화 영속·provider·프론트 UI는 후속 스테이지(S8.1~).
