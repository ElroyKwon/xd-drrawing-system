"""격리 불변식 (g): backend/ai/ 소스가 기존 backend 모듈을 import하지 않음 (S8.0 K6).

AST로 모든 backend/ai 소스의 import를 스캔해 금지 모듈 참조가 0임을 강제한다.
"""
from __future__ import annotations

import ast
import pathlib

_AI_DIR = pathlib.Path(__file__).resolve().parent.parent

# 기존 8000 backend 모듈 — 이들 중 하나라도 import하면 격리 위반.
_FORBIDDEN = {
    "store", "auth", "config", "conversion", "vector", "compare",
    "sheet_meta", "main",
}
_FORBIDDEN_PREFIX = ("routes_",)

# 로컬(사이드카 자체) 모듈은 스캔 대상이지만 위반이 아니다.
_LOCAL = {p.stem for p in _AI_DIR.glob("*.py")}


def _ai_sources():
    for p in _AI_DIR.rglob("*.py"):
        if ".venv" in p.parts:
            continue
        yield p


def _imported_top_names(tree: ast.AST) -> set:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # 절대 import만(레벨 0). 상대 import는 격리 내부.
            if node.module and node.level == 0:
                names.add(node.module.split(".")[0])
    return names


def test_no_backend_module_imports():
    violations = []
    for src in _ai_sources():
        tree = ast.parse(src.read_text(encoding="utf-8"), filename=str(src))
        for name in _imported_top_names(tree):
            if name in _LOCAL:
                continue
            if name in _FORBIDDEN or name.startswith(_FORBIDDEN_PREFIX):
                violations.append(f"{src.name}: import {name}")
    assert not violations, f"격리 위반(backend 모듈 import): {violations}"


def test_sidecar_imports_without_backend():
    # 8001 앱이 backend 모듈 없이 import·구성된다(격리 부팅).
    import main_ai  # noqa: F401

    assert main_ai.app is not None
