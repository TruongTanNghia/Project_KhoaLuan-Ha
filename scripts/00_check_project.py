"""PHASE 00 — Verify the project skeleton and configuration system.

Checks:
    1. Every required directory / file of the project layout exists.
    2. Every config (configs/*.yaml, experiments/*/config.yaml) loads, inherits
       correctly and contains the keys the pipeline depends on.
    3. Experiment configs differ only in the intended factors (ablation design).
    4. Seeding makes Python / NumPy / PyTorch random draws reproducible.
    5. Logging writes to logs/.

Usage:
    python scripts/00_check_project.py
Exit code 0 = PHASE 00 valid, 1 = at least one check failed.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.io import PROJECT_ROOT, ConfigError, get_by_dotted, load_config, require_keys  # noqa: E402
from src.utils.logger import get_logger, setup_logging  # noqa: E402
from src.utils.seed import set_seed  # noqa: E402

logger = get_logger("check_project")

REQUIRED_DIRS = [
    "configs", "data/raw/LIDC-IDRI", "data/interim/dicom", "data/interim/annotations",
    "data/interim/converted", "data/processed/images", "data/processed/masks",
    "data/processed/metadata", "data/splits", "src/data", "src/datasets", "src/models",
    "src/losses", "src/metrics", "src/training", "src/evaluation", "src/inference",
    "src/utils", "scripts", "experiments", "checkpoints", "logs", "results/metrics",
    "results/curves", "results/predictions", "results/overlays", "results/failure_cases",
    "notebooks", "tests", "app", "docs",
]
REQUIRED_FILES = [
    "README.md", "requirements.txt", ".gitignore", "LICENSE", "pyproject.toml",
    "configs/base.yaml", "configs/unet.yaml", "configs/attention_unet.yaml",
    "app/app.py", "app/README.md", "docs/DATA_ASSUMPTIONS.md", "docs/PHASES.md",
]
REQUIRED_CONFIG_KEYS = [
    "project.name", "project.dataset_version", "project.seed",
    "paths.raw_dir", "paths.processed_dir", "paths.splits_dir", "paths.checkpoints_dir",
    "annotation.consensus.method", "annotation.consensus.level",
    "preprocessing.window.level", "preprocessing.window.width",
    "split.train_ratio", "split.val_ratio", "split.test_ratio",
    "dataset.image_size", "model.name", "loss.name", "optimizer.name", "optimizer.lr",
    "scheduler.name", "training.epochs", "training.batch_size",
    "evaluation.metrics",
]
NUMERIC_KEYS = [
    "optimizer.lr", "optimizer.weight_decay", "scheduler.min_lr",
    "training.early_stopping.min_delta", "split.train_ratio", "split.val_ratio",
    "split.test_ratio", "annotation.consensus.level",
]
# Expected (model, loss) per experiment — the 2x2 ablation grid.
EXPECTED_EXPERIMENTS = {
    "exp01_unet_baseline": ("unet", "bce"),
    "exp02_unet_dice": ("unet", "bce_dice"),
    "exp03_attention_unet": ("attention_unet", "bce"),
    "exp04_attention_unet_dice": ("attention_unet", "bce_dice"),
}
# Keys allowed to differ between experiments; anything else breaks the ablation.
ALLOWED_DIFF_PREFIXES = ("experiment", "model.name", "model.gate_channels_ratio", "loss.name", "_meta")


def _flatten(d: dict, prefix: str = "") -> dict[str, object]:
    out: dict[str, object] = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten(v, key))
        else:
            out[key] = v
    return out


def check_layout() -> list[str]:
    errors = [f"missing directory: {d}" for d in REQUIRED_DIRS if not (PROJECT_ROOT / d).is_dir()]
    errors += [f"missing file: {f}" for f in REQUIRED_FILES if not (PROJECT_ROOT / f).is_file()]
    return errors


def check_config(path: Path) -> tuple[dict | None, list[str]]:
    rel = path.relative_to(PROJECT_ROOT)
    try:
        cfg = load_config(path)
        require_keys(cfg, REQUIRED_CONFIG_KEYS)
    except (ConfigError, KeyError) as exc:
        return None, [f"{rel}: {exc}"]
    errors = []
    for key in NUMERIC_KEYS:
        value = get_by_dotted(cfg, key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{rel}: '{key}' must be numeric, got {value!r} ({type(value).__name__})")
    ratios = sum(get_by_dotted(cfg, f"split.{k}_ratio") for k in ("train", "val", "test"))
    if abs(ratios - 1.0) > 1e-6:
        errors.append(f"{rel}: split ratios sum to {ratios}, expected 1.0")
    depth = get_by_dotted(cfg, "model.depth")
    for side in get_by_dotted(cfg, "dataset.image_size"):
        if side % (2 ** depth) != 0:
            errors.append(f"{rel}: image_size {side} not divisible by 2**depth={2 ** depth}")
    return cfg, errors


def check_experiments() -> list[str]:
    errors: list[str] = []
    flat_cfgs: dict[str, dict] = {}
    for exp_name, (model_name, loss_name) in EXPECTED_EXPERIMENTS.items():
        path = PROJECT_ROOT / "experiments" / exp_name / "config.yaml"
        if not path.is_file():
            errors.append(f"missing experiment config: {path.relative_to(PROJECT_ROOT)}")
            continue
        cfg, cfg_errors = check_config(path)
        errors += cfg_errors
        if cfg is None:
            continue
        if cfg["experiment"]["name"] != exp_name:
            errors.append(f"{exp_name}: experiment.name is '{cfg['experiment']['name']}'")
        if (cfg["model"]["name"], cfg["loss"]["name"]) != (model_name, loss_name):
            errors.append(f"{exp_name}: expected ({model_name}, {loss_name}), "
                          f"got ({cfg['model']['name']}, {cfg['loss']['name']})")
        flat_cfgs[exp_name] = _flatten(cfg)

    # Fair comparison: only architecture / loss may differ between experiments.
    names = list(flat_cfgs)
    for other in names[1:]:
        a, b = flat_cfgs[names[0]], flat_cfgs[other]
        for key in sorted(set(a) | set(b)):
            if key.startswith(ALLOWED_DIFF_PREFIXES):
                continue
            if a.get(key) != b.get(key):
                errors.append(f"ablation leak: '{key}' differs between {names[0]} "
                              f"({a.get(key)!r}) and {other} ({b.get(key)!r})")
    return errors


def check_seed() -> list[str]:
    def draw() -> list[float]:
        set_seed(123)
        values = [random.random()]
        try:
            import numpy as np
            values.append(float(np.random.rand()))
        except ImportError:
            logger.warning("NumPy not installed - NumPy seeding not checked (install in PHASE 01)")
        try:
            import torch
            values.append(float(torch.rand(1)))
        except ImportError:
            logger.warning("PyTorch not installed - torch seeding not checked (install in PHASE 01)")
        return values

    return [] if draw() == draw() else ["set_seed() does not reproduce random draws"]


def main() -> int:
    cfg = load_config("configs/base.yaml")
    log_file = setup_logging("00_check_project", cfg["paths"]["logs_dir"], cfg["logging"]["level"])
    logger.info("Project root: %s", PROJECT_ROOT)
    logger.info("Python %s", sys.version.split()[0])

    results: dict[str, list[str]] = {
        "layout": check_layout(),
        "configs": [e for p in sorted((PROJECT_ROOT / "configs").glob("*.yaml"))
                    for e in check_config(p)[1]],
        "experiments": check_experiments(),
        "seed": check_seed(),
    }

    failed = False
    for name, errors in results.items():
        if errors:
            failed = True
            logger.error("[FAIL] %s (%d issue(s))", name, len(errors))
            for err in errors:
                logger.error("    - %s", err)
        else:
            logger.info("[ OK ] %s", name)

    raw_dir = Path(cfg["paths"]["raw_dir"])
    n_raw = sum(1 for p in raw_dir.iterdir() if p.name != ".gitkeep") if raw_dir.is_dir() else 0
    logger.info("Raw data dir: %s (%d entries) - dataset is validated in PHASE 02", raw_dir, n_raw)
    logger.info("Log written to %s", log_file)

    if failed:
        logger.error("PHASE 00 INVALID - fix the issues above before PHASE 01.")
        return 1
    logger.info("PHASE 00 VALID - project skeleton and config system are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
