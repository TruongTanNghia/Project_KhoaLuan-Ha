"""Raw LIDC-IDRI dataset validation (run BEFORE any processing).

Responsibility
--------------
Verify that the downloaded TCIA folder is complete and usable, and
produce a machine-readable report. If a blocking problem is found the
pipeline must STOP (cfg['data_validation']['on_error'] == 'stop').

Planned public API
------------------
validate_raw_dataset(cfg) -> ValidationReport
ValidationReport.to_csv(path) / .to_json(path) / .has_blocking_errors

Status: NOT IMPLEMENTED — scheduled for PHASE 02.
"""

# TODO(PHASE 02):
#   1. Walk cfg['paths']['raw_dir'] (layout: LIDC-IDRI-XXXX/<study>/<series>/*.dcm + *.xml).
#   2. Read headers only (pydicom.dcmread(stop_before_pixels=True)) for speed.
#   3. Per series record: patient_id, study_uid, series_uid, modality, n_slices,
#      pixel spacing, slice spacing (from ImagePositionPatient), rows/cols, has_xml.
#   4. Flag: non-CT series (LIDC also contains CR/DX chest radiographs), series with
#      < min_slices_per_series, non-uniform slice spacing, duplicated z positions,
#      missing XML, unreadable files, patients without any CT series.
#   5. Write results/metrics/raw_data_validation.csv + data/interim/validation_report.json.
#   6. Report the counts actually observed (patients, CT series, XML files) — do not
#      assume the published numbers; compare and document any difference.
