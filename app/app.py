"""Demo application: upload a CT slice / series -> lung-nodule segmentation overlay.

Status: NOT IMPLEMENTED — scheduled for PHASE 23.

The demo must:
    * call src.inference.predict only (no model/preprocessing code here);
    * load the checkpoint path from a config file, never hard-coded;
    * show the disclaimer below on every page.
"""

DISCLAIMER = (
    "Research prototype. Output is a lung-NODULE segmentation, "
    "NOT a diagnosis of lung cancer. Not for clinical use."
)

# TODO(PHASE 23):
#   1. Choose the UI framework in PHASE 23 (Gradio or Streamlit) and add it to
#      requirements.txt.
#   2. Inputs: one DICOM series folder (zip) or one .dcm slice.
#   3. Pipeline: src.inference.predict.predict_series(...) -> overlay figure from
#      src.evaluation.visualization.
#   4. Display: original CT (lung window) | predicted mask | overlay, plus
#      per-candidate size (mm) and the model's probability — never "malignant".
