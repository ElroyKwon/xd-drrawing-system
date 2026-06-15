"""read_modeling_order — Stage 4가 생성한 modeling_order.yml 반환."""
from .base import IDX_DIR

try:
    import yaml
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pyyaml"])
    import yaml

SCHEMA = {
    "name": "read_modeling_order",
    "description": (
        "Stage 4가 생성한 모델링 순서 DAG를 반환한다. "
        "queue[], blocked[], baseline(reference_floor, reference_sheet, level_stack) 포함. "
        "Agent는 이를 처음에 1회 호출하여 전체 계획을 파악하고, queue의 각 step을 순서대로 진행한다."
    ),
    "input_schema": {
        "type": "object",
        "properties": {},
    },
}


def execute(tool_input, context=None):
    path = IDX_DIR / "modeling_order.yml"
    if not path.exists():
        return {"error": "modeling_order.yml 없음. Stage 4 먼저 실행."}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data
