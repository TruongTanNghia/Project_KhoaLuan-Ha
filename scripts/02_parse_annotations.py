"""Parse LIDC XML files and group reader annotations into physical nodules.

Usage (once implemented):
    python scripts/02_parse_annotations.py --config configs/base.yaml [--set key=value ...]

Uses: src.data.xml_parser, src.data.annotation_processor
Status: NOT IMPLEMENTED — scheduled for PHASE 04-05.
"""

import sys

PHASE = "04-05"


def main() -> int:
    # TODO(PHASE 04-05): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.data.xml_parser, src.data.annotation_processor. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/02_parse_annotations.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
