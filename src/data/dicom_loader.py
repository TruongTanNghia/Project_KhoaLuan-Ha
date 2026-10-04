"""DICOM CT series reader.

Responsibility
--------------
Load one CT series into a 3D volume with correct slice order and the
geometry needed to map XML annotations to voxels.

Planned public API
------------------
@dataclass CTVolume: raw (np.int16 [Z,Y,X]), spacing_zyx_mm, origin_xyz,
    z_positions, sop_instance_uids, rescale_slope, rescale_intercept,
    patient_id, study_uid, series_uid
load_ct_series(series_dir: Path) -> CTVolume
find_ct_series(raw_dir: Path) -> list[Path]

Status: NOT IMPLEMENTED — scheduled for PHASE 03.
"""

# TODO(PHASE 03):
#   1. Sort slices by ImagePositionPatient[2], NOT by InstanceNumber or file name
#      (InstanceNumber ordering is unreliable in some LIDC series).
#   2. Derive slice spacing from consecutive z positions; SliceThickness may differ
#      from the actual spacing (overlapping reconstructions).
#   3. Keep the raw stored values; HU conversion is done in hu_converter (PHASE 08).
#   4. Build sop_uid -> slice_index map: LIDC XML ROIs reference imageSOP_UID.
#   5. Raise a clear error for mixed series / inconsistent Rows x Columns.
#   6. Unit test with a synthetic pydicom dataset in tests/test_dicom.py.
