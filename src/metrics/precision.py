"""Pixel-wise precision (positive predictive value).

Responsibility
--------------
Precision = TP / (TP + FP). Low precision -> over-segmentation / false positives.

Planned public API
------------------
precision_score(pred, gt, empty_value: float | None) -> float

Status: NOT IMPLEMENTED — scheduled for PHASE 17.
"""

# TODO(PHASE 17):
#   1. Undefined when the prediction is empty (TP + FP = 0): return empty_value.
