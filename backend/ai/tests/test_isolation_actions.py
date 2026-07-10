"""actions.py는 8000을 mutate하지 않는다(POST/PATCH/PUT/DELETE 호출 0)."""
import ast
from pathlib import Path


def test_actions_module_has_no_write_calls():
    src = (Path(__file__).resolve().parents[1] / "actions.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in {"post", "patch", "put", "delete"}:
            bad.append(node.attr)
    assert not bad, f"actions.py에 write 호출 발견: {bad}"


def test_actions_only_uses_read_tools():
    src = (Path(__file__).resolve().parents[1] / "actions.py").read_text(encoding="utf-8")
    # tools.py의 READ 함수만 참조(write 함수는 존재하지 않아야 함).
    for w in ("create_", "update_", "delete_", "patch_"):
        assert f"tools.{w}" not in src
