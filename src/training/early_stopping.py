"""Early stopping on a monitored validation metric.

Responsibility
--------------
Stop training when the monitored metric (default val_dice) has not improved
by min_delta for `patience` epochs.

Planned public API
------------------
class EarlyStopping: __init__(monitor, mode, patience, min_delta);
    step(value, epoch) -> bool (True = stop); best_value; best_epoch

Status: NOT IMPLEMENTED — scheduled for PHASE 17.
"""

# TODO(PHASE 17):
#   1. Pure-Python, no torch dependency; unit test the max/min modes.
