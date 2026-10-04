"""Evaluate a trained model on the test split; failure-case analysis.

Usage (once implemented):
    python scripts/08_evaluate.py --config experiments/exp01_unet_baseline/config.yaml [--set key=value ...]

Uses: src.evaluation.evaluator, src.evaluation.failure_analysis
Status: NOT IMPLEMENTED — scheduled for PHASE 19-21.
"""

import sys

PHASE = "19-21"


def main() -> int:
    # TODO(PHASE 19-21): parse --config/--set, call load_config(), setup_logging(),
    # set_seed(), then delegate to src.evaluation.evaluator, src.evaluation.failure_analysis. Keep this script thin: no processing
    # logic here, only orchestration of src/ modules.
    print(f"[NOT IMPLEMENTED] scripts/08_evaluate.py is scheduled for PHASE {PHASE}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
