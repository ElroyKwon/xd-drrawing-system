"""Agent tool registry — 10 tool 모음."""
from . import (
    list_sheets,
    read_sheet,
    read_modeling_order,
    extract_sheet,
    build_kb_from_extract,
    generate_threejs,
    render_preview,
    validate_coordinate_system,
    log_decision,
    ask_human,
)

ALL_MODULES = [
    list_sheets,
    read_sheet,
    read_modeling_order,
    extract_sheet,
    build_kb_from_extract,
    generate_threejs,
    render_preview,
    validate_coordinate_system,
    log_decision,
    ask_human,
]


def get_schemas():
    """Anthropic SDK tools= 파라미터용 schema 리스트."""
    return [m.SCHEMA for m in ALL_MODULES]


def dispatch(tool_name, tool_input, context=None):
    """tool_use block 처리 → 해당 모듈의 execute 호출."""
    for m in ALL_MODULES:
        if m.SCHEMA["name"] == tool_name:
            return m.execute(tool_input, context=context)
    return {"error": f"unknown tool: {tool_name}"}
