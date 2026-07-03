# XD AI 사이드카(8001) 기동 — 8000과 별개 프로세스.
# 사전: backend/ai/.venv 생성 + requirements.txt 설치(README 참고).
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
& "$here/.venv/Scripts/python.exe" -m uvicorn main_ai:app --host 127.0.0.1 --port 8001
