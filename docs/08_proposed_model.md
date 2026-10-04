# 08 — Proposed Model: Attention U-Net

Code: `src/models/attention_unet.py` (PHASE 18). Config: `configs/attention_unet.yaml`.

> **Nguyên tắc:** tài liệu này mô tả *vì sao kỳ vọng* attention giúp ích. Nó **không** khẳng định attention giúp ích. Câu trả lời chỉ đến từ thực nghiệm ([11](11_experiment_plan.md)).

## 1. Lựa chọn phương pháp cải tiến

| Phương án | Thay đổi so với U-Net | Ưu | Nhược | Đánh giá |
|-----------|----------------------|----|-------|----------|
| **A. Attention U-Net** | Thêm attention gate trên skip connection | Thay đổi **cục bộ, ít tham số** (+khoảng 1%); có động cơ rõ cho bài toán vật thể nhỏ; có bản đồ attention để giải thích | Lợi ích thực tế không đảm bảo; có thể không khác biệt đáng kể | **Khuyến nghị** |
| B. UNet++ | Skip connection lồng nhau, dày đặc | Thường cải thiện nhẹ | Tốn bộ nhớ hơn nhiều; nhiều thay đổi cùng lúc, khó quy kết nguyên nhân | Không chọn |
| C. Residual / Dense U-Net | Thay khối conv | Huấn luyện sâu tốt hơn | Động cơ không gắn với đặc thù nốt phổi | Không chọn |
| D. Transformer (TransUNet, Swin-UNet…) | Encoder dựa trên attention toàn cục | Ngữ cảnh toàn cục | Cần nhiều dữ liệu và VRAM; khó huấn luyện trên 4 GB | **[NOT RECOMMENDED]** cho khóa luận này |
| E. 3D U-Net | Tích chập 3D | Thấy ngữ cảnh giữa các lát (phân biệt mạch máu) | VRAM rất lớn; đổi toàn bộ pipeline | Hướng phát triển |

**Khuyến nghị: A.** Lý do quyết định: so sánh **nhân quả sạch**. Kiến trúc chỉ khác baseline đúng một thành phần, nên mọi khác biệt về kết quả có thể quy cho attention gate.

## 2. Attention gate (Oktay et al., 2018)

### 2.1 Cơ chế

Tại mỗi mức của decoder, trước khi nối skip connection $x^l$ (từ encoder) với đặc trưng decoder:

$$q = \psi^\top\, \text{ReLU}\big(W_x^\top x^l + W_g^\top g + b_g\big) + b_\psi$$

$$\alpha = \sigma(q) \in [0,1]^{H_l \times W_l}, \qquad \hat{x}^l = \alpha \odot x^l$$

- $x^l$: đặc trưng skip (độ phân giải cao, giàu chi tiết, nhưng "không biết" đâu là quan trọng).
- $g$: **tín hiệu gating** từ mức thô hơn của decoder (ngữ cảnh rộng, "biết" vùng nào đáng quan tâm).
- $W_x, W_g, \psi$: tích chập 1×1. Số kênh trung gian = `gate_channels_ratio × kênh skip` (0.5).
- $\alpha$: **hệ số attention** cho từng pixel, nhân vào skip để giữ vùng liên quan và làm yếu vùng không liên quan.

**Giải thích dễ hiểu:** skip connection giống như chuyển nguyên một bức ảnh chi tiết sang decoder. Attention gate giống như một người đã nhìn toàn cảnh, cầm bút dạ quang tô đậm vùng nghi có nốt trước khi chuyển ảnh đi.

### 2.2 Feature selection

- Gate học được **trong lúc huấn luyện, không cần nhãn attention riêng**. Gradient từ loss phân đoạn tự định hướng $\alpha$.
- **[FACT]** Theo Oktay et al. (2018) và Schlemper et al. (2019), attention gate được đề xuất để làm nổi vùng mục tiêu và giảm đáp ứng với nền không liên quan, đặc biệt với cấu trúc nhỏ, có hình dạng thay đổi. Cả hai paper đều thực nghiệm trên CT bụng, **không** phải phổi, nên lợi ích trên nốt phổi vẫn là giả thuyết.
- **[DECISION]** Theo bài gốc, tín hiệu gating lấy từ mức decoder thô hơn và $\alpha$ được nội suy về kích thước của $x^l$. Chi tiết cài đặt (stride, vị trí resample) chốt ở PHASE 18 và ghi lại trong khóa luận.

### 2.3 Chi phí

| | U-Net | Attention U-Net |
|---|---|---|
| Số tham số (bản phác thảo cùng cấu hình) | ≈ 7.76 M | ≈ 7.85 M (**+ khoảng 1.1%**) |
| Số gate | — | 4 (mỗi mức decoder một gate) |

Số chính xác do code in ra ở PHASE 18. **[DECISION]** Báo cáo số tham số của cả hai model trong khóa luận để chứng minh so sánh công bằng: cải thiện (nếu có) không đến từ việc model "to hơn".

## 3. Vì sao có thể phù hợp với phân đoạn nốt phổi

| Đặc điểm bài toán | Lập luận | Nhãn |
|-------------------|----------|------|
| Nốt **nhỏ** (vài mm) so với patch | Skip độ phân giải cao chứa rất nhiều đặc trưng nền; gate giúp lọc bớt | [HYPOTHESIS] H1 |
| **Mạch máu** cắt ngang trên ảnh 2D trông giống nốt tròn | Gating từ ngữ cảnh rộng có thể giảm đáp ứng với mạch máu, nên giảm FP | [HYPOTHESIS] H1b |
| Nốt **sát màng phổi** dính với thành ngực có cùng HU | Attention có thể giúp tách nốt khỏi thành ngực | [HYPOTHESIS], khả năng thấp hơn |
| Có bản đồ $\alpha$ | Trực quan hóa vùng model "chú ý", phục vụ failure analysis và giải thích | [FACT] (về khả năng trực quan hóa) |

## 4. Lợi ích kỳ vọng và hạn chế tiềm ẩn

**Lợi ích kỳ vọng [HYPOTHESIS]:**
- Precision tăng (ít over-segmentation, ít FP ở mạch máu) mà Recall không giảm.
- Cải thiện rõ hơn trên nhóm nốt nhỏ (3–6 mm) và nốt cạnh mạch máu.

**Hạn chế tiềm ẩn:**
- **[LIMITATION]** Patch đã được cắt quanh nốt nên vị trí đại khái đã được "cho sẵn". Lợi ích của attention trong việc *tìm vùng quan tâm* có thể nhỏ hơn so với ảnh toàn lát. Lợi ích có thể chỉ lộ ra trong **đánh giá phát hiện** (sliding window) hơn là trong Dice trên patch.
- **[LIMITATION]** Attention không bù được việc thiếu ngữ cảnh 3D.
- **[LIMITATION]** Bản đồ $\alpha$ **không** phải giải thích nhân quả. Không được trình bày như "model hiểu bệnh lý".
- Rủi ro: chênh lệch giữa hai model nhỏ hơn biến thiên giữa các seed. Vì vậy cần ≥ 3 seed và kiểm định thống kê.

## 5. Tiêu chí kết luận (định trước, tránh "chọn kết quả đẹp")

Attention U-Net được kết luận là **tốt hơn** U-Net khi và chỉ khi:
1. Dice trung bình theo nốt trên test cao hơn, **và**
2. Kiểm định Wilcoxon theo cặp (theo nốt, gộp seed bằng trung bình) cho p < 0.05, **và**
3. Chênh lệch lớn hơn độ lệch chuẩn giữa các seed.

Nếu không thỏa: kết luận là "**không có bằng chứng** cho thấy attention cải thiện trong điều kiện thí nghiệm này". Đây vẫn là kết quả hợp lệ và có giá trị.

## Tham khảo
- Oktay O. et al. (2018). Attention U-Net: Learning where to look for the pancreas. *MIDL*. arXiv:1804.03999
- Schlemper J. et al. (2019). Attention gated networks: Learning to leverage salient regions in medical images. *Medical Image Analysis*, 53, 197–207. doi:10.1016/j.media.2019.01.012 (lưu ý: thực nghiệm trên CT bụng và siêu âm, **không** có dữ liệu phổi)
