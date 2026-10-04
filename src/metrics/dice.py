"""Dice similarity coefficient (DSC).

Responsibility
--------------
Dice = 2|P ∩ G| / (|P| + |G|) on thresholded binary masks.

Planned public API
------------------
dice_score(pred: np.ndarray|Tensor, gt, empty_value: float | None) -> float

Status: NOT IMPLEMENTED — scheduled for PHASE 17.
"""

# TODO(PHASE 17):
#   1. Operate on binary masks (threshold applied by caller from cfg).
#   2. Empty GT AND empty prediction: return empty_value (policy set in PHASE 19)
#      and let the evaluator report such cases separately.
#   3. Unit tests with hand-computed toy masks in tests/test_metrics.py.
