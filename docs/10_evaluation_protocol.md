# 10 — Evaluation Protocol

Code: `src/metrics/*`, `src/evaluation/evaluator.py` (PHASE 17, 19). Output: `results/metrics/`.

## 1. Nguyên tắc

1. **Tập test chỉ dùng một lần** cho mỗi cấu hình cuối cùng, sau khi mọi lựa chọn (checkpoint, τ, hậu xử lý) đã cố định trên validation.
2. **Không báo cáo một metric duy nhất.** Luôn báo cáo cùng lúc Dice, IoU, Precision, Recall và HD95.
3. **Metric được tính bằng code**, lưu ra CSV/JSON. Bảng trong khóa luận được sinh từ các file này, không chép tay.
4. Báo cáo **trung bình ± độ lệch chuẩn**, **trung vị (IQR)** và **khoảng tin cậy 95%**.

## 2. Metric phân đoạn

Ký hiệu: $P$ = mask dự đoán, $G$ = ground truth; TP, FP, FN tính theo pixel (voxel).

| Metric | Công thức | Ý nghĩa | Giá trị tốt | Hạn chế |
|--------|-----------|---------|-------------|---------|
| **Dice (DSC)** | $\frac{2TP}{2TP + FP + FN}$ | Mức trùng khớp vùng; trung bình điều hòa của precision và recall | → 1. Hãy đặt cạnh mức đồng thuận giữa các bác sĩ thay vì dùng ngưỡng tuyệt đối | **Rất nhạy với vật thể nhỏ**: lệch 1 pixel trên nốt 4 pixel làm Dice giảm mạnh. Không phản ánh sai số biên. Không xác định khi $P = G = \emptyset$ |
| **IoU (Jaccard)** | $\frac{TP}{TP + FP + FN}$ | Như Dice nhưng phạt nặng hơn | → 1. Luôn ≤ Dice | Liên hệ đơn điệu với Dice ($IoU = D/(2-D)$ trên từng mẫu), nên **không mang thông tin độc lập** khi tính trên từng mẫu. Báo cáo vì thông lệ |
| **Precision** | $\frac{TP}{TP + FP}$ | Bao nhiêu phần vùng dự đoán là đúng | Thấp = **over-segmentation** / FP | Không xác định khi $P = \emptyset$ |
| **Recall (Sensitivity)** | $\frac{TP}{TP + FN}$ | Bao nhiêu phần nốt được bao phủ | Thấp = **under-segmentation** / bỏ sót | Không xác định khi $G = \emptyset$ |
| **HD95 (mm)** | Phân vị 95 của khoảng cách đối xứng giữa hai biên | Sai số biên "gần xấu nhất", có loại bỏ ngoại lệ, theo **mm** | → 0; nên so với kích thước nốt và pixel spacing | Không xác định khi một mask rỗng. Với nốt rất nhỏ, HD95 bị chặn dưới bởi độ phân giải pixel |

**[NOT RECOMMENDED]** Pixel accuracy và specificity theo pixel: nền chiếm > 99% pixel, nên một model dự đoán toàn nền vẫn đạt > 0.99. Hai metric này gây hiểu lầm.

**[FACT]** *Metrics Reloaded* (Maier-Hein et al., 2024) khuyến nghị kết hợp một metric **chồng lấn** (Dice) với một metric **biên/khoảng cách** (ví dụ HD95, NSD) khi hình dạng và biên quan trọng. Đây là cơ sở chọn bộ metric trên.

### Tùy chọn có giá trị: Normalized Surface Dice (NSD)
Tỉ lệ biên nằm trong dung sai τ_mm (ví dụ 1 mm). Ít nhạy với kích thước hơn Dice. **Không bắt buộc.** Chỉ thêm nếu thời gian cho phép.

## 3. Đơn vị đánh giá

| Đơn vị | Cách tính | Vai trò |
|--------|-----------|---------|
| **Nốt (chính)** | Ghép dự đoán của mọi lát/patch thuộc cùng một nốt thành mask 3D cục bộ, rồi tính metric 3D trên nốt đó. HD95 dùng spacing (z, y, x) thật | **Báo cáo chính**. Mỗi nốt có trọng số bằng nhau, không để nốt lớn (nhiều lát) chi phối |
| Lát / patch dương | Metric 2D trên từng patch | Phụ; dùng cho early stopping và để so với các paper báo cáo theo lát |
| Patch âm | Tỉ lệ patch âm có dự đoán khác rỗng; diện tích FP trung bình | Đo FP. **Không** tính Dice trên patch âm |
| Bệnh nhân | Trung bình các nốt của một bệnh nhân | Dùng cho bootstrap CI (đơn vị độc lập) |

**[DECISION] Chính sách mask rỗng** (`evaluation.empty_gt_policy = report_separately`):
- GT khác rỗng, dự đoán rỗng: Dice = IoU = Recall = 0; Precision không xác định (ghi NaN, đếm riêng); HD95 = NaN, tính vào nhóm "missed nodule".
- GT rỗng (patch âm): **không** đưa vào trung bình Dice. Báo cáo riêng tỉ lệ FP.
- Báo cáo **số lượng NaN** cho mỗi metric. Trung bình HD95 chỉ tính trên các ca xác định được, và phải ghi rõ điều này.

## 4. Thống kê

| Mục | Phương pháp |
|-----|-------------|
| Khoảng tin cậy 95% | **Bootstrap theo bệnh nhân** (≥ 1000 lần lấy mẫu lại bệnh nhân, giữ nguyên các nốt của mỗi bệnh nhân), percentile CI |
| So sánh hai model | **Wilcoxon signed-rank theo cặp** trên Dice từng nốt (cùng nốt, hai model). Mỗi model lấy trung bình 3 seed cho mỗi nốt |
| Đa so sánh | Ablation 2 × 2 có nhiều cặp so sánh: hiệu chỉnh **Holm–Bonferroni** |
| Biến thiên do seed | Báo cáo mean ± std **giữa các seed** của Dice trung bình |
| Kích thước hiệu ứng | Chênh lệch trung vị Dice theo cặp + CI bootstrap của chênh lệch |

**[DECISION]** Chỉ kết luận "khác biệt có ý nghĩa" khi p (sau hiệu chỉnh) < 0.05 **và** chênh lệch > độ lệch chuẩn giữa các seed.

## 5. Phân tầng (stratified analysis)

Báo cáo metric theo nhóm:
- **Kích thước nốt:** [3, 6), [6, 10), [10, 20), ≥ 20 mm.
- **Texture:** đặc / bán đặc / kính mờ (trung vị điểm của các bác sĩ).
- **Mức đồng thuận:** radiologist_count = 2, 3, 4; `mean_pairwise_iou` theo tứ phân vị.
- **Vị trí:** sát màng phổi / không (heuristic, xem [13](13_failure_analysis.md)).
- **Slice thickness của scan:** ≤ 1.5 mm, (1.5, 2.5], > 2.5 mm.

## 6. Mốc tham chiếu con người

Tính trên **cùng tập test**:
- Dice giữa từng cặp bác sĩ trên các nốt có ≥ 2 annotation.
- (Tốt hơn) Leave-one-reader-out: Dice giữa bác sĩ *k* và đồng thuận của những người còn lại.

**[FACT]** iW-Net (Aresta et al., 2019) báo cáo IoU giữa các bác sĩ là 0.59 trên LIDC. Con số này cho thấy mức "trần" thực tế khác xa 1.0.

## 7. Đánh giá phát hiện thứ cấp (phương án B)

| Metric | Định nghĩa |
|--------|-----------|
| Per-nodule sensitivity | % nốt GT có ít nhất một thành phần dự đoán chồng lấn |
| FP/scan | Số thành phần dự đoán không khớp nốt GT nào, chia cho số scan |
| FP "có thể không phải lỗi" | Số FP trùng vị trí nốt < 3 mm, non-nodule, hoặc nốt chỉ 1 bác sĩ vẽ: báo cáo riêng |
| (Tùy chọn) FROC | Sensitivity theo FP/scan khi thay đổi ngưỡng điểm ứng viên (ví dụ xác suất cực đại của thành phần) |

**[LIMITATION]** Không so sánh trực tiếp với CPM của LUNA16: khác tập scan, khác tiêu chuẩn tham chiếu (≥ 3/4 so với ≥ 2/4), khác định nghĩa "trúng".

## 8. Đầu ra bắt buộc

```
results/metrics/
├── <exp>_s<seed>_test_per_nodule.csv    patient_id, nodule_id, size, texture, dice, iou, precision, recall, hd95, ...
├── <exp>_s<seed>_test_per_patch.csv
├── <exp>_s<seed>_test_negatives.csv
├── test_results.csv                     một dòng / (exp, seed): mean, std, median, CI
├── experiments_summary.csv              tổng hợp 4 experiment × 3 seed (bảng chính)
├── statistical_tests.csv                cặp so sánh, thống kê, p, p_holm
├── stratified_results.csv
└── inter_observer_reference.csv
```

## Tham khảo
- Maier-Hein L. et al. (2024). Metrics reloaded. *Nature Methods*, 21(2), 195–212. doi:10.1038/s41592-023-02151-z
- Taha A.A., Hanbury A. (2015). Metrics for evaluating 3D medical image segmentation. *BMC Medical Imaging*, 15, 29. [VERIFY REQUIRED]
- Aresta G. et al. (2019). iW-Net. *Scientific Reports*, 9, 11591. doi:10.1038/s41598-019-48004-8
