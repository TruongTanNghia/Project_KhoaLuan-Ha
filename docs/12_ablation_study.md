# 12 — Ablation Study

## 1. Phản biện thiết kế ablation dạng chuỗi

Yêu cầu ban đầu đề xuất một **chuỗi tích lũy**:

```
Baseline U-Net → + Dice loss → + Attention → + Augmentation → + Preprocessing strategy
```

**Không khuyến nghị dùng chuỗi tích lũy làm thiết kế chính.** Lý do:

| Vấn đề | Giải thích |
|--------|-----------|
| **Phụ thuộc thứ tự** | Đóng góp đo được của "+ Attention" là đóng góp *khi đã có Dice loss*. Đảo thứ tự có thể cho kết luận khác. Chuỗi không cho biết tương tác |
| **Baseline không sạch** | Nếu baseline đã có augmentation (cấu hình mặc định), thì bước "+ Augmentation" ở cuối chuỗi là không nhất quán |
| **"Preprocessing strategy" quá mơ hồ** | Không phải một biến mà là cả một họ lựa chọn (window, resample, lung mask…). Thay một lúc nhiều thứ thì không quy kết được nguyên nhân |
| **Chi phí** | 5 bước × 3 seed = 15 lần chạy, mà vẫn không trả lời được tương tác |
| **Thay đổi preprocessing = đổi dataset** | Phải tạo lại dữ liệu (tăng `dataset_version`) và đảm bảo cùng split. Chi phí lớn nhất trong mọi bước |

## 2. Thiết kế khuyến nghị

### 2.1 Lõi: thiết kế giai thừa 2 × 2 (đã có trong [11](11_experiment_plan.md))

|                     | BCE    | BCE + Dice |
|---------------------|--------|------------|
| **U-Net**           | EXP-01 | EXP-02     |
| **Attention U-Net** | EXP-03 | EXP-04     |

Cho biết **hiệu ứng chính** của từng thành phần **và** tương tác, với 4 cấu hình. Đây là cách hiệu quả nhất để trả lời "thành phần nào thực sự đóng góp".

### 2.2 Ablation bổ sung: một yếu tố mỗi lần, trên cấu hình tốt nhất

Chạy **sau** khi có kết quả 2 × 2 (chọn cấu hình tốt nhất **theo validation**, ký hiệu BEST):

| ID | Thay đổi so với BEST | Câu hỏi | Ưu tiên | Ghi chú |
|----|---------------------|---------|---------|---------|
| **ABL-A** | `augmentation.enabled = false` | Augmentation đóng góp bao nhiêu? (H4) | **Cao** | Chỉ đổi 1 cờ; không phải tạo lại dữ liệu |
| **ABL-B** | Cửa sổ HU: thêm kênh trung thất (2 kênh: phổi + trung thất) | Thông tin HU ngoài cửa sổ phổi có giúp không? | Trung bình | Chỉ đổi `in_channels` và hàm tạo kênh; dùng cùng patch |
| ABL-C | Resample in-plane về 0.7 mm | Chuẩn hóa kích thước vật lý có giúp không? | Thấp | Phải tạo lại dữ liệu; metric vẫn tính ở spacing gốc |
| ABL-D | GT = union / intersection (thay cho majority) | Kết quả nhạy với định nghĩa GT đến đâu? | Thấp | **Phân tích độ nhạy**, không phải cải tiến; phải đánh giá trên **cả hai** định nghĩa GT |

**Khuyến nghị:** làm **ABL-A** (bắt buộc), **ABL-B** (nếu còn thời gian). ABL-C và ABL-D chỉ làm khi mọi phần khác đã xong.
"Preprocessing strategy" trong yêu cầu ban đầu được cụ thể hóa thành **ABL-B** (một biến, có giả thuyết rõ ràng).

Mỗi ablation bổ sung: 3 seed, so với BEST bằng cùng kiểm định ([10](10_evaluation_protocol.md) mục 4).

## 3. Bảng kết quả (template — KHÔNG điền tay)

Sinh từ `results/metrics/experiments_summary.csv`:

| Cấu hình | Attention | Dice loss | Aug | Dice (mean ± std, 3 seed) | IoU | Precision | Recall | HD95 (mm) | Δ Dice so với EXP-01 [CI 95%] | p (Holm) |
|----------|:---:|:---:|:---:|---|---|---|---|---|---|---|
| EXP-01 | – | – | ✓ | — | — | — | — | — | — | — |
| EXP-02 | – | ✓ | ✓ | — | — | — | — | — | — | — |
| EXP-03 | ✓ | – | ✓ | — | — | — | — | — | — | — |
| EXP-04 | ✓ | ✓ | ✓ | — | — | — | — | — | — | — |
| ABL-A | (BEST) | (BEST) | – | — | — | — | — | — | Δ so với BEST | — |

## 4. Diễn giải

- Đóng góp được gán cho một thành phần chỉ khi thỏa tiêu chí thống kê ở [10](10_evaluation_protocol.md).
- Báo cáo kèm **phân tầng**: một thành phần có thể không giúp trên trung bình nhưng giúp rõ trên nốt nhỏ. Đây là phát hiện có giá trị, **với điều kiện** phân tích phân tầng đã được **định trước** (đã liệt kê ở [10](10_evaluation_protocol.md) mục 5), không phải tìm sau khi thấy kết quả.
- **[LIMITATION]** 3 seed cho ước lượng biến thiên còn thô. Phải nêu rõ trong khóa luận.
