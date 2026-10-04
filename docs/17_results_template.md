# 17 — Results Template

> **Quy tắc tuyệt đối:** mọi ô "—" chỉ được điền bằng giá trị sinh tự động từ file nguồn ghi ở mỗi bảng. Mỗi bảng trong khóa luận ghi chú nguồn (`results/metrics/...`) và `run_id`. Không làm tròn "cho đẹp"; dùng 3 chữ số thập phân cho Dice/IoU/Precision/Recall, 2 chữ số cho HD95 (mm).

## R1. Thống kê dữ liệu
Nguồn: `data/interim/validation_report.json`, `data/interim/annotations/nodules.csv`, `data/splits/split_manifest.json`

| | Giá trị |
|---|---|
| Bệnh nhân có series CT hợp lệ | — |
| Series CT hợp lệ | — |
| Nốt vật lý ≥ 3 mm (≥ 1 bác sĩ) | — |
| Nốt theo số bác sĩ đánh dấu: 1 / 2 / 3 / 4 | — / — / — / — |
| Nốt dương sau majority ≥ 2/4 | — |

| | Train | Val | Test |
|---|---|---|---|
| Bệnh nhân | — | — | — |
| Nốt dương | — | — | — |
| Patch dương / âm | — | — | — |
| Đường kính nốt, trung vị (IQR) mm | — | — | — |

## R2. Mốc tham chiếu con người (tập test)
Nguồn: `results/metrics/inter_observer_reference.csv`

| | Dice trung vị (IQR) | n cặp |
|---|---|---|
| Giữa từng cặp bác sĩ | — | — |
| Leave-one-reader-out | — | — |

## R3. Kết quả chính (test, theo nốt, mean ± std qua 3 seed)
Nguồn: `results/metrics/experiments_summary.csv`

| Experiment | Dice | IoU | Precision | Recall | HD95 (mm) | Dice CI 95% (bootstrap) | best_epoch |
|------------|------|-----|-----------|--------|-----------|-------------------------|------------|
| EXP-01 U-Net + BCE | — | — | — | — | — | — | — |
| EXP-02 U-Net + BCE+Dice | — | — | — | — | — | — | — |
| EXP-03 Att U-Net + BCE | — | — | — | — | — | — | — |
| EXP-04 Att U-Net + BCE+Dice | — | — | — | — | — | — | — |

Ghi chú bắt buộc: số nốt test; số ca HD95 không xác định ở mỗi experiment.

## R4. Kiểm định thống kê
Nguồn: `results/metrics/statistical_tests.csv`

| So sánh | Δ Dice trung vị [CI 95%] | Wilcoxon p | p (Holm) | Kết luận |
|---------|--------------------------|------------|----------|----------|
| EXP-03 vs EXP-01 (attention, BCE) | — | — | — | — |
| EXP-04 vs EXP-02 (attention, BCE+Dice) | — | — | — | — |
| EXP-02 vs EXP-01 (loss, U-Net) | — | — | — | — |
| EXP-04 vs EXP-03 (loss, Att U-Net) | — | — | — | — |

## R5. Ablation bổ sung
Nguồn: `results/metrics/experiments_summary.csv` (ABL-*) — xem [12](12_ablation_study.md)

## R6. Phân tầng
Nguồn: `results/metrics/stratified_results.csv`

| Nhóm | n nốt | EXP-01 Dice | EXP-04 Dice | Δ |
|------|-------|-------------|-------------|---|
| 3–6 mm | — | — | — | — |
| 6–10 mm | — | — | — | — |
| 10–20 mm | — | — | — | — |
| ≥ 20 mm | — | — | — | — |
| Đặc / Bán đặc / Kính mờ | — | — | — | — |
| Đồng thuận 2 / 3 / 4 bác sĩ | — | — | — | — |
| Sát màng phổi / không | — | — | — | — |

## R7. Phát hiện thứ cấp (sliding window, test)
Nguồn: `results/metrics/detection_results.csv`

| Model | Per-nodule sensitivity | FP/scan | FP trùng nốt < 3 mm, non-nodule, nốt 1 phiếu |
|-------|------------------------|---------|----------------------------------------------|
| — | — | — | — |

## R8. Failure analysis
Nguồn: `results/failure_cases/summary_by_error_type.csv`, `crosstab_error_x_context.csv`

| Loại lỗi | EXP-01 % | EXP-04 % |
|----------|----------|----------|
| Correct | — | — |
| Under-segmentation | — | — |
| Over-segmentation | — | — |
| Missed | — | — |
| Boundary error | — | — |

## R9. Hình bắt buộc
| Hình | Nguồn |
|------|-------|
| Đường cong loss/Dice train–val của 4 experiment (seed 42) | `results/curves/` |
| Panel CT / GT / Prediction / Overlay cho các ca chọn theo quy tắc | `results/overlays/` |
| Boxplot Dice theo nốt của 4 experiment | sinh từ per-nodule CSV |
| Dice theo nhóm kích thước (có error bar) | sinh từ stratified CSV |
| Ví dụ từng nhóm lỗi + attention map | `results/failure_cases/` |

## R10. Mẫu câu diễn giải

- Đúng: "Trên tập test gồm *n* nốt của *m* bệnh nhân, EXP-04 đạt Dice theo nốt *x ± s* (3 seed). Chênh lệch so với EXP-02 là *Δ* [CI], p (Holm) = *p*."
- Đúng (kết quả âm tính): "Không có bằng chứng cho thấy attention gate cải thiện Dice trong điều kiện thí nghiệm này (p = …)."
- **Sai:** "Model đạt độ chính xác 99%." · "Model chẩn đoán ung thư phổi với độ chính xác …" · "Vượt các nghiên cứu trước."
