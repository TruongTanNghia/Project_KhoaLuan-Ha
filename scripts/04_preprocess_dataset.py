"""HU conversion, windowing, normalisation and ROI cropping.

Usage (once implemented):
    python scripts/04_preprocess_dataset.py --config configs/base.yaml [--set key=value ...]

Uses: src.data.hu_converter, src.data.preprocessing
Status: NOT IMPLEMENTED — scheduled for PHASE 08-10.
"""

import sys

PHASE = "08-10"


def main() -> int:
    # TODO(PHASE 08-10): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.data.hu_converter, src.data.preprocessing. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/04_preprocess_dataset.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
