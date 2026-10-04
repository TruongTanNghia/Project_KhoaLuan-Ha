# 07 — U-Net Baseline

Code: `src/models/unet.py`, `src/models/model_factory.py` (PHASE 14). Config: `configs/unet.yaml`.

## 1. Vì sao U-Net làm baseline

- **[FACT]** U-Net (Ronneberger et al., 2015) được thiết kế cho phân đoạn ảnh y sinh với **ít dữ liệu**. Nó là kiến trúc nền của phần lớn phương pháp phân đoạn y khoa sau đó, bao gồm 3D U-Net, Attention U-Net, UNet++ và nnU-Net.
- **[FACT]** nnU-Net (Isensee et al., 2021) cho thấy một U-Net được cấu hình tốt vẫn là baseline rất mạnh trên nhiều bộ dữ liệu.
- Baseline phải **mạnh vừa đủ và chuẩn mực**. Một baseline yếu khiến "cải tiến" của phương pháp đề xuất trở nên vô nghĩa.

## 2. Kiến trúc

```
Input [1×128×128]
  │ Enc1: (Conv3×3-BN-ReLU)×2 → 32×128×128 ───────────────── skip1 ──────────┐
  │ MaxPool 2×2                                                             │
  │ Enc2: → 64×64×64 ─────────────────────────────── skip2 ───────────┐     │
  │ MaxPool                                                           │     │
  │ Enc3: → 128×32×32 ───────────────────── skip3 ──────────┐         │     │
  │ MaxPool                                                 │         │     │
  │ Enc4: → 256×16×16 ──────────── skip4 ──────┐            │         │     │
  │ MaxPool                                    │            │         │     │
  ▼ Bottleneck: → 512×8×8                      │            │         │     │
  │ UpConv 2×2 → 256×16×16 ─ concat(skip4) → Dec4 → 256×16×16         │     │
  │ UpConv     → 128×32×32 ─ concat(skip3) → Dec3 → 128×32×32         │     │
  │ UpConv     → 64×64×64  ─ concat(skip2) → Dec2 → 64×64×64 ◄────────┘     │
  │ UpConv     → 32×128×128─ concat(skip1) → Dec1 → 32×128×128 ◄────────────┘
  ▼ Conv 1×1 → 1×128×128 (logits) → sigmoid (trong loss/metric/inference)
```

| Thành phần | Vai trò | Giải thích dễ hiểu |
|------------|---------|--------------------|
| **Encoder** | Trích đặc trưng từ cục bộ đến toàn cục; giảm độ phân giải, tăng số kênh | "Nhìn xa dần": từ cạnh, góc, đến hình dạng, rồi ngữ cảnh |
| **Bottleneck** | Biểu diễn trừu tượng nhất, trường nhìn (receptive field) rộng nhất | Hiểu "đây là vùng nào của phổi" |
| **Decoder** | Khôi phục độ phân giải để vẽ mask từng pixel | "Vẽ lại chi tiết" |
| **Skip connections** | Nối đặc trưng độ phân giải cao từ encoder sang decoder | Trả lại chi tiết biên đã mất khi pooling. **Rất quan trọng cho nốt nhỏ** |
| **Conv 1×1 + sigmoid** | Ánh xạ về xác suất từng pixel | |

## 3. Cấu hình

| Tham số | Giá trị | Lý do |
|---------|---------|-------|
| `in_channels` | 1 | Một cửa sổ HU |
| `out_channels` | 1 | Nhị phân, dùng sigmoid (không cần softmax 2 lớp) |
| `base_channels` | 32 | Bản gốc dùng 64. 32 giảm khoảng 4 lần số tham số, vừa GPU 4 GB, và vẫn đủ năng lực cho patch 128 × 128 |
| `depth` | 4 | 128 / 2⁴ = 8: bottleneck 8 × 8, receptive field đủ bao nốt lớn cùng ngữ cảnh |
| Padding | `same` (padding = 1) | Đầu ra cùng kích thước đầu vào, không phải cắt mask như bản gốc |
| Normalization | BatchNorm | Chuẩn; batch 16 đủ để BN ổn định |
| Upsampling | ConvTranspose 2 × 2 | Như bản gốc |
| Đầu ra | **logits** | Sigmoid nằm trong `BCEWithLogitsLoss`, ổn định số học khi dùng AMP |
| Số tham số | ≈ **7.76 M** | Đo trên bản phác thảo cùng thiết kế; số chính xác do code in ra ở PHASE 14 |

**Khác biệt so với bản gốc (2015), cần nêu trong khóa luận:** padding `same` thay vì `valid`, thêm BatchNorm, số kênh giảm một nửa. Đây là những điều chỉnh tiêu chuẩn trong các cài đặt hiện đại.

## 4. Kiểm tra trước khi huấn luyện (PHASE 14)

1. Forward `[2, 1, 128, 128]` → `[2, 1, 128, 128]`.
2. Kích thước đầu vào không chia hết cho 2^depth → báo lỗi rõ ràng.
3. **Overfit một batch:** huấn luyện trên 1 batch cố định khoảng 200 bước, Dice train phải tiến gần 1. Nếu không đạt thì có bug (nhãn, loss, hoặc luồng gradient) và **DỪNG**.
4. Ghi số tham số và VRAM đỉnh với batch 16 + AMP vào log.

## 5. Giới hạn của baseline

- **[LIMITATION]** 2D: không thấy được rằng mạch máu là cấu trúc dạng ống *kéo dài qua nhiều lát*, còn nốt là cấu trúc *khu trú*. Đây là nguồn FP chính được dự báo trước.
- **[LIMITATION]** Skip connection truyền **mọi** đặc trưng, kể cả đặc trưng của mạch máu và thành ngực. Đây chính là động cơ cho attention gate ([08](08_proposed_model.md)).

## Tham khảo
- Ronneberger O., Fischer P., Brox T. (2015). U-Net. *MICCAI*, LNCS 9351, 234–241. doi:10.1007/978-3-319-24574-4_28
- Isensee F. et al. (2021). nnU-Net. *Nature Methods*, 18, 203–211. doi:10.1038/s41592-020-01008-z
