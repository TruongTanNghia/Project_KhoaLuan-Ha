"""Training / validation loop.

Responsibility
--------------
Run epochs, log metrics, save checkpoints, apply early stopping and write
the experiment record. Contains no data or model construction logic.

Planned public API
------------------
class Trainer: __init__(model, loss_fn, optimizer, scheduler, loaders, cfg, exp_dir)
    fit() -> dict  # best_epoch, best_val_dice, ...
    train_one_epoch(epoch) -> dict; validate(epoch) -> dict

Status: NOT IMPLEMENTED — scheduled for PHASE 16-17.
"""

# TODO(PHASE 16-17):
#   1. AMP (torch.autocast + GradScaler) and grad clipping from cfg['training'].
#   2. Every epoch append to <exp_dir>/history.csv and TensorBoard: train/val loss,
#      val dice/iou/precision/recall, lr.
#   3. Checkpoint best (monitor) and latest via src.utils.checkpoint.
#   4. Save resolved_config.yaml + run_info.json (seed, git commit, torch/CUDA version,
#      GPU name, dataset_version) at start; summary.json at the end.
#   5. Fail fast: NaN loss -> stop and log the batch metadata.
