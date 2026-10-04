"""Categorise and export failure cases.

Responsibility
--------------
Two-axis failure analysis: error type (exclusive) x nodule context (multi-label).

Planned public API
------------------
categorize_error(nodule_metrics, thresholds) -> str
context_labels(nodule_row, lung_mask, hu_volume, cfg) -> dict[str, bool]
export_failure_cases(per_sample_csv, predictions_dir, out_dir, n_per_category)

Status: NOT IMPLEMENTED — scheduled for PHASE 21.
"""

# TODO(PHASE 21): (design: docs/13_failure_analysis.md)
#   1. Axis A - error type, mutually exclusive, per NODULE (3D metrics), rule order:
#      missed (Dice < 0.1) -> correct (Dice >= t_good) -> under_segmentation
#      (recall < precision - delta) -> over_segmentation (precision < recall - delta)
#      -> boundary_error (rest). Thresholds from cfg['evaluation']['failure_thresholds'],
#      fixed on the VALIDATION set before the test set is evaluated.
#   2. Axis B - nodule context, multi-label: small (< 6 mm), vessel_adjacent (Frangi
#      vesselness heuristic in a 2-5 mm ring; validate on ~50 manually reviewed nodules),
#      pleural_adjacent (GT boundary < 2 mm from closed lung-mask boundary), plus texture
#      and radiologist agreement from metadata.
#   3. Export crosstab A x B, per-group panels (CT | GT | Pred | Overlay [+ attention
#      map]) selected by a FIXED rule (median + worst cases), never hand-picked.
#   4. Outputs: results/failure_cases/{summary_by_error_type,crosstab_error_x_context,
#      vessel_label_review}.csv and <group>/<nodule_id>.png.
