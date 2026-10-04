# 06 — Dataset Construction

Code: `src/data/preprocessing.py` (PHASE 10), `src/data/dataset_split.py` (11), `src/datasets/lung_nodule_dataset.py` (12–13).

## 1. Định nghĩa mẫu

| Loại mẫu | Định nghĩa | Nhãn |
|----------|-----------|------|
| **Dương** | Patch 128 × 128 trên một lát có mask GT khác rỗng, tâm patch = tâm nốt + jitter | Mask GT |
| **Âm** | Patch 128 × 128 có tâm nằm trong mask phổi và **không chứa** pixel GT nào; khoảng cách tới mọi nốt (kể cả nốt < 3 mm, non-nodule, nốt chỉ 1 bác sĩ vẽ) > biên an toàn | Mask rỗng |

**[DECISION]** Patch âm **tránh** vị trí của nốt < 3 mm, non-nodule và nốt chỉ có 1 phiếu. Những vùng này có thể *thật sự* là nốt; nếu gán nhãn "nền" cho chúng là dạy model sai.

**[DECISION]** `negative_ratio = 1.0` (1 patch âm cho mỗi patch dương) trong experiment chính. Tỉ lệ này cân bằng giữa học "khi nào không có nốt" và không để nền lấn át.

## 2. Chia tập theo bệnh nhân

### 2.1 Quy tắc

> **Toàn bộ dữ liệu của một bệnh nhân (mọi scan, mọi lát, mọi patch) nằm trong đúng MỘT tập.**

| | Train | Validation | Test |
|---|---|---|---|
| Tỉ lệ bệnh nhân | 70% | 15% | 15% |
| Dùng để | Cập nhật trọng số | Chọn checkpoint, early stopping, chọn ngưỡng τ | **Chỉ** báo cáo kết quả cuối cùng |

### 2.2 Vì sao không chia theo slice/patch?

**[FACT]** Các lát liền kề của cùng một nốt gần như giống hệt nhau (khoảng cách 1–2.5 mm). Nếu lát *i* thuộc train và lát *i+1* thuộc test, model chỉ cần "nhớ" là đúng. Kết quả test bị **thổi phồng** và không phản ánh khả năng trên bệnh nhân mới. Đây là dạng **data leakage** phổ biến nhất trong các nghiên cứu phân đoạn ảnh y khoa.

**[FACT]** Một số bệnh nhân LIDC có > 1 scan (1018 scan / 1010 bệnh nhân). Chia theo `series_uid` vẫn để lọt cùng một người vào hai tập. **Phải chia theo `patient_id`.**

### 2.3 Phân tầng (stratification)

Mục tiêu: các tập có phân bố tương tự nhau, để kết quả test không phụ thuộc vào "may rủi".

- Mỗi bệnh nhân được gán một **nhóm tầng**: `{không có nốt dương} ∪ {có nốt, đường kính lớn nhất ∈ [3,6), [6,10), [10,20), ≥ 20 mm}`.
- Chia ngẫu nhiên **trong từng nhóm** theo 70/15/15, với seed cố định (`project.seed`).
- **[DECISION]** Bệnh nhân **không** có nốt dương sau majority vẫn được giữ: họ cung cấp patch âm và lát "sạch" cho đánh giá FP.

### 2.4 Kiểm tra tự động (bắt buộc)

```text
assert train_patients ∩ val_patients  = ∅
assert train_patients ∩ test_patients = ∅
assert val_patients   ∩ test_patients = ∅
assert train ∪ val ∪ test = all_patients
```

- Chạy khi tạo split (PHASE 11) **và** mỗi lần khởi tạo Dataset (PHASE 12) **và** khi bắt đầu training.
- Lưu `data/splits/split_manifest.json`: seed, tỉ lệ, số bệnh nhân/nốt/patch mỗi tập, `dataset_version`, hash của 3 file CSV.

### 2.5 Đóng băng tập test

**[DECISION]** Sau khi tạo, tập test được **đóng băng**:
- Không nhìn vào ảnh hay kết quả test khi tinh chỉnh bất cứ điều gì.
- Chỉ chạy đánh giá test **một lần cho mỗi cấu hình cuối cùng**, sau khi mọi lựa chọn đã cố định trên validation.
- Nếu phát hiện lỗi pipeline sau khi đã nhìn kết quả test: sửa lỗi, tăng `dataset_version`, ghi vào nhật ký, và **báo cáo minh bạch** trong khóa luận.

## 3. Thống kê mô tả cần báo cáo (sinh tự động, KHÔNG điền tay)

| | Train | Val | Test |
|---|---|---|---|
| Số bệnh nhân | — | — | — |
| Số nốt dương (majority ≥ 2/4) | — | — | — |
| Số patch dương / âm | — | — | — |
| Đường kính nốt: trung vị (IQR), mm | — | — | — |
| % nốt theo texture (đặc / bán đặc / kính mờ) | — | — | — |
| % nốt theo radiologist_count (2/3/4) | — | — | — |

**Gate:** nếu phân bố giữa các tập lệch rõ rệt (ví dụ test có ít nốt nhỏ hơn hẳn) thì xem lại phân tầng trước khi huấn luyện.

## 4. PyTorch Dataset

```python
LungNoduleDataset(split="train", cfg=cfg, transform=build_transforms(cfg, train=True))
# __getitem__ → {"image": float32 [1,128,128], "mask": float32 [1,128,128], "meta": {...}}
```

- Lọc `samples.csv` theo danh sách **bệnh nhân** trong `data/splits/<split>.csv`, **không** lọc theo sample.
- `meta` mang theo `patient_id`, `nodule_id`, `pixel_spacing_yx` để tính HD95 (mm) và gom kết quả theo nốt.
- DataLoader: `worker_init_fn=seed_worker`, `generator=make_generator(seed)` để tái lập được.
- **Windows:** `num_workers > 0` cần guard `if __name__ == "__main__":` trong script.

## 5. Tập cho đánh giá phát hiện (phương án B)

Ngoài patch, cần **toàn bộ volume** của các bệnh nhân **test** (HU + GT + mask phổi) để chạy sliding window. Tập này được dựng từ cùng split, **không** tạo split mới.

## 6. Rủi ro và cách kiểm soát

| Rủi ro | Dấu hiệu | Kiểm soát |
|--------|----------|-----------|
| Leakage theo bệnh nhân | Val/test Dice cao bất thường, gần bằng train | Assert ở 3 nơi (mục 2.4) |
| Leakage qua tiền xử lý | Thống kê chuẩn hóa tính trên toàn dataset | Chuẩn hóa theo **cửa sổ cố định**, không học từ dữ liệu |
| Leakage qua lựa chọn mô hình | Chọn checkpoint/ngưỡng/cấu hình dựa trên test | Mọi lựa chọn chỉ dựa trên val |
| Nhãn sai ở patch âm | Model bị phạt khi phát hiện đúng nốt chưa được gán nhãn | Biên an toàn quanh mọi tổn thương có trong XML |
| Lệch phân bố giữa các tập | Bảng thống kê mục 3 | Phân tầng |
