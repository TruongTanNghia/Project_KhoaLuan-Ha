"""Windowing, normalisation and ROI cropping.

Responsibility
--------------
Turn HU volumes + GT masks into model-ready 2D samples and save them to
data/processed/ with full traceability metadata.

Planned public API
------------------
apply_window(hu, level, width) -> np.ndarray[float32] in [0, 1]
crop_nodule_patches(image, mask, nodule_rows, cfg, rng) -> list[Sample]
sample_negative_patches(image, mask, lung_mask, cfg, rng) -> list[Sample]
preprocess_series(volume, gt, cfg) -> metadata rows

Status: NOT IMPLEMENTED — scheduled for PHASE 09-10.
"""

# TODO(PHASE 09-10):
#   1. PHASE 09: window [level - width/2, level + width/2], clip, scale to [0, 1].
#   2. PHASE 09: decide on in-plane resampling (target_spacing_xy_mm) and justify.
#   3. PHASE 10: nodule-centred patches with random centre jitter; negative patches
#      sampled inside the lungs (not in air outside the body) at negative_ratio.
#   4. Save image/mask pairs as .npy (float16 image, uint8 mask) under
#      data/processed/{images,masks}/<patient_id>/ and one row per sample in
#      data/processed/metadata/samples.csv (includes patient_id for the split).
#   5. Record dataset_version + config hash in data/processed/metadata/manifest.json.
