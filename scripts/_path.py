import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def add_project_root_to_path() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
