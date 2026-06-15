"""ask_human — 에이전트가 사용자에게 질문. 현재는 stdin 기반.

주의: max 3회 초과 호출 금지 (시스템 프롬프트에 명시).
"""
import sys
from .base import now_iso

SCHEMA = {
    "name": "ask_human",
    "description": (
        "애매한 결정에 대해 사람에게 질문한다. "
        "context 파라미터에 배경을 담아 전달. 사용 3회 초과 금지. "
        "가능하면 log_decision 으로 자율 판단 선호."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
            "context": {
                "type": "object",
                "description": "사용자가 결정을 내리는 데 필요한 배경 정보",
            },
        },
        "required": ["question"],
    },
}


def execute(tool_input, context=None):
    question = tool_input.get("question", "(질문 없음)")
    ctx_info = tool_input.get("context") or {}

    # auto mode 등에서 stdin 비대화면 AUTO_ASK_HUMAN 환경변수로 기본 응답 지정
    import os
    auto = os.environ.get("AUTO_ASK_HUMAN")
    if auto is not None:
        return {
            "answered_by": "auto_env",
            "question": question,
            "answer": auto,
            "ts": now_iso(),
        }

    print("\n" + "=" * 60, flush=True, file=sys.stderr)
    print("[ask_human] 에이전트가 질문합니다:", flush=True, file=sys.stderr)
    print(f"  Q: {question}", flush=True, file=sys.stderr)
    if ctx_info:
        print(f"  context: {ctx_info}", flush=True, file=sys.stderr)
    print("=" * 60, flush=True, file=sys.stderr)
    try:
        answer = input("답변> ").strip()
    except EOFError:
        answer = "(stdin closed)"
    return {
        "answered_by": "stdin",
        "question": question,
        "answer": answer,
        "ts": now_iso(),
    }
