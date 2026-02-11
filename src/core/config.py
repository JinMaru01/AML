import os
from pathlib import Path
from dotenv import dotenv_values
from typing import Any

# Internal cache to prevent re-loading env files
_cached_config: dict[str, str] = None

def auto_cast(value: str) -> Any:
    """Cast string value from .env into native Python types."""
    value = value.strip()

    # Quoted string
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    # Boolean
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"

    # Integer
    if value.isdigit():
        return int(value)

    # Float
    try:
        float_val = float(value)
        if "." in value or "e" in value.lower():
            return float_val
    except ValueError:
        pass

    # Comma-separated list
    if "," in value:
        return [auto_cast(v.strip()) for v in value.split(",")]

    return value

def load_dict_into_environ(dotenv_dict: dict[str, str], override: bool = True):
    for key, value in dotenv_dict.items():
        if override or key not in os.environ:
            os.environ[key] = value


def load_environment_variables(env: str = None, enforce_uppercase: bool = True) -> dict[str, str]:
    # Navigate to project root (3 levels up from src/core/config.py)
    base_path = Path(__file__).resolve().parent.parent.parent / "_lib" / "app_env"
    environment = env or os.getenv("ENVIRONMENT", "office")

    env_files = [
        base_path / ".env",
        base_path / f".env.{environment}",
        base_path / ".env.local"
    ]

    merged_config = {}

    for file in env_files:
        if file.exists():
            merged_config.update(dotenv_values(file))
            

    # Reflect overrides in os.environ
    for key in merged_config:
        merged_config[key] = os.getenv(key, merged_config[key])

    load_dict_into_environ(merged_config, True)
    #load_dotenv(dotenv_path=file, override=True)
    # Enforce UPPERCASE keys
    if enforce_uppercase:
        lowercase_keys = [k for k in merged_config if not k.isupper()]
        if lowercase_keys:
            raise ValueError(
                f"❌ Found lowercase or mixed-case keys in .env files: {', '.join(lowercase_keys)}. "
                "Please use UPPERCASE for all environment variable keys."
            )

    return merged_config

def get_cached_env() -> dict[str, str]:
    global _cached_config
    if _cached_config is None:
        _cached_config = load_environment_variables()
    return _cached_config

def load_env_by_prefix(
    prefix: str,
    required: list[str] = [],
    config: dict[str, str] = None
) -> dict[str, Any]:
    config = config or get_cached_env()
    prefix = prefix.upper() + "_"

    result = {
        key[len(prefix):].lower(): auto_cast(value)
        for key, value in config.items()
        if key.startswith(prefix)
    }

    missing = [key.lower() for key in required if key.lower() not in result]
    if missing:
        raise EnvironmentError(
            f"❌ Missing required keys for prefix '{prefix[:-1]}': {', '.join(missing)}"
        )

    return result
