"""Train MODEL 02 (Attention U-Net).

Usage (once implemented):
    python scripts/07_train_attention_unet.py --config experiments/exp04_attention_unet_dice/config.yaml [--set key=value ...]

Uses: src.training.trainer
Status: NOT IMPLEMENTED — scheduled for PHASE 18.
"""

import sys

PHASE = "18"


def main() -> int:
    # TODO(PHASE 18): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.training.trainer. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/07_train_attention_unet.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
