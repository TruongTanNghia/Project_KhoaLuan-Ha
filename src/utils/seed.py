"""Random-seed control for reproducible experiments.

Seeds Python, NumPy and PyTorch (CPU + CUDA). NumPy and PyTorch are imported
lazily so that the early data phases can run without PyTorch installed.

Note: even with ``deterministic=True`` some CUDA kernels have no deterministic
implementation; PyTorch then emits a warning (``warn_only=True``) instead of
crashing. Bit-exact reproducibility across different GPUs/driver versions is
not guaranteed — report results as mean ± std over several seeds.
"""

from __future__ import annotations

import os
import random

from src.utils.logger import get_logger

logger = get_logger(__name__)


def set_seed(seed: int, deterministic: bool = True) -> None:
    """Seed every random number generator used by the project.

    Args:
        seed: Non-negative integer seed.
        deterministic: Also ask cuDNN / PyTorch for deterministic algorithms
            (slower, but required for reproducible training curves).
    """
    if not isinstance(seed, int) or seed < 0:
        raise ValueError(f"seed must be a non-negative int, got {seed!r}")

    random.seed(seed)
    # Only affects subprocesses (e.g. DataLoader workers spawned on Windows).
    os.environ["PYTHONHASHSEED"] = str(seed)

    try:
        import numpy as np
    except ImportError:
        logger.debug("NumPy not installed; skipping NumPy seeding")
    else:
        np.random.seed(seed)

    try:
        import torch
    except ImportError:
        logger.debug("PyTorch not installed; skipping torch seeding")
    else:
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        if deterministic:
            # Required by cuBLAS for deterministic matmul on CUDA >= 10.2.
            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            torch.use_deterministic_algorithms(True, warn_only=True)

    logger.info("Global seed set to %d (deterministic=%s)", seed, deterministic)


def seed_worker(worker_id: int) -> None:  # noqa: ARG001 - signature fixed by DataLoader
    """``worker_init_fn`` for ``torch.utils.data.DataLoader``.

    Each worker derives its NumPy/Python seed from the torch seed that the
    DataLoader assigns it, so augmentations differ between workers but are
    reproducible across runs.
    """
    import numpy as np
    import torch

    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def make_generator(seed: int):
    """Return a seeded ``torch.Generator`` to pass to ``DataLoader(generator=...)``."""
    import torch

    generator = torch.Generator()
    generator.manual_seed(seed)
    return generator
