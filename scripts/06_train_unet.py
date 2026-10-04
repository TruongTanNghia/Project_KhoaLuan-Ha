"""Train MODEL 01 (U-Net baseline).

Usage (once implemented):
    python scripts/06_train_unet.py --config experiments/exp01_unet_baseline/config.yaml [--set key=value ...]

Uses: src.training.trainer
Status: NOT IMPLEMENTED — scheduled for PHASE 16-17.
"""

import sys

PHASE = "16-17"


def main() -> int:
    # TODO(PHASE 16-17): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.training.trainer. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/06_train_unet.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
