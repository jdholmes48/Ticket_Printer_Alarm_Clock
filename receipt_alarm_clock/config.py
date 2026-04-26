from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.json"
EXAMPLE_CONFIG_PATH = PROJECT_ROOT / "config.example.json"


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    config_path = Path(path).expanduser() if path else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        config_path = EXAMPLE_CONFIG_PATH

    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    config["_project_root"] = str(PROJECT_ROOT)
    config["_config_path"] = str(config_path)
    return config


def resolve_project_path(config: Dict[str, Any], value: Optional[str]) -> Optional[Path]:
    if not value:
        return None

    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return Path(config["_project_root"]) / path
