"""Optimizer factory.

Responsibility
--------------
Build the optimizer from cfg['optimizer'] (default AdamW).

Planned public API
------------------
build_optimizer(model, optim_cfg) -> torch.optim.Optimizer

Status: NOT IMPLEMENTED — scheduled for PHASE 16.
"""

# TODO(PHASE 16):
#   1. Support 'adamw' (default) and 'adam'; exclude norm/bias params from weight decay.
#   2. Unknown name -> ValueError.
