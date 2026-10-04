"""Contour -> binary ground-truth mask with multi-reader consensus.

Responsibility
--------------
Rasterise each reader's polygon per slice and combine readers into one
ground-truth mask per nodule according to cfg['annotation']['consensus'].

Planned public API
------------------
rasterize_contour(points, shape, include_boundary) -> np.ndarray[bool]
reader_mask(reader_annotation, volume_shape) -> np.ndarray[bool]  # inclusion - exclusion
consensus_mask(reader_masks, method, level, n_readers) -> (mask, agreement_count_map)
build_ground_truth(nodules, volume, cfg) -> (mask_volume, metadata_rows)

Status: NOT IMPLEMENTED — scheduled for PHASE 06.
"""

# TODO(PHASE 06):
#   1. Rasterise with skimage.draw.polygon (row = y, col = x); handle boundary pixels
#      according to include_contour_boundary and verify visually in PHASE 07.
#   2. Subtract inclusion=FALSE contours from the reader's mask on that slice.
#   3. majority: pixel = 1 if votes >= ceil(level * N), where N = number of readers of the
#      scan (denominator=all_readers, default: level 0.5 -> '>= 2 of 4') or number of
#      readers who marked THAT nodule (denominator=nodule_readers). Log scans whose
#      reader count != 4 because 'all_readers' then changes the effective threshold.
#   4. Keep agreement_count_map (0..4) so disagreement can be analysed later.
#   5. Metadata row per (nodule, slice) - full column list in docs/04_annotation_pipeline.md
#      section 2 [6]: patient_id, study_uid, series_uid, slice_index,
#      nodule_id, radiologist_count, mask_source (e.g. 'majority@0.5'), nodule_size_mm,
#      reader_pairwise_iou (disagreement measure).
#   6. Never assume 1 patient = 1 mask: a patient can have 0..N nodules.
