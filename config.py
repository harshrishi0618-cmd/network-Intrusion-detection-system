"""
Central config loader. All modules should import from here instead of
hardcoding thresholds and settings.

Usage:
    from config import cfg
    threshold = cfg["detection"]["cic_threshold"]
"""

import os
import yaml

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
_config: dict | None = None


def _load() -> dict:
    with open(_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def get() -> dict:
    global _config
    if _config is None:
        _config = _load()
    return _config


# Convenience alias
cfg = get()
