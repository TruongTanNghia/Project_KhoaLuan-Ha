"""Create the patient-level train/val/test split.

Usage (once implemented):
    python scripts/05_create_splits.py --config configs/base.yaml [--set key=value ...]

Uses: src.data.dataset_split
Status: NOT IMPLEMENTED — scheduled for PHASE 11.
"""

import sys

PHASE = "11"


def main() -> int:
    # TODO(PHASE 11): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.data.dataset_split. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/05_create_splits.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
