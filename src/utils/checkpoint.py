"""Model checkpoint save/load.

Responsibility
--------------
Persist and restore training state for best/latest checkpoints and resume.

Planned public API
------------------
save_checkpoint(path, model, optimizer, scheduler, scaler, epoch, metrics, cfg)
load_checkpoint(path, model, optimizer=None, scheduler=None, scaler=None, map_location)
    -> dict(epoch, metrics, cfg)

Status: NOT IMPLEMENTED — scheduled for PHASE 16.
"""

# TODO(PHASE 16):
#   1. Write to a temp file then os.replace() to avoid corrupt files on crash.
#   2. Store cfg + dataset_version inside the checkpoint; warn on mismatch at load.
#   3. Paths: checkpoints/<experiment_name>/{best.pt,last.pt}.
#   4. torch.load(weights_only=...) per installed torch version.
