"""Soft Dice loss.

Responsibility
--------------
Overlap-based loss that directly optimises the evaluation criterion and is
insensitive to the background/foreground ratio.

Planned public API
------------------
class DiceLoss(nn.Module): __init__(smooth: float); forward(logits, target)

Status: NOT IMPLEMENTED — scheduled for PHASE 15.
"""

# TODO(PHASE 15):
#   1. probs = sigmoid(logits); compute per-sample Dice over (H, W), average over batch.
#   2. Document behaviour for empty GT (negative patches): with smooth > 0 an empty
#      prediction on an empty mask gives loss ~ 0, which is the desired behaviour.
#   3. Compute in float32 even under AMP.
