# 01 — Problem Definition

## 1. Phát biểu bằng lời

Cho một lát cắt CT ngực (hoặc một vùng ảnh cắt ra từ lát đó), xác định **mỗi pixel** có thuộc về một nốt phổi hay không. "Đúng" được định nghĩa bởi đường viền mà **đa số** các bác sĩ chẩn đoán hình ảnh của LIDC-IDRI đã vẽ.

## 2. Ký hiệu

| Ký hiệu | Ý nghĩa | Ghi chú dễ hiểu |
|---------|---------|-----------------|
| $V \in \mathbb{R}^{D \times H \times W}$ | Một volume CT (đơn vị HU) gồm $D$ lát cắt, mỗi lát $H \times W$ (thường 512 × 512) | "Chồng ảnh" CT của một lần chụp |
| $s = (s_z, s_y, s_x)$ | Khoảng cách voxel (mm) | 1 pixel ≈ 0.5–0.9 mm theo chiều ngang [ASSUMPTION, đo ở PHASE 02] |
| $R = \{r_1, \dots, r_K\}$ | Các bác sĩ đã đọc scan, $K \le 4$ | |
| $A_k^{(j)} \subset \Omega$ | Vùng bác sĩ $k$ vẽ cho nốt $j$ | $\Omega$ là tập tọa độ pixel |
| $\phi(\cdot)$ | Tiền xử lý: HU → window → chuẩn hóa → cắt patch | Chi tiết ở [05](05_preprocessing_pipeline.md) |
| $X \in [0,1]^{h \times w}$ | Ảnh đầu vào của model (patch 2D, $h = w = 128$) | |
| $Y \in \{0,1\}^{h \times w}$ | Ground truth mask (đồng thuận) | 1 = nốt, 0 = nền |
| $f_\theta$ | Mạng nơ-ron với tham số $\theta$ | U-Net hoặc Attention U-Net |
| $P = \sigma(f_\theta(X)) \in [0,1]^{h \times w}$ | Bản đồ xác suất | $\sigma$ = hàm sigmoid |
| $\hat{Y} = \mathbb{1}[P \ge \tau]$ | Mask dự đoán | $\tau$ = ngưỡng, chọn trên validation |

## 3. Xây dựng ground truth (một phần của bài toán)

Với mỗi pixel $u$ của nốt $j$, số phiếu là

$$v_j(u) = \sum_{k=1}^{K} \mathbb{1}[u \in A_k^{(j)}]$$

Ground truth đồng thuận theo đa số:

$$Y_j(u) = \mathbb{1}\big[v_j(u) \ge \lceil \lambda \cdot N \rceil\big], \quad \lambda = 0.5,\; N = K \text{ (số bác sĩ đọc scan)}$$

Với $K = 4$, công thức này nghĩa là **ít nhất 2/4 bác sĩ** đồng ý pixel đó thuộc nốt.

- **[DECISION]** $\lambda = 0.5$, $N = K$. Lý do và các phương án so sánh ở [04_annotation_pipeline.md](04_annotation_pipeline.md).
- **Dễ hiểu:** một pixel được tính là "nốt" khi ít nhất một nửa số bác sĩ đồng ý.
- **[LIMITATION]** $Y$ là *ước lượng* của sự thật, không phải sự thật. Không có xác nhận giải phẫu bệnh ở mức pixel.

## 4. Bài toán học (phân đoạn — nhiệm vụ chính)

Cho tập huấn luyện $\mathcal{D}_{train} = \{(X_i, Y_i)\}_{i=1}^{N}$, tìm

$$\theta^{*} = \arg\min_{\theta} \; \frac{1}{N} \sum_{i=1}^{N} \mathcal{L}\big(\sigma(f_\theta(X_i)),\, Y_i\big)$$

(với regularization kiểu weight decay tách rời, như trong AdamW.)

với $\mathcal{L}$ là một trong các loss:

$$\mathcal{L}_{BCE} = -\frac{1}{|\Omega|}\sum_{u} \big[ Y(u)\log P(u) + (1-Y(u))\log(1-P(u)) \big]$$

$$\mathcal{L}_{Dice} = 1 - \frac{2\sum_u P(u)Y(u) + \epsilon}{\sum_u P(u) + \sum_u Y(u) + \epsilon}$$

$$\mathcal{L}_{BCE+Dice} = w_1 \mathcal{L}_{BCE} + w_2 \mathcal{L}_{Dice}, \quad w_1 = w_2 = 0.5$$

**Mục tiêu đánh giá:** trên tập test (bệnh nhân chưa từng thấy), **tối đa hóa** Dice và IoU, đồng thời giữ Precision/Recall cân bằng và HD95 nhỏ:

$$\text{Dice}(\hat{Y}, Y) = \frac{2|\hat{Y} \cap Y|}{|\hat{Y}| + |Y|}, \qquad \text{IoU}(\hat{Y}, Y) = \frac{|\hat{Y} \cap Y|}{|\hat{Y} \cup Y|}$$

### Vì sao không tối ưu thẳng Dice?

- **[FACT]** Dice tính trên $\hat{Y}$ (đã áp ngưỡng) **không khả vi** theo $\theta$ (hàm bậc thang), nên không lan truyền ngược được.
- Soft Dice loss thay $\hat{Y}$ bằng xác suất $P$, tạo ra một **xấp xỉ khả vi (surrogate)** của Dice (Milletari et al., 2016).
- BCE cho gradient ổn định ở từng pixel nhưng bị **mất cân bằng lớp** chi phối: pixel nốt chỉ chiếm phần rất nhỏ.
- **Dễ hiểu:** BCE dạy model "từng pixel đúng hay sai", Dice dạy model "vùng dự đoán chồng khớp với vùng thật bao nhiêu". Kết hợp cả hai thường ổn định hơn dùng riêng Dice. Đây là **[HYPOTHESIS]** H2, được kiểm tra trong [11](11_experiment_plan.md).

### Chọn ngưỡng τ

- **[DECISION]** Mặc định $\tau = 0.5$. Có thể tinh chỉnh $\tau$ **chỉ trên tập validation**, rồi cố định trước khi chạy test.
- **[NOT RECOMMENDED]** Chọn $\tau$ trên tập test. Đây là một dạng leakage làm kết quả lạc quan giả tạo.

## 5. Bài toán phát hiện (nhiệm vụ thứ cấp — phương án B)

Trên toàn bộ lát cắt của một bệnh nhân test, model sinh mask $\hat{Y}$ (sliding window). Gọi $\{C_m\}$ là các thành phần liên thông 3D của $\hat{Y}$ (ứng viên), và $\{G_j\}$ là các nốt ground truth.

- Nốt $G_j$ được coi là **phát hiện** (true positive) nếu tồn tại $C_m$ với $\text{Dice}(C_m, G_j) > 0$ (có chồng lấn). Tiêu chí "trúng" này phải được cố định trước; một lựa chọn chặt hơn là khoảng cách tâm < bán kính nốt. **[DECISION]** chốt ở PHASE 19.
- **Per-nodule sensitivity** $= \#\{G_j \text{ được phát hiện}\} / \#\{G_j\}$.
- **FP/scan** $= \#\{C_m \text{ không khớp } G_j \text{ nào}\} / \#\text{scan}$.

**[LIMITATION]** Các ứng viên khớp với nốt < 3 mm hoặc non-nodule (có trong XML nhưng không có contour) sẽ bị tính là FP. Cần báo cáo riêng số FP "trùng vị trí nốt < 3 mm hoặc non-nodule" để không phạt oan model.

## 6. Giả định của bài toán

| ID | Giả định | Nhãn | Hệ quả nếu sai |
|----|----------|------|----------------|
| P1 | Có thể phân đoạn từng lát axial độc lập (2D) | [ASSUMPTION] | Mất ngữ cảnh 3D: dễ nhầm mạch máu (hình ống chạy qua nhiều lát) với nốt |
| P2 | Majority ≥ 2/4 là ground truth "đủ tốt" | [DECISION] | Kết quả phụ thuộc định nghĩa GT; kiểm tra độ nhạy bằng union/intersection (tùy chọn) |
| P3 | Phân bố bệnh nhân giữa train/val/test tương đương | [ASSUMPTION] | Kiểm tra bằng thống kê mô tả sau khi chia tập |
| P4 | Ảnh LIDC đại diện cho CT ngực thông thường | [LIMITATION] | Không tổng quát hóa được sang máy chụp hay quy trình khác |
| P5 | Ngưỡng τ chọn trên val dùng được cho test | [ASSUMPTION] | Báo cáo thêm kết quả theo nhiều τ (độ nhạy) |

## 7. Những gì bài toán này KHÔNG giải

- Không ước lượng khả năng ác tính, không phân biệt nốt lành tính hay ác tính.
- Không đưa ra khuyến nghị xử trí lâm sàng.
- Không đảm bảo phát hiện được **mọi** nốt (đặc biệt nốt < 3 mm, vốn không có ground truth).
