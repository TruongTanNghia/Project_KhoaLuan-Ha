"""95th-percentile Hausdorff distance (HD95), in millimetres.

Responsibility
--------------
Boundary-distance metric complementary to overlap metrics: penalises
contours that are far from the GT boundary even when Dice is high.

Planned public API
------------------
hd95(pred, gt, spacing_yx_mm: tuple[float, float]) -> float  # NaN if either is empty

Status: NOT IMPLEMENTED — scheduled for PHASE 19.
"""

# TODO(PHASE 19):
#   1. Extract surfaces (mask XOR eroded mask), compute distances with
#      scipy.ndimage.distance_transform_edt(sampling=spacing), take the 95th
#      percentile of the symmetric surface distances.
#   2. Use physical spacing (mm), not pixels; patches keep the source pixel spacing.
#   3. Return NaN when pred or GT is empty and count such cases separately.
#   4. Cross-check against MONAI/medpy implementation on random masks in tests.
