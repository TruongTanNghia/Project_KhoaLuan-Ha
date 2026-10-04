"""Pixel-wise recall (sensitivity).

Responsibility
--------------
Recall = TP / (TP + FN). Low recall -> under-segmentation / missed nodule.

Planned public API
------------------
recall_score(pred, gt, empty_value: float | None) -> float

Status: NOT IMPLEMENTED — scheduled for PHASE 17.
"""

# TODO(PHASE 17):
#   1. Undefined when GT is empty (TP + FN = 0): return empty_value.
