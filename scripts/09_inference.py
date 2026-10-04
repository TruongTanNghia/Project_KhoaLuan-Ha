"""Segment lung nodules on a new CT series (research use only).

Usage (once implemented):
    python scripts/09_inference.py --config experiments/exp04_attention_unet_dice/config.yaml [--set key=value ...]

Uses: src.inference.predict
Status: NOT IMPLEMENTED — scheduled for PHASE 22.
"""

import sys

PHASE = "22"


def main() -> int:
    # TODO(PHASE 22): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.inference.predict. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/09_inference.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
