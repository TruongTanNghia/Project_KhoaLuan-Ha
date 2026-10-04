"""Learning-rate scheduler factory.

Responsibility
--------------
Build the LR scheduler from cfg['scheduler'].

Planned public API
------------------
build_scheduler(optimizer, sched_cfg, epochs) -> scheduler | None

Status: NOT IMPLEMENTED — scheduled for PHASE 16.
"""

# TODO(PHASE 16):
#   1. 'cosine' -> CosineAnnealingLR(T_max=epochs, eta_min=min_lr);
#      'plateau' -> ReduceLROnPlateau on the monitored val metric; 'none' -> None.
#   2. Log the LR every epoch into history.csv.
