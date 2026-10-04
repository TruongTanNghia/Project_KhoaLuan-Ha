# 09 — Training Strategy & Loss Functions

Code: `src/losses/*` (PHASE 15), `src/training/*` (16–17). Config: `configs/base.yaml` → `optimizer`, `scheduler`, `training`, `loss`.

## 1. Training protocol

| Thành phần | Giá trị | Lý do | Nhãn |
|------------|---------|-------|------|
| **Dataset split** | Theo bệnh nhân 70/15/15, phân tầng theo kích thước nốt | Tránh leakage; phân bố tương đồng ([06](06_dataset_construction.md)) | [DECISION] |
| **Input** | Patch 128 × 128, 1 kênh, cửa sổ phổi, [0, 1] | [05](05_preprocessing_pipeline.md) | [DECISION] |
| **Batch size** | 16 | Vừa 4 GB VRAM với AMP và base_channels 32; đủ lớn cho BatchNorm ổn định. **Đo VRAM thực tế ở PHASE 14**; nếu tràn thì giảm còn 8 và ghi lại | [DECISION] |
| **Optimizer** | AdamW, `lr = 3e-4`, `weight_decay = 1e-4`, betas (0.9, 0.999) | Adam hội tụ nhanh, ít nhạy với lr; AdamW tách weight decay khỏi cập nhật gradient (Loshchilov & Hutter, 2019). 3e-4 là điểm khởi đầu phổ biến cho Adam | [DECISION] |
| **Scheduler** | Cosine annealing về `min_lr = 1e-6` theo số epoch | Giảm lr mượt, không cần chọn mốc giảm; ít tham số hơn step decay | [DECISION] |
| **Epochs** | Tối đa 100 | Giới hạn trên; early stopping thường dừng sớm hơn | [DECISION] |
| **Early stopping** | Theo dõi `val_dice` = Dice trung bình trên **patch dương** của val (nhanh, ổn định), patience 15, min_delta 1e-4. Ghi kèm tỉ lệ FP trên patch âm | Tránh overfit; Dice là mục tiêu chính. Đánh giá cuối cùng theo nốt nằm ở [10](10_evaluation_protocol.md) | [DECISION] |
| **Checkpoint** | `best.pt` (theo val_dice) + `last.pt` | Best để đánh giá; last để resume | [DECISION] |
| **Mixed precision** | AMP (float16) | Tiết kiệm VRAM, tăng tốc trên GPU RTX | [DECISION] |
| **Gradient clipping** | max norm 1.0 | Ổn định khi dùng Dice loss (gradient có thể lớn ở mask nhỏ) | [DECISION] |
| **Seed** | 42 (chính) + 2 seed bổ sung (ví dụ 1, 2) | Ước lượng biến thiên giữa các lần chạy | [DECISION] |
| **Augmentation** | Lật ngang, xoay ±15°, scale ±10% ([05](05_preprocessing_pipeline.md) bước 8) | Hình học nhẹ, hợp lý về giải phẫu | [DECISION] |
| **Validation** | Mỗi epoch, trên **toàn bộ** tập val (patch dương + âm), τ = 0.5 | Theo dõi nhất quán | [DECISION] |

### Lưu ý về lựa chọn hyperparameter
- **[DECISION]** **Không** grid search diện rộng. Hyperparameter giống nhau cho cả 4 experiment, để so sánh công bằng. Grid search riêng cho từng model sẽ làm lẫn "kiến trúc tốt hơn" với "được tinh chỉnh kỹ hơn".
- Nếu baseline không hội tụ với lr = 3e-4: chạy **LR range test** trên tập train cho U-Net baseline, chọn lr, rồi dùng **chung** cho mọi experiment. Ghi lại quy trình này.
- **[NOT RECOMMENDED]** Chọn hyperparameter dựa trên kết quả test.

## 2. Phân tích loss function

| Loss | Công thức (rút gọn) | Ưu điểm | Nhược điểm | Phù hợp nốt phổi? |
|------|---------------------|---------|------------|-------------------|
| **BCE** | $-\frac{1}{N}\sum [y\log p + (1-y)\log(1-p)]$ | Gradient ổn định, mượt; tiêu chuẩn | **Bị nền chi phối**: pixel nốt rất ít nên model có thể dự đoán thiên về nền | Baseline hợp lý; cần patch-based để giảm mất cân bằng |
| **Dice loss** | $1 - \frac{2\sum py + \epsilon}{\sum p + \sum y + \epsilon}$ | Tối ưu trực tiếp xấp xỉ của metric chính; không nhạy với tỉ lệ nền/nốt (Milletari et al., 2016) | Gradient kém ổn định khi mask rất nhỏ hoặc rỗng; với patch âm (mask rỗng) hành vi phụ thuộc $\epsilon$ | Tốt cho vật thể nhỏ, nhưng nên kết hợp |
| **BCE + Dice** | $0.5\,\mathcal{L}_{BCE} + 0.5\,\mathcal{L}_{Dice}$ | BCE cho gradient ổn định từng pixel, Dice cho mục tiêu vùng; là lựa chọn phổ biến (nnU-Net dùng CE + Dice) | Thêm một trọng số cần cố định | **Main experiment** |
| **Focal** (Lin et al., 2017) | $-\alpha(1-p_t)^\gamma \log p_t$ | Giảm trọng số mẫu dễ, tập trung vào pixel khó | 2 siêu tham số (α, γ); thiết kế cho phát hiện vật thể dày đặc | Không cần thiết khi đã có patch-based + Dice |
| **Tversky** (Salehi et al., 2017) | $1 - \frac{TP}{TP + \alpha FP + \beta FN}$ | Điều chỉnh được cân bằng FP/FN (β > α thì ưu tiên recall) | Thêm siêu tham số; chọn α, β cần lý do lâm sàng | Hữu ích nếu failure analysis cho thấy under-segmentation có hệ thống |

### Khuyến nghị

- **Baseline loss: BCE.** Đây là điểm tham chiếu tự nhiên nhất, cho phép đo chính xác đóng góp của Dice.
- **Main loss: BCE + Dice** (trọng số 0.5/0.5).
- **[DECISION]** **Không** đưa Focal và Tversky vào ma trận thực nghiệm chính. Lý do:
  1. Mỗi loss thêm vào nhân số experiment lên (× 2 kiến trúc × 3 seed = thêm 6 lần chạy), trong khi GPU 4 GB và thời gian có hạn.
  2. Chúng không trả lời câu hỏi nghiên cứu chính (attention có giúp không?).
  3. Thêm siêu tham số (α, β, γ) cần tinh chỉnh, nên so sánh không còn công bằng nếu không tinh chỉnh kỹ.
- **Điều kiện để xem xét lại:** nếu failure analysis cho thấy under-segmentation chiếm ưu thế rõ rệt (Recall << Precision), **một** experiment bổ sung với Tversky (α = 0.3, β = 0.7, theo bài gốc) trên model tốt nhất là hợp lý, và trình bày như **phân tích bổ sung**.
- **Dice loss thuần**: không làm experiment riêng. BCE + Dice đã bao hàm tác dụng của Dice, và Dice thuần không ổn định với patch âm.

### Chi tiết cài đặt quan trọng
- Dùng `BCEWithLogitsLoss` (sigmoid tích hợp), **không** dùng sigmoid + `BCELoss`, vì không ổn định số học khi chạy AMP.
- Dice loss tính **theo từng mẫu** rồi lấy trung bình batch; tính bằng float32 ngay cả khi bật AMP.
- Patch âm: Dice loss với $\epsilon = 1$ cho loss ≈ 0 khi dự đoán rỗng trên mask rỗng. Đó là hành vi mong muốn. Test đơn vị cho trường hợp này ở PHASE 15.
- Ghi riêng thành phần BCE và Dice mỗi epoch, để phát hiện khi một thành phần lấn át thành phần kia.

## 3. Quy trình một experiment

```
1. load_config(experiments/<exp>/config.yaml) + --set project.seed=<s>
2. Kiểm tra split (assert rời nhau), dataset_version khớp manifest
3. set_seed(seed), build dataloaders (seed_worker, generator)
4. build_model, build_loss, build_optimizer, build_scheduler
5. Lưu resolved_config.yaml + run_info.json (git commit, versions, GPU)
6. for epoch: train → validate → log (history.csv, TensorBoard) → ckpt → early stop?
7. summary.json: best_epoch, best_val_dice, thời gian huấn luyện, VRAM đỉnh
8. (Sau khi CẢ 4 experiment xong) → đánh giá test MỘT lần → results/metrics/
```

## 4. Baseline experiment đề xuất (chạy đầu tiên)

**EXP-01: U-Net + BCE, seed 42.**

Trước khi chạy đầy đủ:
1. **Smoke test:** 2 epoch trên 5% dữ liệu, xác nhận pipeline chạy hết vòng, sinh checkpoint và history.
2. **Overfit test:** 1 batch, khoảng 200 bước, Dice train phải tiến gần 1.
3. **Sanity check của loss:** loss ban đầu với BCE ≈ ln(2) ≈ 0.693 (khi output ban đầu ≈ 0.5).

## 5. Dấu hiệu cảnh báo khi huấn luyện

| Dấu hiệu | Nguyên nhân có thể | Hành động |
|----------|-------------------|-----------|
| Loss = NaN | lr quá lớn, AMP tràn số, chia cho 0 trong Dice | Trainer dừng ngay, ghi log batch gây lỗi |
| Val Dice ≈ 0 suốt | Model dự đoán toàn nền (BCE bị nền chi phối), nhãn sai | Kiểm tra mask, tỉ lệ dương, thử overfit test |
| Val Dice ≈ train Dice và rất cao | **Nghi leakage** | **DỪNG**, kiểm tra split |
| Train tăng, val giảm sớm | Overfit | Early stopping xử lý; xem lại augmentation |
| Val dao động mạnh | Tập val nhỏ hoặc batch nhỏ | Báo cáo trung bình trượt; không chọn checkpoint theo một "đỉnh may mắn" |

## Tham khảo
- Loshchilov I., Hutter F. (2019). Decoupled weight decay regularization. *ICLR*. arXiv:1711.05101
- Loshchilov I., Hutter F. (2017). SGDR: Stochastic gradient descent with warm restarts. *ICLR*. arXiv:1608.03983
- Milletari F. et al. (2016). V-Net. *3DV*. doi:10.1109/3DV.2016.79
- Lin T.-Y. et al. (2017). Focal loss for dense object detection. *ICCV*. arXiv:1708.02002
- Salehi S.S.M. et al. (2017). Tversky loss function for image segmentation using 3D FCDN. *MLMI*. arXiv:1706.05721
