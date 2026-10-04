"""Combined BCE + Dice loss and loss factory.

Responsibility
--------------
Main loss of the project: w_bce * BCE + w_dice * Dice.

Planned public API
------------------
class BCEDiceLoss(nn.Module): forward(logits, target) -> (total, {'bce':..., 'dice':...})
build_loss(loss_cfg: dict) -> nn.Module   # 'bce' | 'dice' | 'bce_dice'

Status: NOT IMPLEMENTED — scheduled for PHASE 15.
"""

# TODO(PHASE 15):
#   1. Return individual components so both are logged every epoch.
#   2. Unknown loss name -> ValueError.
