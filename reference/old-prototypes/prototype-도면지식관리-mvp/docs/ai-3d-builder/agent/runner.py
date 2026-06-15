"""2D→3D Auto Modeling Agent — Runner.

Anthropic Claude API (claude-opus-4-7) + 10 custom tools.

사용:
  python agent/runner.py --goal "..." --session-id smoke_001 --max-steps 5
  python agent/runner.py --goal "build full 3D" --session-id full_001 --max-steps 50 --budget-tokens 1500000
  python agent/runner.py --smoke   # 최소 smoke (tool 호출 2~3회로 기능 검증)

환경변수:
  ANTHROPIC_API_KEY 또는 api_keys.json 의 "anthropic" 키
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# agent 패키지 import path 설정
THIS = Path(__file__).resolve()
AGENT_DIR = THIS.parent
DOCS_DIR = AGENT_DIR.parent
ROOT = DOCS_DIR.parent.parent
sys.path.insert(0, str(DOCS_DIR))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent.tools import get_schemas, dispatch as dispatch_tool
from agent.tools.base import load_keys, now_iso

try:
    import anthropic
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "anthropic"])
    import anthropic


DEFAULT_MODEL = "claude-opus-4-7"
FALLBACK_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT_PATH = AGENT_DIR / "system_prompt.md"


def resolve_api_key():
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k
    try:
        return load_keys()["anthropic"]
    except Exception:
        try:
            return load_keys()["claude"]
        except Exception:
            raise RuntimeError("ANTHROPIC_API_KEY 또는 api_keys.json.anthropic 필요")


def jsonify(obj):
    """tool result 를 JSON 문자열로 직렬화 (non-serializable 은 repr)."""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except Exception:
        return json.dumps({"_repr": repr(obj)})


def run_agent(goal, session_id, max_steps=50, budget_tokens=1_500_000,
              model=DEFAULT_MODEL, dry_run=False):
    session_dir = AGENT_DIR / "runs" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    messages_path = session_dir / "messages.jsonl"
    usage_path = session_dir / "usage.jsonl"
    summary_path = session_dir / "summary.md"

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tools = get_schemas()

    print(f"[runner] session={session_id}  model={model}  max_steps={max_steps}")
    print(f"[runner] tools={[t['name'] for t in tools]}")
    print(f"[runner] goal: {goal[:120]}")
    if dry_run:
        print("[runner] dry_run — 실제 호출 없이 구성만 검증")
        return {"dry_run": True, "tools": [t["name"] for t in tools]}

    client = anthropic.Anthropic(api_key=resolve_api_key())
    messages = [{"role": "user", "content": goal}]
    total_in = 0
    total_out = 0
    tool_calls = 0
    step_records = []

    def log_msg(role, content):
        with messages_path.open("a", encoding="utf-8") as f:
            # content 는 list 또는 str
            f.write(json.dumps({
                "ts": now_iso(), "role": role, "content": content,
            }, ensure_ascii=False, default=str) + "\n")

    def log_usage(step, usage):
        with usage_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": now_iso(), "step": step, "usage": usage,
            }, ensure_ascii=False) + "\n")

    log_msg("user", goal)

    stop_reason = None
    for step in range(1, max_steps + 1):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=8000,
                system=[
                    {"type": "text", "text": system_prompt,
                     "cache_control": {"type": "ephemeral"}}
                ],
                tools=tools,
                messages=messages,
            )
        except anthropic.APIStatusError as e:
            err = {"step": step, "api_error": str(e)}
            step_records.append(err)
            print(f"[runner] API error step {step}: {e}", file=sys.stderr)
            stop_reason = "api_error"
            break

        usage = {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
            "cache_read_input_tokens": getattr(resp.usage, "cache_read_input_tokens", 0),
            "cache_creation_input_tokens": getattr(resp.usage, "cache_creation_input_tokens", 0),
        }
        total_in += usage["input_tokens"]
        total_out += usage["output_tokens"]
        log_usage(step, usage)

        assistant_blocks_serializable = []
        tool_uses = []
        text_chunks = []
        for block in resp.content:
            if block.type == "text":
                text_chunks.append(block.text)
                assistant_blocks_serializable.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                tool_uses.append(block)
                assistant_blocks_serializable.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
        log_msg("assistant", assistant_blocks_serializable)

        if text_chunks:
            print(f"[step {step}] {' '.join(text_chunks)[:200]}")

        # assistant message 를 message history 에 추가
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn" and not tool_uses:
            stop_reason = "end_turn"
            break

        # tool_use 처리
        if tool_uses:
            tool_results_block = []
            for tu in tool_uses:
                tool_calls += 1
                print(f"  > tool_use #{tool_calls}: {tu.name}  input_keys={list(tu.input.keys())}")
                try:
                    result = dispatch_tool(
                        tu.name, tu.input,
                        context={"session_id": session_id},
                    )
                except Exception as e:
                    result = {"error": f"dispatch_exception: {type(e).__name__}: {e}"}
                result_str = jsonify(result)
                # 너무 긴 결과 잘라서 로그 (원본은 파일에 남음)
                preview = result_str[:400] + ("…" if len(result_str) > 400 else "")
                print(f"    result: {preview}")
                tool_results_block.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": result_str,
                })
            messages.append({"role": "user", "content": tool_results_block})
            log_msg("user_tool_result", tool_results_block)

        if total_in + total_out > budget_tokens:
            stop_reason = "budget_exceeded"
            print(f"[runner] budget exceeded at step {step}", file=sys.stderr)
            break

    if stop_reason is None:
        stop_reason = "max_steps"

    summary = {
        "session_id": session_id,
        "goal": goal,
        "stop_reason": stop_reason,
        "steps_executed": step + 1,
        "tool_calls": tool_calls,
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "model": model,
        "finished_at": now_iso(),
    }

    summary_md = f"""# Agent Session Summary — {session_id}

- **Goal**: {goal}
- **Model**: {model}
- **Stop reason**: {stop_reason}
- **Steps**: {summary['steps_executed']}
- **Tool calls**: {tool_calls}
- **Tokens**: in={total_in} out={total_out}

## Artifacts
- messages: `{messages_path.relative_to(ROOT)}`
- usage: `{usage_path.relative_to(ROOT)}`
- decisions: `{(session_dir / 'decisions.jsonl').relative_to(ROOT) if (session_dir / 'decisions.jsonl').exists() else '(none)'}`
- screenshots: `{(session_dir / 'screenshots').relative_to(ROOT) if (session_dir / 'screenshots').exists() else '(none)'}`
"""
    summary_path.write_text(summary_md, encoding="utf-8")

    print(f"\n[runner] 완료: stop_reason={stop_reason}")
    print(f"  steps={summary['steps_executed']}  tool_calls={tool_calls}")
    print(f"  tokens: in={total_in}  out={total_out}")
    print(f"  summary: {summary_path.relative_to(ROOT)}")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", default=(
        "modeling_order.yml 의 queue 전체를 실행하여 건물 전층 Three.js 3D 매싱을 완성하라. "
        "scene_id='full-building'. 각 step 마다 read_sheet 로 기존 KB 확인 후 필요 시 extract_sheet → build_kb_from_extract. "
        "모든 KB 확보되면 generate_threejs → render_preview → validate_coordinate_system. "
        "버그 발견 시 log_decision + 재시도."
    ))
    ap.add_argument("--session-id", default=datetime.now().strftime("%Y%m%d_%H%M%S") + "_full")
    ap.add_argument("--max-steps", type=int, default=50)
    ap.add_argument("--budget-tokens", type=int, default=1_500_000)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="최소 smoke (list_sheets + read_modeling_order)")
    args = ap.parse_args()

    if args.smoke:
        args.goal = (
            "다음을 순서대로만 수행하라: "
            "(1) list_sheets(only_3d_candidates=true) 로 3D 후보 목록 확인, "
            "(2) read_modeling_order 로 queue 확인, "
            "(3) log_decision('smoke test OK', '두 tool 동작 확인') 후 end_turn. "
            "다른 tool 호출 금지."
        )
        args.session_id = args.session_id.replace("_full", "_smoke")
        args.max_steps = 8

    run_agent(
        goal=args.goal,
        session_id=args.session_id,
        max_steps=args.max_steps,
        budget_tokens=args.budget_tokens,
        model=args.model,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
