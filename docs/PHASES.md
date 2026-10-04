# Phase tracker

> Roadmap nghiên cứu (R1–R12) và quality gate chi tiết: [20_roadmap_and_quality_gates.md](20_roadmap_and_quality_gates.md). Mục lục tài liệu: [README.md](README.md).

Chỉ chuyển sang phase tiếp theo khi **tiêu chí hoàn thành** của phase hiện tại
đã đạt và đã được kiểm chứng bằng lệnh/test tương ứng.
Nếu phát hiện vấn đề về dataset/annotation: **DỪNG**, ghi vào
`docs/DATA_ASSUMPTIONS.md`, không tiếp tục sang training.

| Phase | Nội dung | Module chính | Tiêu chí hoàn thành | Trạng thái |
|-------|----------|--------------|---------------------|------------|
| 00 | Project initialization | `src/utils/{io,logger,seed}.py` | `python scripts/00_check_project.py` → exit 0; `pytest` pass | ✅ DONE (2026-10-04) |
| 01 | Environment + dependencies | `requirements.txt` | venv sạch, `pip install -r` thành công, import + CUDA check | ⏳ |
| 02 | Raw dataset validation | `src/data/data_validator.py` | Báo cáo validation không có blocking error; số liệu thực tế được ghi lại | ⏳ |
| 03 | DICOM reader | `src/data/dicom_loader.py` | Thứ tự slice/spacing đúng trên dữ liệu thật + test tổng hợp | ⏳ |
| 04 | XML annotation parser | `src/data/xml_parser.py` | Parse 100% file XML CT; thống kê số reader/nodule | ⏳ |
| 05 | Annotation → contour | `src/data/annotation_processor.py` | 100% ROI khớp được slice; báo cáo gom cụm | ⏳ |
| 06 | Contour → binary mask | `src/data/mask_generator.py` | Test consensus pass; metadata đủ các cột bắt buộc | ⏳ |
| 07 | Visualization CT + contour + mask | `src/evaluation/visualization.py` | Kiểm tra trực quan ≥ 20 nodule ngẫu nhiên: contour khớp mask | ⏳ |
| 08 | HU conversion | `src/data/hu_converter.py` | Histogram HU hợp lý (không khí ≈ −1000) | ⏳ |
| 09 | Windowing + normalization | `src/data/preprocessing.py` | Giá trị nằm trong [0, 1]; hình ảnh kiểm tra | ⏳ |
| 10 | ROI / cropping | `src/data/preprocessing.py` | Patch chứa đúng nodule; tỉ lệ âm/dương đúng config | ⏳ |
| 11 | Patient-level split | `src/data/dataset_split.py` | Không trùng bệnh nhân giữa các tập (assert) | ⏳ |
| 12 | Dataset / DataLoader | `src/datasets/lung_nodule_dataset.py` | Shape/dtype đúng; lặp hết 1 epoch | ⏳ |
| 13 | Augmentation | `src/datasets/lung_nodule_dataset.py` | Mask và ảnh biến đổi đồng bộ (hình kiểm tra) | ⏳ |
| 14 | U-Net baseline | `src/models/unet.py` | Forward shape đúng; overfit được 1 batch | ⏳ |
| 15 | Loss functions | `src/losses/*` | Unit test giá trị loss trên ví dụ biết trước | ⏳ |
| 16 | Training pipeline | `src/training/trainer.py` | Chạy hết vài epoch, có checkpoint + history | ⏳ |
| 17 | Validation | `src/training/*`, `src/metrics/*` | Early stopping + best checkpoint theo val_dice | ⏳ |
| 18 | Attention U-Net | `src/models/attention_unet.py` | Cùng hợp đồng với UNet; overfit 1 batch | ⏳ |
| 19 | Evaluation | `src/evaluation/evaluator.py` | `results/metrics/test_results.csv` sinh tự động | ⏳ |
| 20 | Ablation study | `experiments/*` | 4 experiment × ≥ 3 seed; bảng tổng hợp tự động | ⏳ |
| 21 | Failure-case analysis | `src/evaluation/failure_analysis.py` | 5 nhóm lỗi có ví dụ + thống kê | ⏳ |
| 22 | Inference | `src/inference/predict.py` | Chạy trên 1 series ngoài tập train | ⏳ |
| 23 | Demo application | `app/app.py` | Demo chạy cục bộ, có disclaimer | ⏳ |
