"""Group per-radiologist annotations into physical nodules (annotation -> contour).

Responsibility
--------------
LIDC readers annotated independently and their nodule IDs are NOT linked.
This module clusters annotations that refer to the same physical nodule and
maps every contour onto CT slice indices.

Planned public API
------------------
link_rois_to_slices(read_msg, volume) -> per-ROI slice_index
cluster_nodules(read_msg, volume, cfg) -> list[PhysicalNodule]
@dataclass PhysicalNodule: nodule_uid, patient_id, series_uid, reader_annotations,
    radiologist_count, centroid_zyx, estimated_diameter_mm, slice_range

Status: NOT IMPLEMENTED — scheduled for PHASE 05.
"""

# TODO(PHASE 05):
#   1. Map ROI -> slice via imageSOP_UID; fall back to imageZposition with a tolerance of
#      half the slice spacing; log every fallback and every unmatched ROI.
#   2. Compute each reader-annotation centroid in mm (use spacing), then cluster with
#      distance threshold cfg['annotation']['cluster_distance_mm'].
#   3. A cluster must contain at most one annotation per reader; if violated, log it as
#      ambiguous and keep it in the disagreement report instead of silently merging.
#   4. Estimate diameter (max in-plane extent across slices) for nodule_size bins.
#   5. Write data/interim/annotations/nodules.csv and a disagreement report
#      (nodules marked by 1, 2, 3, 4 readers). STOP if ROIs cannot be matched.
