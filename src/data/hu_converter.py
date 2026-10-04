"""Stored pixel values -> Hounsfield Units (HU).

Responsibility
--------------
Convert raw DICOM values to the physical HU scale, where air ~ -1000 HU,
water = 0 HU, soft tissue ~ +20..+80 HU and bone > +400 HU.

Planned public API
------------------
to_hu(raw: np.ndarray, slope: float, intercept: float,
      padding_value: int | None, min_hu: float, max_hu: float) -> np.ndarray[float32]

Status: NOT IMPLEMENTED — scheduled for PHASE 08.
"""

# TODO(PHASE 08):
#   1. HU = raw * RescaleSlope + RescaleIntercept (per series; check it is constant
#      across slices, otherwise convert per slice).
#   2. Pixels outside the scanner field of view (PixelPaddingValue, often -2000/-3024)
#      must be set to min_hu (air) before clipping, otherwise they distort windowing.
#   3. Clip to [min_hu, max_hu] from cfg['preprocessing']['hu'].
#   4. Sanity check per series: median HU inside the body ~ soft tissue, outside ~ air;
#      log a warning if the histogram looks wrong (wrong slope/intercept).
