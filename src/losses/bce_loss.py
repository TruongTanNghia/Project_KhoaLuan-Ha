"""Binary cross-entropy loss (baseline loss).

Responsibility
--------------
Numerically stable BCE on logits, optional pos_weight for the strong
foreground/background imbalance (nodule pixels are a tiny fraction).

Planned public API
------------------
class BCELoss(nn.Module): __init__(pos_weight: float | None); forward(logits, target)

Status: NOT IMPLEMENTED — scheduled for PHASE 15.
"""

# TODO(PHASE 15):
#   1. Wrap nn.BCEWithLogitsLoss (never sigmoid + BCELoss: unstable under AMP).
