"""Validate the raw LIDC-IDRI download before any processing.

Usage (once implemented):
    python scripts/01_validate_raw_data.py --config configs/base.yaml [--set key=value ...]

Uses: src.data.data_validator
Status: NOT IMPLEMENTED — scheduled for PHASE 02.
"""

import sys

PHASE = "02"


def main() -> int:
    # TODO(PHASE 02): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.data.data_validator. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/01_validate_raw_data.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
