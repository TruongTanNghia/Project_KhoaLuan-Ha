"""Test-set evaluation and experiment summary.

Responsibility
--------------
Load the best checkpoint, predict on the test split and compute all metrics
per sample, per nodule and aggregated.

Planned public API
------------------
evaluate(cfg, checkpoint_path, split='test') -> dict
summarize_experiments(experiments_dir) -> results/metrics/experiments_summary.csv

Status: NOT IMPLEMENTED — scheduled for PHASE 19.
"""

# TODO(PHASE 19):
#   1. Per-sample rows -> results/metrics/<exp>_test_per_sample.csv (with patient_id,
#      nodule_id, nodule_size_mm, radiologist_count for stratified analysis).
#   2. Aggregates (mean, std, median, 95% CI via bootstrap over PATIENTS) ->
#      results/metrics/test_results.csv and <exp_dir>/summary.json.
#   3. Report Dice, IoU, Precision, Recall, HD95 together — never a single metric.
#   4. Report negative (empty-GT) samples separately: false-positive rate on them.
#   5. Stratify results by nodule size bin and by radiologist agreement level.
