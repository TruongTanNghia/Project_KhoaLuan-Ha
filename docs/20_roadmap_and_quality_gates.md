# 20 — Research Roadmap & Quality Gates

Roadmap nghiên cứu gồm 12 phase. Mỗi phase ánh xạ sang các phase triển khai code (PHASE 00–23 trong [PHASES.md](PHASES.md)).
**Quy tắc:** chỉ sang phase tiếp theo khi **mọi** ô trong gate của phase hiện tại đã được tick, kèm bằng chứng (lệnh, file, hình). Gate không đạt thì **DỪNG**, ghi vấn đề vào [DATA_ASSUMPTIONS.md](DATA_ASSUMPTIONS.md).

## Tổng quan

```
R1 Literature ─► R2 Dataset ─► R3 Annotation ─► R4 Preprocessing ─► R5 Baseline ─► R6 Improved model
                                                                                        │
R12 Defense ◄─ R11 Thesis writing ◄─ R10 Demo ◄─ R9 Analysis ◄─ R8 Evaluation ◄─ R7 Experiments
(chương 3 viết song song từ R2)
```

| Research phase | Nội dung | Code phase | Tài liệu | Sản phẩm |
|----------------|----------|-----------|----------|----------|
| **R1 Literature** | Đọc và xác minh tài liệu; chốt câu hỏi nghiên cứu | — | [02](02_literature_review.md) | Bảng tài liệu đã xác minh |
| **R2 Dataset** | Tải, kiểm tra dữ liệu; đọc DICOM | 00–03 | [03](03_dataset_specification.md) | `validation_report.json` |
| **R3 Annotation** | XML → nốt → contour → mask đồng thuận; QC | 04–07 | [04](04_annotation_pipeline.md) | `nodules.csv`, mask GT, hình QC |
| **R4 Preprocessing** | HU, window, lung ROI, patch, split, Dataset, augmentation | 08–13 | [05](05_preprocessing_pipeline.md), [06](06_dataset_construction.md) | `data/processed/`, `data/splits/` |
| **R5 Baseline** | U-Net, loss, trainer, validation | 14–17 | [07](07_unet_baseline.md), [09](09_training_strategy.md) | EXP-01 seed 42 |
| **R6 Improved model** | Attention U-Net | 18 | [08](08_proposed_model.md) | Model đã test |
| **R7 Experiments** | 4 cấu hình × 3 seed + ablation bổ sung | 16–20 | [11](11_experiment_plan.md), [12](12_ablation_study.md) | 12+ run có đủ vết |
| **R8 Evaluation** | Đánh giá test, thống kê, phát hiện thứ cấp | 19 | [10](10_evaluation_protocol.md) | `results/metrics/*` |
| **R9 Analysis** | Phân tầng, failure analysis, mốc tham chiếu con người | 20–21 | [13](13_failure_analysis.md) | `results/failure_cases/*` |
| **R10 Demo** | Inference + ứng dụng | 22–23 | [16](16_demo_application.md) | `app/` chạy được |
| **R11 Thesis writing** | 5 chương + phụ lục | — | [18](18_thesis_structure.md), [17](17_results_template.md) | Bản thảo khóa luận |
| **R12 Defense** | Slide, demo, câu hỏi | — | [19](19_defense_questions.md) | Slide + kịch bản demo |

---

## Quality gates

### R1 — LITERATURE GATE
- [ ] Mọi tài liệu trích dẫn đã mở DOI và đối chiếu tác giả, năm, venue
- [ ] Mọi số liệu trích dẫn có trong abstract/toàn văn (ghi trang/bảng)
- [ ] Không còn mục [VERIFY REQUIRED] nào được dùng trong khóa luận
- [ ] Câu hỏi nghiên cứu và giả thuyết H1–H6 đã chốt ([11](11_experiment_plan.md))

### R2 — DATASET GATE
- [ ] Dataset tải đủ; số bệnh nhân/series/XML thực tế được ghi lại và so với số công bố
- [ ] Mọi file DICOM đọc được (danh sách lỗi = rỗng hoặc đã giải thích)
- [ ] Mọi file XML CT đọc được
- [ ] Patient ID hợp lệ (định dạng `LIDC-IDRI-XXXX`), không trùng lặp
- [ ] Chỉ series Modality = CT được giữ
- [ ] Thứ tự lát và spacing kiểm tra đúng (test + kiểm tra trên dữ liệu thật)
- [ ] `00_check_project.py` và `pytest` đạt

### R3 — ANNOTATION GATE
- [ ] 100% ROI của nốt ≥ 3 mm ánh xạ được tới lát cắt
- [ ] Gom cụm hợp lý: phân bố `radiologist_count` so được với số công bố; cụm `ambiguous` đã xem xét
- [ ] Contour inclusion=FALSE được xử lý (có ít nhất một ca kiểm tra trực quan)
- [ ] QC trực quan ≥ 20 nốt ngẫu nhiên: contour khớp ảnh, x/y không đảo, đúng lát
- [ ] Đối chiếu pylidc trên mẫu ngẫu nhiên: sai khác đã giải thích được
- [ ] Metadata có đủ cột bắt buộc ([04](04_annotation_pipeline.md) mục 2.6)
- [ ] Báo cáo bất đồng giữa các bác sĩ đã sinh ra

### R4 — PREPROCESSING & DATASET GATE
- [ ] Histogram HU hợp lý ở mọi series (đỉnh khí ≈ −1000)
- [ ] Ảnh sau chuẩn hóa nằm trong [0, 1]
- [ ] 100% tâm nốt GT nằm trong mask phổi (sau closing), hoặc ngoại lệ đã ghi log
- [ ] Patch dương chứa đúng nốt; patch âm không chứa tổn thương nào trong XML
- [ ] **Không trùng bệnh nhân giữa train/val/test** (assert tự động)
- [ ] Thống kê các tập tương đồng (bảng R1)
- [ ] Augmentation: ảnh và mask biến đổi đồng bộ (hình kiểm tra)
- [ ] `dataset_version` và `manifest.json` đã ghi; split đã commit

### R5 — TRAINING GATE (baseline)
- [ ] Forward shape đúng; số tham số và VRAM đã ghi lại
- [ ] Overfit 1 batch đạt Dice ≈ 1
- [ ] Loss giảm ổn định; không có NaN
- [ ] Validation ổn định; early stopping hoạt động
- [ ] Checkpoint best và last được lưu, resume được
- [ ] `history.csv`, `resolved_config.yaml`, `run_info.json` đầy đủ
- [ ] Split được kiểm tra lại lúc bắt đầu huấn luyện

### R6 — IMPROVED MODEL GATE
- [ ] Attention U-Net có cùng giao diện với UNet; chỉ khác ở attention gate
- [ ] `00_check_project.py`: không có ablation leak
- [ ] Overfit 1 batch đạt
- [ ] Số tham số của hai model đã ghi lại

### R7 — EXPERIMENT GATE
- [ ] 4 cấu hình × 3 seed hoàn tất (hoặc cắt giảm theo thứ tự ưu tiên ở [11](11_experiment_plan.md) mục 4, và ghi lại)
- [ ] Mọi run cùng `dataset_version`, cùng split, git tree sạch
- [ ] Chọn checkpoint và τ **chỉ** trên validation
- [ ] Kiểm tra tái lập: chạy lại EXP-01 seed 42, chênh lệch nhỏ hơn std giữa các seed

### R8 — EVALUATION GATE
- [ ] Tập test chưa từng được dùng cho bất kỳ lựa chọn nào
- [ ] Metric được tính tự động; CSV/JSON đã sinh
- [ ] Báo cáo đủ Dice, IoU, Precision, Recall, HD95 (kèm số ca NaN)
- [ ] Khoảng tin cậy bootstrap theo bệnh nhân
- [ ] Kiểm định Wilcoxon + Holm cho các cặp so sánh
- [ ] Mốc tham chiếu con người đã tính trên cùng tập test
- [ ] Đánh giá phát hiện thứ cấp (nếu thực hiện phương án B)

### R9 — ANALYSIS GATE
- [ ] Ngưỡng gán nhóm lỗi đã chốt trên validation trước khi chạy test
- [ ] Bảng chéo loại lỗi × đặc điểm nốt
- [ ] Ví dụ định tính chọn theo quy tắc cố định
- [ ] Heuristic vessel-adjacent đã kiểm tra tay trên mẫu
- [ ] Mỗi giả thuyết H1–H6 có kết luận: chấp nhận / bác bỏ / không đủ bằng chứng

### R10 — DEMO GATE
- [ ] Demo dùng chung code tiền xử lý và inference với pipeline đánh giá
- [ ] Không hiển thị Dice/IoU cho ca không có GT; không có "confidence" chưa hiệu chỉnh
- [ ] Số đo tính từ mask, nhất quán về hình học
- [ ] Disclaimer luôn hiển thị
- [ ] Chạy được trên máy bảo vệ (đã thử)

### R11 — THESIS GATE
- [ ] Mọi bảng và hình kết quả có nguồn file và run_id
- [ ] Thuật ngữ nhất quán: "nốt phổi"; không có "chẩn đoán ung thư"
- [ ] Phân biệt rõ FACT / HYPOTHESIS / RESULT / LIMITATION trong văn bản
- [ ] Mục hạn chế đầy đủ ([15](15_ethics_and_limitations.md))
- [ ] Tóm tắt có số liệu thật
- [ ] Trích dẫn dataset (DOI TCIA) và Armato et al. 2011

### R12 — DEFENSE GATE
- [ ] Slide: bài toán → dữ liệu → GT → phương pháp → kết quả (có CI) → lỗi → hạn chế
- [ ] Đã luyện trả lời 38 câu trong [19](19_defense_questions.md), đã điền số liệu thật
- [ ] Demo chạy offline; có video dự phòng
- [ ] Không còn hình nào chứa số liệu minh họa (ví dụ các bản phác thảo trong `img-demo/`)
