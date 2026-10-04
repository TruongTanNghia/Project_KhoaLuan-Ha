"""Inference on new CT data.

Responsibility
--------------
Run a trained model on a DICOM series or preprocessed slices and output a
lung-NODULE segmentation mask. Output is NOT a cancer diagnosis.

Planned public API
------------------
load_model(checkpoint_path, cfg) -> nn.Module
predict_slice(model, hu_slice, cfg) -> probability map
predict_series(model, series_dir, cfg) -> (mask_volume, nodule_candidates)

Status: NOT IMPLEMENTED — scheduled for PHASE 22.
"""

# TODO(PHASE 22):
#   1. Reuse exactly the same HU/window/normalisation code as training (no copy-paste).
#   2. Sliding-window over full slices when trained on patches; document overlap/stitching.
#   3. Save mask as .npy and optionally DICOM-SEG/NIfTI; save overlay PNGs.
#   4. Every output file/report must carry the disclaimer: research use only,
#      segmentation of lung nodules, not a diagnosis of malignancy.
