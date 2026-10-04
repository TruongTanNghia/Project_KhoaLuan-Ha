"""File I/O and configuration utilities.

Responsibilities
----------------
* Locate the project root so that no absolute path is ever hard-coded.
* Load hierarchical YAML configs (``_base_`` inheritance + CLI overrides).
* Resolve relative paths in ``cfg["paths"]`` against the project root.
* Read/write JSON, YAML and CSV artefacts produced by the pipeline.

Config inheritance
------------------
A YAML file may declare ``_base_: <relative/path.yaml>``. The base file is
loaded first (recursively) and the child is deep-merged on top of it, so a
child only needs to state what differs. Overrides given on the command line
(``--set training.batch_size=8``) are applied last.
"""

from __future__ import annotations

import copy
import csv
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

BASE_KEY = "_base_"
# Environment variable that overrides ``paths.raw_dir`` so the (>120 GB)
# LIDC-IDRI download can live on any drive without editing tracked configs.
RAW_DIR_ENV_VAR = "LIDC_IDRI_DIR"
_MAX_INHERITANCE_DEPTH = 10
_SCI_NOTATION = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)[eE][+-]?\d+")


class ConfigError(ValueError):
    """Raised when a configuration file is missing, malformed or inconsistent."""


# --------------------------------------------------------------------------- #
# Generic helpers
# --------------------------------------------------------------------------- #
def ensure_dir(path: str | Path) -> Path:
    """Create ``path`` (and parents) if needed and return it as a ``Path``."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_path(path: str | Path, root: Path = PROJECT_ROOT) -> Path:
    """Return ``path`` as an absolute path; relative paths are anchored at ``root``."""
    path = Path(os.path.expandvars(os.path.expanduser(str(path))))
    return path if path.is_absolute() else (root / path).resolve()


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` into a copy of ``base``.

    Nested mappings are merged key by key; any other value in ``override``
    (including lists) replaces the value in ``base``.
    """
    merged = copy.deepcopy(dict(base))
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def get_by_dotted(cfg: Mapping[str, Any], dotted_key: str, default: Any = ...) -> Any:
    """Fetch ``cfg["a"]["b"]`` via ``"a.b"``. Raises ``KeyError`` if missing and no default."""
    node: Any = cfg
    for part in dotted_key.split("."):
        if not isinstance(node, Mapping) or part not in node:
            if default is ...:
                raise KeyError(f"Config key not found: '{dotted_key}'")
            return default
        node = node[part]
    return node


def set_by_dotted(cfg: dict[str, Any], dotted_key: str, value: Any) -> None:
    """Set ``cfg["a"]["b"] = value`` via ``"a.b"``, creating intermediate dicts."""
    parts = dotted_key.split(".")
    node = cfg
    for part in parts[:-1]:
        child = node.setdefault(part, {})
        if not isinstance(child, dict):
            raise ConfigError(
                f"Cannot set '{dotted_key}': '{part}' is a {type(child).__name__}, not a mapping"
            )
        node = child
    node[parts[-1]] = value


# --------------------------------------------------------------------------- #
# YAML / config
# --------------------------------------------------------------------------- #
def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file that must contain a mapping at top level."""
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"Top level of {path} must be a mapping, got {type(data).__name__}")
    return data


def save_yaml(data: Mapping[str, Any], path: str | Path) -> Path:
    """Write ``data`` to ``path`` as human-readable YAML (keys keep insertion order)."""
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(_to_plain(data), f, sort_keys=False, allow_unicode=True)
    return path


def _load_with_bases(path: Path, depth: int = 0) -> dict[str, Any]:
    if depth > _MAX_INHERITANCE_DEPTH:
        raise ConfigError(f"Config inheritance deeper than {_MAX_INHERITANCE_DEPTH} levels at {path}")
    data = load_yaml(path)
    base_ref = data.pop(BASE_KEY, None)
    if base_ref is None:
        return data
    base_path = (path.parent / str(base_ref)).resolve()
    return deep_merge(_load_with_bases(base_path, depth + 1), data)


def parse_overrides(overrides: Iterable[str] | None) -> list[tuple[str, Any]]:
    """Parse ``["a.b=1", "c=[1, 2]"]`` into typed ``(key, value)`` pairs.

    Values are parsed with YAML so ``8`` -> int, ``true`` -> bool,
    ``null`` -> None, ``[1,2]`` -> list. Scientific notation without a dot
    (``1e-4``), which YAML 1.1 reads as a string, is converted to float.
    """
    parsed: list[tuple[str, Any]] = []
    for item in overrides or []:
        if "=" not in item:
            raise ConfigError(f"Override must look like key=value, got '{item}'")
        key, raw_value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ConfigError(f"Empty key in override '{item}'")
        try:
            value = yaml.safe_load(raw_value)
        except yaml.YAMLError as exc:
            raise ConfigError(f"Cannot parse value in override '{item}': {exc}") from exc
        if isinstance(value, str) and _SCI_NOTATION.fullmatch(value.strip()):
            value = float(value)
        parsed.append((key, value))
    return parsed


def load_config(
    path: str | Path,
    overrides: Sequence[str] | None = None,
    resolve_paths: bool = True,
) -> dict[str, Any]:
    """Load a config with inheritance, environment and CLI overrides.

    Precedence (lowest -> highest): ``_base_`` chain, the file itself,
    ``$LIDC_IDRI_DIR`` (for ``paths.raw_dir`` only), ``overrides``.

    Args:
        path: YAML file to load. Relative paths are resolved from the project root.
        overrides: ``key=value`` strings with dotted keys.
        resolve_paths: Convert every entry of ``cfg["paths"]`` to an absolute path string.

    Returns:
        A plain ``dict``. ``cfg["_meta"]`` records where the config came from.
    """
    cfg_path = resolve_path(path)
    cfg = _load_with_bases(cfg_path)

    env_raw_dir = os.environ.get(RAW_DIR_ENV_VAR)
    if env_raw_dir:
        set_by_dotted(cfg, "paths.raw_dir", env_raw_dir)

    applied = parse_overrides(overrides)
    for key, value in applied:
        set_by_dotted(cfg, key, value)

    if resolve_paths and isinstance(cfg.get("paths"), dict):
        cfg["paths"] = {k: str(resolve_path(v)) for k, v in cfg["paths"].items()}

    cfg["_meta"] = {
        "config_path": str(cfg_path),
        "project_root": str(PROJECT_ROOT),
        "raw_dir_from_env": bool(env_raw_dir),
        "overrides": [f"{k}={v}" for k, v in applied],
    }
    return cfg


def require_keys(cfg: Mapping[str, Any], keys: Iterable[str]) -> None:
    """Raise ``ConfigError`` listing every dotted key that is absent from ``cfg``."""
    missing = [k for k in keys if get_by_dotted(cfg, k, default=None) is None]
    if missing:
        raise ConfigError(f"Missing required config keys: {', '.join(missing)}")


# --------------------------------------------------------------------------- #
# JSON / CSV
# --------------------------------------------------------------------------- #
def _to_plain(obj: Any) -> Any:
    """Convert Paths / numpy scalars / tuples into JSON- and YAML-safe objects."""
    if isinstance(obj, Mapping):
        return {str(k): _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if hasattr(obj, "item") and callable(obj.item):  # numpy / torch scalar
        try:
            return obj.item()
        except (ValueError, RuntimeError):
            pass
    if hasattr(obj, "tolist") and callable(obj.tolist):  # numpy array
        return obj.tolist()
    return obj


def save_json(data: Any, path: str | Path, indent: int = 2) -> Path:
    """Write ``data`` as UTF-8 JSON, creating parent directories."""
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(_to_plain(data), f, indent=indent, ensure_ascii=False)
    return path


def load_json(path: str | Path) -> Any:
    """Read a UTF-8 JSON file."""
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def save_csv(rows: Sequence[Mapping[str, Any]], path: str | Path,
             fieldnames: Sequence[str] | None = None) -> Path:
    """Write a list of dicts as CSV. Column order follows ``fieldnames`` or first-seen keys."""
    path = Path(path)
    ensure_dir(path.parent)
    if fieldnames is None:
        seen: dict[str, None] = {}
        for row in rows:
            seen.update(dict.fromkeys(row.keys()))
        fieldnames = list(seen)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _to_plain(row.get(k, "")) for k in fieldnames})
    return path


def load_csv(path: str | Path) -> list[dict[str, str]]:
    """Read a CSV file into a list of dicts (all values are strings)."""
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
