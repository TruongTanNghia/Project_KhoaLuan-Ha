# Bộ tài liệu kỹ thuật — Phân đoạn nốt phổi trên CT bằng U-Net (LIDC-IDRI)

Bộ tài liệu này là **nguồn sự thật duy nhất (single source of truth)** cho phần phương pháp
của khóa luận. Code (`src/`, `configs/`) phải khớp với tài liệu. Khi một quyết định thay đổi,
sửa tài liệu **trước**, rồi mới sửa code và ghi vào nhật ký ở [DATA_ASSUMPTIONS.md](DATA_ASSUMPTIONS.md).

## Quy ước nhãn nhận định

Mọi nhận định quan trọng đều được gắn một trong các nhãn sau. Khi viết khóa luận, giữ nguyên
sự phân biệt này (có thể đổi sang văn phong học thuật, nhưng không được biến giả thuyết thành sự thật).

| Nhãn | Ý nghĩa | Ví dụ |
|------|---------|-------|
| **[FACT]** | Đã được công bố trong nguồn tin cậy (có trích dẫn) hoặc là định nghĩa toán học/vật lý. | HU của nước = 0. |
| **[ASSUMPTION]** | Điều ta tin là đúng nhưng **chưa kiểm chứng** trên dữ liệu của chính project. | Mọi scan đều có đúng 4 phiên đọc. |
| **[DECISION]** | Lựa chọn thiết kế của project, kèm lý do. Có thể thay đổi nếu có bằng chứng mới. | Ground truth = majority ≥ 2/4. |
| **[HYPOTHESIS]** | Giả thuyết nghiên cứu, cần thực nghiệm để chấp nhận hoặc bác bỏ. | Attention gate cải thiện Dice trên nodule < 6 mm. |
| **[RESULT]** | Kết quả thực nghiệm sinh ra **bởi pipeline của project**, có đường dẫn file nguồn. | *(chưa có)* |
| **[LIMITATION]** | Giới hạn đã biết của dữ liệu, phương pháp hoặc đánh giá. | Model 2D bỏ qua ngữ cảnh giữa các lát cắt. |
| **[VERIFY REQUIRED]** | Thông tin trích dẫn chưa được xác minh trên nguồn gốc. **Không** đưa vào khóa luận khi chưa xác minh. | |
| **[NOT RECOMMENDED]** | Phương án advisor khuyến nghị không làm, kèm lý do. | Resize toàn slice 512 → 256. |

## Mục lục

| # | Tài liệu | Trả lời câu hỏi | Phase code liên quan |
|---|----------|-----------------|----------------------|
| 00 | [Project overview](00_project_overview.md) | Làm gì, vì sao, phạm vi đến đâu? | — |
| 01 | [Problem definition](01_problem_definition.md) | Bài toán được định nghĩa hình thức như thế nào? | — |
| 02 | [Literature review](02_literature_review.md) | Người khác đã làm gì, ta đứng ở đâu? | — |
| 03 | [Dataset specification](03_dataset_specification.md) | LIDC-IDRI gồm những gì? | 02–03 |
| 04 | [Annotation pipeline](04_annotation_pipeline.md) | XML → contour → mask, gộp nhiều bác sĩ ra sao? | 04–07 |
| 05 | [Preprocessing pipeline](05_preprocessing_pipeline.md) | HU, window, ROI, crop, augmentation | 08–10, 13 |
| 06 | [Dataset construction](06_dataset_construction.md) | Mẫu huấn luyện, chia tập, chống leakage | 10–12 |
| 07 | [U-Net baseline](07_unet_baseline.md) | Kiến trúc baseline | 14 |
| 08 | [Proposed model](08_proposed_model.md) | Attention U-Net và lý do chọn | 18 |
| 09 | [Training strategy](09_training_strategy.md) | Protocol huấn luyện, loss | 15–17 |
| 10 | [Evaluation protocol](10_evaluation_protocol.md) | Metric, đơn vị đánh giá, thống kê | 19 |
| 11 | [Experiment plan](11_experiment_plan.md) | Ma trận thực nghiệm EXP-01..04 | 16–20 |
| 12 | [Ablation study](12_ablation_study.md) | Thành phần nào thực sự đóng góp? | 20 |
| 13 | [Failure analysis](13_failure_analysis.md) | Model sai ở đâu, vì sao? | 21 |
| 14 | [Reproducibility](14_reproducibility.md) | Người khác chạy lại được không? | toàn bộ |
| 15 | [Ethics & limitations](15_ethics_and_limitations.md) | Giới hạn và đạo đức | — |
| 16 | [Demo application](16_demo_application.md) | Demo hiển thị gì và không được hiển thị gì? | 22–23 |
| 17 | [Results template](17_results_template.md) | Kết quả trình bày theo khung nào? | 19–21 |
| 18 | [Thesis structure](18_thesis_structure.md) | Khóa luận gồm những chương, hình, bảng gì? | — |
| 19 | [Defense questions](19_defense_questions.md) | Hội đồng sẽ hỏi gì? | — |
| 20 | [Roadmap & quality gates](20_roadmap_and_quality_gates.md) | Làm theo thứ tự nào, khi nào được đi tiếp? | toàn bộ |

Tài liệu vận hành (cập nhật trong quá trình làm):

- [PHASES.md](PHASES.md): tiến độ 24 phase triển khai code (PHASE 00–23).
- [DATA_ASSUMPTIONS.md](DATA_ASSUMPTIONS.md): sổ giả định và quyết định về dữ liệu, có nhật ký thay đổi.

## Đọc theo mục đích

- **Triển khai code:** 03 → 04 → 05 → 06 → 07 → 09 → 10 → 14, kèm PHASES.md.
- **Viết khóa luận:** 00 → 01 → 02 → 18, sau đó lấy nội dung từng chương từ 03–13.
- **Chuẩn bị bảo vệ:** 19 → 15 → 12 → 10.
