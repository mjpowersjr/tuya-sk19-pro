"""Shared config loader for the SK19 Pro tools.

Precedence (first found wins, per field):
  1. environment: SK19_DEVICE_ID, SK19_HOST, SK19_LOCAL_KEY, SK19_VERSION
  2. file named by $SK19_CONFIG
  3. ./sk19.toml
  4. ~/.config/sk19/config.toml
"""
import os
import pathlib
import tomllib

FIELDS = {"device_id": "SK19_DEVICE_ID", "host": "SK19_HOST", "local_key": "SK19_LOCAL_KEY", "version": "SK19_VERSION"}


def _candidates():
    if os.environ.get("SK19_CONFIG"):
        yield pathlib.Path(os.environ["SK19_CONFIG"]).expanduser()
    yield pathlib.Path(__file__).with_name("sk19.toml")
    yield pathlib.Path.home() / ".config" / "sk19" / "config.toml"


def load() -> dict:
    cfg = {"version": 3.5}
    for path in _candidates():
        if path.is_file():
            if path.stat().st_mode & 0o077:
                raise SystemExit(f"{path} is readable by others; run: chmod 600 {path}")
            cfg.update({k: v for k, v in tomllib.loads(path.read_text()).get("device", {}).items() if v not in (None, "")})
            break
    for key, env in FIELDS.items():
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    missing = [k for k in ("device_id", "host", "local_key") if not cfg.get(k)]
    if missing:
        raise SystemExit(f"missing config: {', '.join(missing)} (see sk19.example.toml)")
    cfg["version"] = float(cfg["version"])
    return cfg
