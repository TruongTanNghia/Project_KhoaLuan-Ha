"""Build consensus ground-truth masks and QC figures (CT + contour + mask).

Usage (once implemented):
    python scripts/03_generate_masks.py --config configs/base.yaml [--set key=value ...]

Uses: src.data.mask_generator, src.evaluation.visualization
Status: NOT IMPLEMENTED — scheduled for PHASE 06-07.
"""

import sys

PHASE = "06-07"


def main() -> int:
    # TODO(PHASE 06-07): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.data.mask_generator, src.evaluation.visualization. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/03_generate_masks.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
