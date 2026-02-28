"""
Configuration management for Linux System Agent
"""

import json
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".linux_agent"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "search": {"rate_limit_per_minute": 5, "language": "en", "max_results": 5},
    "auto_fix": {"enabled": True, "ask_before_fix": True},
    "llm": {"model": "qwen2:7b", "temperature": 0.1},
}


def ensure_config_dir():
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(exist_ok=True)


def load_config() -> dict:
    """Load configuration from file or return defaults."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                stored = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = DEFAULT_CONFIG.copy()
                for section, values in stored.items():
                    if section in config:
                        config[section].update(values)
                return config
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_setting(path: str):
    """Get a specific setting using dot notation (e.g., 'search.language')."""
    config = load_config()
    keys = path.split(".")
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def set_setting(path: str, value) -> bool:
    """Set a specific setting using dot notation."""
    config = load_config()
    keys = path.split(".")
    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    if keys[-1] in current:
        current[keys[-1]] = value
        save_config(config)
        return True
    return False


def reset_config() -> None:
    """Reset configuration to defaults."""
    save_config(DEFAULT_CONFIG.copy())
