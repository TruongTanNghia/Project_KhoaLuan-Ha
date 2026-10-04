# 11 — Experiment Plan

Config: `experiments/exp0X_*/config.yaml`. Kiểm tra công bằng tự động: `python scripts/00_check_project.py` báo lỗi nếu các experiment khác nhau ở bất kỳ điểm nào ngoài kiến trúc và loss.

## 1. Câu hỏi và giả thuyết nghiên cứu

| ID | Giả thuyết | Kiểm tra bằng |
|----|-----------|---------------|
| **H1** | Attention gate cải thiện Dice theo nốt so với U-Net cùng cấu hình | EXP-01 vs EXP-03; EXP-02 vs EXP-04 |
| H1b | Cải thiện (nếu có) đến chủ yếu từ việc tăng Precision (giảm FP ở mạch máu) | Precision trong cùng các cặp |
| **H2** | BCE + Dice cải thiện Dice và Recall so với BCE, vì giảm ảnh hưởng mất cân bằng lớp | EXP-01 vs EXP-02; EXP-03 vs EXP-04 |
| H3 | Hiệu ứng của attention và Dice loss **cộng dồn** (không có tương tác) | So sánh 4 ô của ma trận 2 × 2 |
| H4 | Augmentation hình học nhẹ cải thiện tổng quát hóa | Ablation bổ sung ([12](12_ablation_study.md)) |
| H5 | Nốt kính mờ và nốt < 6 mm có Dice thấp hơn rõ rệt ở mọi model | Phân tích phân tầng |
| H6 | Dice của model trên test nằm trong khoảng Dice giữa các bác sĩ | Mốc tham chiếu con người |

## 2. Ma trận thực nghiệm

Cấu hình chung cho cả 4 experiment: `dataset_version`, split, patch 128, batch 16, AdamW 3e-4, cosine, 100 epoch tối đa, early stopping 15, augmentation mặc định, τ = 0.5. Seeds: **42, 1, 2**.

### EXP-01 — U-Net + BCE (baseline)
| Mục | Nội dung |
|-----|----------|
| **Hypothesis** | Là điểm tham chiếu; không có giả thuyết riêng. Kỳ vọng Precision cao hơn Recall, vì BCE có xu hướng dự đoán thiên về nền |
| **Configuration** | `model.name=unet`, `loss.name=bce` |
| **Expected comparison** | Mốc cho EXP-02 (tác động loss) và EXP-03 (tác động attention) |
| **Actual result** | *Chưa có. Sinh tự động từ `results/metrics/experiments_summary.csv`* |
| **Conclusion** | *Chưa có* |

### EXP-02 — U-Net + BCE + Dice
| Mục | Nội dung |
|-----|----------|
| **Hypothesis** | H2: Dice và Recall tăng so với EXP-01 |
| **Configuration** | `model.name=unet`, `loss.name=bce_dice`, w = 0.5/0.5 |
| **Expected comparison** | vs EXP-01, chỉ khác loss |
| **Actual result** | *Chưa có* |
| **Conclusion** | *Chưa có* |

### EXP-03 — Attention U-Net + BCE
| Mục | Nội dung |
|-----|----------|
| **Hypothesis** | H1, H1b: Dice và Precision tăng so với EXP-01 |
| **Configuration** | `model.name=attention_unet`, `loss.name=bce` |
| **Expected comparison** | vs EXP-01, chỉ khác kiến trúc |
| **Actual result** | *Chưa có* |
| **Conclusion** | *Chưa có* |

### EXP-04 — Attention U-Net + BCE + Dice (phương pháp đề xuất)
| Mục | Nội dung |
|-----|----------|
| **Hypothesis** | H1 + H2 + H3: cấu hình tốt nhất trong 4 cấu hình |
| **Configuration** | `model.name=attention_unet`, `loss.name=bce_dice` |
| **Expected comparison** | vs EXP-02 (tác động attention khi đã có Dice loss), vs EXP-03 (tác động Dice loss khi đã có attention) |
| **Actual result** | *Chưa có* |
| **Conclusion** | *Chưa có* |

## 3. Quy tắc diễn giải (định trước)

1. **Hiệu ứng chính của attention** = trung bình của (EXP-03 − EXP-01) và (EXP-04 − EXP-02).
2. **Hiệu ứng chính của loss** = trung bình của (EXP-02 − EXP-01) và (EXP-04 − EXP-03).
3. **Tương tác** = (EXP-04 − EXP-03) − (EXP-02 − EXP-01). Nếu khác 0 đáng kể thì tác dụng của loss phụ thuộc vào kiến trúc.
4. Kết luận theo tiêu chí ở [08](08_proposed_model.md) mục 5 và [10](10_evaluation_protocol.md) mục 4.
5. **Kết quả âm tính được báo cáo đầy đủ.** "EXP-04 không tốt hơn EXP-02" là một phát hiện hợp lệ.

## 4. Ngân sách tính toán

| Hạng mục | Số lần chạy |
|----------|-------------|
| Ma trận chính | 4 cấu hình × 3 seed = **12** |
| Ablation bổ sung ([12](12_ablation_study.md)) | 2–4 |
| Smoke / overfit / debug | không tính |

**[ASSUMPTION]** Thời gian mỗi lần chạy chưa biết. Đo ở PHASE 16 (thời gian/epoch × số epoch trung bình), rồi cập nhật bảng này. Nếu tổng thời gian vượt ngân sách, ưu tiên theo thứ tự: (1) đủ 4 cấu hình × seed 42; (2) thêm seed cho EXP-01 và EXP-04; (3) thêm seed cho EXP-02 và EXP-03; (4) ablation bổ sung.

## 5. Những gì KHÔNG làm, và vì sao

| Đề xuất | Đánh giá |
|---------|----------|
| Thêm UNet++, TransUNet, nnU-Net | **[NOT RECOMMENDED]** Làm loãng câu hỏi nghiên cứu; không đủ tài nguyên để so sánh công bằng |
| Thêm Focal, Tversky vào ma trận | **[NOT RECOMMENDED]** Xem [09](09_training_strategy.md) mục 2; chỉ làm có điều kiện |
| Tinh chỉnh hyperparameter riêng cho từng model | **[NOT RECOMMENDED]** Làm lẫn hiệu ứng kiến trúc với hiệu ứng tinh chỉnh |
| Báo cáo seed tốt nhất | **[NOT RECOMMENDED]** Thiên lệch lựa chọn; luôn báo cáo mean ± std |
| Chạy test nhiều lần trong khi phát triển | **[NOT RECOMMENDED]** Leakage qua lựa chọn mô hình |
