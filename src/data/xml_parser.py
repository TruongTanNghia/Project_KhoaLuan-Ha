"""LIDC-IDRI XML annotation parser.

Responsibility
--------------
Parse one LIDC XML file into typed Python objects. No geometry or
consensus logic here — only faithful extraction of what radiologists drew.

Planned public API
------------------
@dataclass RoiContour: z_position, sop_uid, inclusion (bool), points [(x, y), ...]
@dataclass ReaderNodule: reader_index, nodule_id, rois, characteristics (dict|None)
@dataclass ReaderSmallNodule / ReaderNonNodule: centroid only
@dataclass LidcReadMessage: study_uid, series_uid, sessions: list[ReadingSession]
parse_lidc_xml(path: Path) -> LidcReadMessage | None   # None for non-CT XML

Status: NOT IMPLEMENTED — scheduled for PHASE 04.
"""

# TODO(PHASE 04):
#   1. Detect the XML namespace from the root tag instead of hard-coding it.
#   2. Root 'LidcReadMessage' = CT read; other roots (e.g. CXR reads) -> skip + log.
#   3. One <readingSession> per radiologist (up to 4). Reader identity is anonymous.
#   4. <unblindedReadNodule> with >1 edgeMap point and <characteristics> = nodule >= 3 mm;
#      single-point ROI without characteristics = nodule < 3 mm (centroid only).
#   5. <inclusion>FALSE</inclusion> marks an EXCLUSION contour (a hole) — keep the flag.
#   6. Store characteristics as-is, including 'malignancy' (1-5). This is a SUBJECTIVE
#      radiologist rating, NOT a pathological diagnosis: never use it as a cancer label.
#   7. Save per-file output to data/interim/annotations/<series_uid>.json.
