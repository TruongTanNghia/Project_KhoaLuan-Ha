"""Tests for src.utils (PHASE 00): config loading, overrides, IO, seeding."""

from __future__ import annotations

import random

import pytest

from src.utils.io import (
    PROJECT_ROOT,
    RAW_DIR_ENV_VAR,
    ConfigError,
    deep_merge,
    load_config,
    load_csv,
    load_json,
    parse_overrides,
    save_csv,
    save_json,
)
from src.utils.seed import set_seed


def test_deep_merge_keeps_unrelated_keys():
    base = {"a": {"x": 1, "y": 2}, "b": [1, 2]}
    merged = deep_merge(base, {"a": {"y": 3}, "b": [9]})
    assert merged == {"a": {"x": 1, "y": 3}, "b": [9]}
    assert base["a"]["y"] == 2, "base must not be mutated"


def test_inheritance_chain(tmp_path):
    (tmp_path / "base.yaml").write_text("a: 1\nnested: {x: 1, y: 2}\n", encoding="utf-8")
    (tmp_path / "mid.yaml").write_text("_base_: base.yaml\nnested: {y: 3}\n", encoding="utf-8")
    (tmp_path / "leaf.yaml").write_text("_base_: mid.yaml\na: 5\n", encoding="utf-8")
    cfg = load_config(tmp_path / "leaf.yaml", resolve_paths=False)
    assert cfg["a"] == 5
    assert cfg["nested"] == {"x": 1, "y": 3}
    assert "_base_" not in cfg


def test_overrides_are_typed():
    parsed = dict(parse_overrides(["t.bs=8", "o.lr=1e-4", "f=true", "n=null", "s=[128, 128]", "m=unet"]))
    assert parsed == {"t.bs": 8, "o.lr": 1e-4, "f": True, "n": None, "s": [128, 128], "m": "unet"}
    assert isinstance(parsed["o.lr"], float)


def test_bad_override_raises():
    with pytest.raises(ConfigError):
        parse_overrides(["no_equals_sign"])


def test_missing_config_raises(tmp_path):
    with pytest.raises(ConfigError):
        load_config(tmp_path / "does_not_exist.yaml")


def test_project_configs_resolve_paths(monkeypatch):
    monkeypatch.delenv(RAW_DIR_ENV_VAR, raising=False)
    cfg = load_config("configs/unet.yaml", overrides=["training.batch_size=4"])
    assert cfg["model"]["name"] == "unet"
    assert cfg["training"]["batch_size"] == 4
    assert cfg["paths"]["raw_dir"] == str((PROJECT_ROOT / "data/raw/LIDC-IDRI").resolve())


def test_raw_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv(RAW_DIR_ENV_VAR, str(tmp_path))
    cfg = load_config("configs/base.yaml")
    assert cfg["paths"]["raw_dir"] == str(tmp_path)
    assert cfg["_meta"]["raw_dir_from_env"] is True


def test_cli_override_beats_env(monkeypatch, tmp_path):
    monkeypatch.setenv(RAW_DIR_ENV_VAR, str(tmp_path / "env"))
    cfg = load_config("configs/base.yaml", overrides=[f"paths.raw_dir={tmp_path / 'cli'}"])
    assert cfg["paths"]["raw_dir"] == str(tmp_path / "cli")


def test_json_csv_roundtrip(tmp_path):
    save_json({"dice": 0.5, "path": tmp_path}, tmp_path / "a" / "x.json")
    assert load_json(tmp_path / "a" / "x.json") == {"dice": 0.5, "path": str(tmp_path)}
    rows = [{"patient_id": "LIDC-IDRI-0001", "n": 1}, {"patient_id": "LIDC-IDRI-0002", "extra": "y"}]
    save_csv(rows, tmp_path / "x.csv")
    loaded = load_csv(tmp_path / "x.csv")
    assert list(loaded[0]) == ["patient_id", "n", "extra"]
    assert loaded[1] == {"patient_id": "LIDC-IDRI-0002", "n": "", "extra": "y"}


def test_seed_reproducible():
    np = pytest.importorskip("numpy")
    set_seed(7)
    first = (random.random(), float(np.random.rand()))
    set_seed(7)
    assert (random.random(), float(np.random.rand())) == first


def test_seed_rejects_invalid():
    with pytest.raises(ValueError):
        set_seed(-1)
