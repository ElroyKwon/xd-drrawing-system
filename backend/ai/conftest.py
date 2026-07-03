# backend/ai를 sys.path에 넣어 flat import(client·tools·main_ai·health)를 보장.
# 격리: 기존 backend/ 는 경로에 넣지 않는다.
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
