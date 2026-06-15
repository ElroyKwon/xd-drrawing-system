# GEM Web UI - FastAPI + WebSocket

## 🚀 Features

### ✨ 완전히 새로운 FastAPI 기반 실시간 채팅 시스템

Gradio를 완전히 제거하고 **FastAPI + WebSocket**으로 새로 구축했습니다!

#### 주요 기능:

- ✅ **실시간 WebSocket 통신** - ChatGPT처럼 글자가 타이핑되듯 나타남
- ✅ **완벽한 다크 테마** - CSS 100% 커스터마이징
- ✅ **실시간 로그 스트리밍** - 분석 진행 상황 실시간 확인
- ✅ **드래그 앤 드롭 파일 업로드** - 직관적인 UI
- ✅ **빠른 성능** - Gradio보다 훨씬 빠름
- ✅ **완전한 제어** - 모든 UI 요소를 자유롭게 커스터마이징

---

## 📂 파일 구조

```
GEM/
├── main.py                 # FastAPI 백엔드 (WebSocket)
├── static/
│   ├── index.html         # 프론트엔드 HTML
│   ├── style.css          # 완벽한 다크 테마 CSS
│   └── app.js             # WebSocket 클라이언트
├── uploads/               # 업로드된 CSV 파일
├── requirements.txt       # FastAPI, uvicorn, websockets
└── start_web_ui.bat      # 실행 스크립트
```

---

## 🎨 UI 스크린샷

### 다크 테마 디자인:
- **배경**: `#0a0e27` (다크 네이비)
- **챗봇**: `#1a1f3a` (어두운 패널)
- **입력창**: `#2a2a2a` (검은색) + 포커스 시 주황색 테두리
- **버튼**: `#f97316` (주황색) + 호버 효과
- **로그**: `#0d1117` (터미널 스타일) + 파란색 텍스트

---

## 🛠️ 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

주요 패키지:
- `fastapi==0.109.0` - 웹 프레임워크
- `uvicorn[standard]==0.27.0` - ASGI 서버
- `websockets==12.0` - WebSocket 지원
- `python-multipart==0.0.6` - 파일 업로드

### 2. 서버 실행

#### Windows:
```bash
start_web_ui.bat
```

#### Linux/Mac:
```bash
python main.py
```

#### 수동 실행 (개발용):
```bash
uvicorn main:app --host 0.0.0.0 --port 7860 --reload
```

### 3. 브라우저에서 접속

```
http://localhost:7860
```

---

## 🔥 실시간 기능

### WebSocket 메시지 타입:

#### 클라이언트 → 서버:
```json
{
  "type": "chat",
  "content": "배터리 분석 시작해줘"
}
```

```json
{
  "type": "file_uploaded",
  "filename": "battery_data.csv",
  "path": "/uploads/battery_data.csv"
}
```

#### 서버 → 클라이언트:
```json
{
  "type": "bot_message",
  "content": "Phase 1 시작합니다..."
}
```

```json
{
  "type": "bot_message_start"
}
```

```json
{
  "type": "bot_message_chunk",
  "content": "분석"
}
```

```json
{
  "type": "bot_message_end",
  "full_content": "분석이 완료되었습니다."
}
```

```json
{
  "type": "log",
  "content": "[12:34:56] Phase 1 완료"
}
```

---

## 📊 Gradio vs FastAPI 비교

| 기능 | Gradio | FastAPI + WebSocket |
|------|--------|---------------------|
| CSS 커스터마이징 | ❌ 어려움 (강제 오버라이드 필요) | ✅ 완전 자유 |
| 실시간 스트리밍 | ❌ 제한적 | ✅ 완벽 지원 |
| 성능 | ⚠️ 보통 | ✅ 빠름 |
| 다크테마 | ❌ 복잡함 | ✅ 쉬움 |
| 유지보수 | ❌ 어려움 | ✅ 쉬움 |
| 배포 | ✅ 간단 | ✅ 간단 |
| 학습 곡선 | ✅ 낮음 | ⚠️ 중간 |

---

## 🎯 사용 시나리오

### 1. CSV 파일 업로드
- 드래그 앤 드롭 또는 클릭하여 업로드
- 실시간으로 서버에 전송
- WebSocket으로 업로드 완료 알림

### 2. 배터리 프로파일 선택
- AI 챗봇이 프로파일 목록 제시
- 사용자가 숫자 또는 이름으로 선택
- 커스텀 프로파일 직접 입력 가능

### 3. Phase 1-3 자동 실행
- **Phase 1**: CSV → Parquet 변환
- **Phase 2**: 4가지 안전성 검증 (열적, SPC, 무결성, 상관성)
- **Phase 3**: AI 인사이트 생성 (Ollama)

### 4. 실시간 로그
- 모든 작업 진행 상황 실시간 표시
- 터미널 스타일 UI
- 자동 스크롤

### 5. HTML 리포트 다운로드
- Phase 3 완료 후 다운로드 가능
- `/api/download/{run_id}` 엔드포인트

---

## 🐛 문제 해결

### WebSocket 연결 실패
```
WebSocket 연결 종료됨. 재연결 시도 중...
```
→ 서버가 실행 중인지 확인 (3초 후 자동 재연결)

### 파일 업로드 실패
```
CSV 파일만 업로드 가능합니다.
```
→ `.csv` 확장자 파일만 업로드

### Ollama 서버 없음
```
[WARNING] Ollama server not running
```
→ Phase 3 인사이트 생성 시 Ollama 필요
```bash
ollama serve
ollama pull qwen2.5:32b
```

---

## 🔧 개발자 가이드

### API 엔드포인트

#### `GET /`
- 메인 HTML 페이지

#### `POST /api/upload`
- CSV 파일 업로드
- Form-data: `file`
- 응답: `{status, filename, path, size}`

#### `GET /api/download/{run_id}`
- HTML 리포트 다운로드

#### `WS /ws`
- WebSocket 연결
- 실시간 양방향 통신

### 세션 관리

각 WebSocket 연결마다 `SessionState` 객체 생성:
```python
class SessionState:
    uploaded_file: str
    run_id: str
    phase: int
    battery_profile: str
    log_buffer: list
```

---

## 📝 TODO

- [ ] 사용자 인증 추가
- [ ] 여러 파일 동시 분석
- [ ] 실시간 차트/그래프
- [ ] 모바일 반응형 개선
- [ ] Docker 이미지 제공

---

## 🎉 결론

Gradio의 한계를 극복하고 **FastAPI + WebSocket**으로 완전히 새롭게 구축했습니다!

- ✅ CSS 자유자재
- ✅ 실시간 스트리밍
- ✅ 완벽한 다크 테마
- ✅ 빠른 성능

**이제 더 이상 CSS와 싸우지 않아도 됩니다!** 🎊
