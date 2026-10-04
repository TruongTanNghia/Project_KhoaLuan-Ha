"""Figures: CT + contour + mask, predictions, overlays, training curves.

Responsibility
--------------
All plotting lives here so scripts and notebooks share the same figures.

Planned public API
------------------
show_ct_with_contours(hu_slice, reader_contours, gt_mask, window) -> Figure  # PHASE 07
plot_training_curves(history_csv, out_path)                              # PHASE 17
save_prediction_panel(image, gt, pred, out_path)  # Original|GT|Pred|Overlay  PHASE 19

Status: NOT IMPLEMENTED — scheduled for PHASE 07 (data figures), 17 (curves), 19 (prediction figures).
"""

# TODO(PHASE 07 (data figures), 17 (curves), 19 (prediction figures)):
#   1. PHASE 07: draw each reader's contour in a different colour on the windowed slice,
#      plus the consensus mask, to visually verify XML -> contour -> mask alignment
#      (x/y not swapped, correct slice, boundary handling).
#   2. Use matplotlib with the 'Agg' backend; save PNG at fixed DPI.
#   3. Overlay colours: GT = green, prediction = red, overlap = yellow; state this in legends.
