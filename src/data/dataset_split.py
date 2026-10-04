"""Patient-level train/val/test split (data-leakage prevention).

Responsibility
--------------
Assign every PATIENT (never an individual slice/patch) to exactly one of
train / val / test, so that slices of one patient never appear in two sets.

Planned public API
------------------
split_patients(patient_table, ratios, stratify_by, seed) -> dict[str, list[str]]
assert_no_patient_overlap(splits) -> None
write_split_files(splits, splits_dir) -> None

Status: NOT IMPLEMENTED — scheduled for PHASE 11.
"""

# TODO(PHASE 11):
#   1. Input: one row per patient (patient_id, n_nodules, size bin) from metadata.
#   2. Stratify by nodule_size_bin (and has-nodule vs. no-nodule) with a seeded RNG.
#   3. Write data/splits/{train,val,test}.csv (patient_id + summary columns) and
#      data/splits/split_manifest.json (seed, ratios, counts, dataset_version).
#   4. Hard assertion: the three patient sets are pairwise disjoint and cover all
#      patients; the training script must re-check this before every run.
#   5. The test split is frozen after creation: never tune anything on it.
