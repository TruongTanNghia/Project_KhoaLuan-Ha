"""Intersection over Union (Jaccard index).

Responsibility
--------------
IoU = |P ∩ G| / |P ∪ G|. Note IoU = Dice / (2 - Dice) per sample.

Planned public API
------------------
iou_score(pred, gt, empty_value: float | None) -> float

Status: NOT IMPLEMENTED — scheduled for PHASE 17.
"""

# TODO(PHASE 17):
#   1. Same empty-mask policy as dice.py; unit test the Dice-IoU identity.
