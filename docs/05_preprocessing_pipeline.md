# 05 — Preprocessing Pipeline

```
DICOM loading → HU conversion → Windowing → Normalization → Lung ROI → Cropping → (Resize) → Augmentation
   PHASE 03        PHASE 08       PHASE 09      PHASE 09      PHASE 10    PHASE 10   PHASE 10   PHASE 13
```

Mọi tham số nằm trong `configs/base.yaml`. Mọi thay đổi tiền xử lý đều phải **tăng `project.dataset_version`**.

---

## Bước 1 — DICOM loading

| | |
|---|---|
| **Purpose** | Đọc một series CT thành volume 3D có hình học đúng |
| **Input** | Thư mục series (`*.dcm`) |
| **Output** | `CTVolume`: mảng `int16 [Z, Y, X]` (giá trị lưu trữ gốc), spacing (z, y, x) mm, danh sách z, map SOP UID → index, slope/intercept |
| **Parameters** | `data_validation.required_modality = CT`, `min_slices_per_series = 30` |
| **Reason** | Annotation tham chiếu SOP UID và z, nên phải giữ nguyên hình học gốc |
| **Potential risk** | (a) Sắp lát theo `InstanceNumber` → thứ tự sai. (b) Lấy `SliceThickness` làm spacing → sai đơn vị z. (c) Lẫn scout/localizer vào series. (d) Lát trùng z. Tất cả được bắt ở PHASE 02–03 |

## Bước 2 — HU conversion

| | |
|---|---|
| **Purpose** | Đưa giá trị pixel về thang vật lý chuẩn (HU), so sánh được giữa các máy |
| **Input** | Giá trị lưu trữ + `RescaleSlope`, `RescaleIntercept` |
| **Output** | `float32` HU, clip vào `[min_hu, max_hu] = [−1024, 3071]` |
| **Parameters** | `preprocessing.hu.min_hu`, `max_hu` |
| **Reason** | **[FACT]** Giá trị lưu trữ phụ thuộc máy; HU thì không. Windowing chỉ có nghĩa trên HU |
| **Potential risk** | Pixel ngoài trường quét (padding, thường −2000 hoặc −3024) không phải "không khí" thật. Nếu không đưa về −1024 trước, chúng làm lệch thống kê. **Kiểm tra:** histogram HU mỗi series phải có đỉnh gần −1000 (khí) và quanh 0–50 (mô mềm) |

## Bước 3 — Windowing

| | |
|---|---|
| **Purpose** | Chỉ giữ dải HU có thông tin cho phổi và nốt; tăng tương phản |
| **Input** | Ảnh HU |
| **Output** | Ảnh HU đã clip vào `[L − W/2, L + W/2]` |
| **Parameters** | **Cửa sổ phổi:** `level = −600`, `width = 1500`, tức `[−1350, +150]` HU |
| **Reason** | **[FACT]** Đây là cửa sổ phổi thông dụng trong đọc phim lâm sàng. Dải này bao gồm khí (−1000), nhu mô phổi, nốt kính mờ và nốt đặc (mô mềm). Xương (> +400) bị bão hòa, tốt vì xương không liên quan |
| **Potential risk** | (a) Cửa sổ quá hẹp làm mất phân biệt giữa nốt đặc và mạch máu cản quang. (b) Nốt vôi hóa (HU cao) bị bão hòa, nhưng vẫn sáng nên vẫn thấy. (c) Cửa sổ là siêu tham số: **không** tinh chỉnh trên tập test |

**Phương án:**
- A: cửa sổ phổi đơn kênh (mặc định).
- B: đa cửa sổ (phổi + trung thất) xếp thành 2–3 kênh.
- C: không window, chỉ chuẩn hóa toàn dải HU.

**Khuyến nghị: A** cho experiment chính. Đơn giản, hợp lý về lâm sàng, ít tham số. B là ứng viên hợp lý cho ablation "preprocessing strategy" ([12](12_ablation_study.md)). **[NOT RECOMMENDED]** C: phần lớn dải động bị lãng phí cho xương và khí ngoài cơ thể.

## Bước 4 — Normalization

| | |
|---|---|
| **Purpose** | Đưa giá trị vào dải ổn định cho tối ưu hóa |
| **Input** | Ảnh đã window |
| **Output** | `x = (HU_clip − (L − W/2)) / W ∈ [0, 1]` |
| **Parameters** | `preprocessing.normalization = minmax_window` |
| **Reason** | Min–max **theo cửa sổ cố định** cho cùng một phép biến đổi với **mọi** ảnh, giữ được ý nghĩa vật lý (cùng HU → cùng giá trị) |
| **Potential risk** | **[NOT RECOMMENDED]** Z-score hoặc min–max **theo từng ảnh hay từng patch**: cùng một mô sẽ có giá trị khác nhau tùy nội dung patch (patch nhiều khí khác patch nhiều mô), phá vỡ ý nghĩa HU |

## Bước 5 — Lung ROI (mask vùng phổi)

| | |
|---|---|
| **Purpose** | (a) Lấy patch âm **bên trong phổi**, thay vì lấy trong không khí ngoài cơ thể (quá dễ, vô ích). (b) Khi suy luận trên toàn lát: loại FP ngoài phổi |
| **Input** | Volume HU |
| **Output** | Mask phổi nhị phân `[Z, Y, X]` |
| **Parameters** | Ngưỡng HU (ví dụ < −320), loại vùng chạm biên ảnh, giữ 2 thành phần lớn nhất, **closing** hình thái học + lấp lỗ. [DECISION] tham số cụ thể chốt ở PHASE 10 |
| **Reason** | Cách heuristic dựa trên ngưỡng là đủ cho mục đích *lấy mẫu* và *lọc FP*. Không cần mạng phân đoạn phổi riêng |
| **Potential risk** | **Nghiêm trọng:** ngưỡng HU đơn giản **cắt mất nốt sát màng phổi (juxtapleural)**, vì nốt đặc có HU của mô mềm, giống thành ngực. Nếu dùng mask phổi để *cắt bỏ* vùng ảnh, model sẽ không bao giờ thấy những nốt này. **Biện pháp:** chỉ dùng mask phổi để **chọn vị trí lấy mẫu** và **lọc ứng viên**, **không** dùng để xóa pixel đầu vào; dùng closing với kernel đủ lớn; **kiểm tra:** 100% tâm nốt GT phải nằm trong mask phổi đã closing, ca vi phạm phải được ghi log |

## Bước 6 — Cropping (patch)

| | |
|---|---|
| **Purpose** | Tập trung vào nốt; giảm mất cân bằng lớp; vừa VRAM 4 GB |
| **Input** | Lát đã chuẩn hóa + mask GT + mask phổi + metadata nốt |
| **Output** | Patch **128 × 128** ảnh/mask + metadata (tọa độ gốc của patch để ghép lại) |
| **Parameters** | `roi.patch_size = [128, 128]`, `center_jitter_px = 16`, `negative_ratio = 1.0` |
| **Reason** | Ở spacing khoảng 0.7 mm, patch 128 px ≈ 90 mm, đủ chứa nốt lớn nhất (≤ 30 mm) cùng ngữ cảnh xung quanh. **Jitter** để model không học "nốt luôn nằm ở giữa". **Patch âm** để model học nói "không có nốt", điều kiện cần cho đánh giá phát hiện |
| **Potential risk** | (a) Không có jitter: model học vị trí, rồi thất bại khi chạy sliding window. (b) Không có patch âm: model luôn vẽ ra một thứ gì đó, FP rất cao. (c) Patch âm lấy ngẫu nhiên đa số là nhu mô "dễ", nên cần một phần patch âm chứa **mạch máu / màng phổi** (hard negatives). **[DECISION]** cân nhắc ở PHASE 10. (d) Lát đầu/cuối của nốt (diện tích rất nhỏ) có nên tính là mẫu dương? → giữ, nhưng gắn cờ `is_edge_slice` |

Phương án đơn vị huấn luyện:

| Phương án | Mô tả | VRAM | Vấn đề |
|-----------|-------|------|--------|
| A | Patch 128 × 128 quanh nốt + patch âm | Thấp | Phải đánh giá phát hiện riêng (sliding window) |
| B | Toàn lát 512 × 512 | Cao (batch rất nhỏ trên 4 GB) | Mất cân bằng cực lớn; huấn luyện chậm |
| C | Toàn lát **resize về 256 × 256** | Trung bình | Xem mục Resize: **[NOT RECOMMENDED]** |

**Khuyến nghị: A.**

## Bước 7 — Resize

**[DECISION]** **Không resize** patch. Patch được cắt trực tiếp ở độ phân giải gốc với kích thước cố định 128 × 128.

**[NOT RECOMMENDED]** Resize toàn lát 512 → 256 (như trong sơ đồ ban đầu):
- Ở spacing khoảng 0.7 mm, nốt 3 mm chỉ rộng khoảng **4 pixel**. Thu nhỏ 2 lần còn khoảng **2 pixel**, gần như mất hẳn, và mask sau nội suy bị sai lệch nặng.
- Đúng nhóm nốt nhỏ (khó nhất, quan trọng nhất cho tầm soát) bị phá hủy nhiều nhất.

**Câu hỏi mở — resample về spacing chuẩn** (`target_spacing_xy_mm`):
- Không resample (mặc định): giữ nguyên thông tin; kích thước pixel khác nhau giữa các scan.
- Resample in-plane về một spacing cố định (ví dụ 0.7 mm): cùng kích thước vật lý cho mỗi pixel, nhưng phải nội suy (ảnh: bilinear, mask: nearest) và phải ánh xạ ngược khi đánh giá.
- **Khuyến nghị:** không resample trong experiment chính. Đưa "có/không resample" vào ablation preprocessing nếu còn thời gian. HD95 luôn tính theo **mm thật**.

## Bước 8 — Augmentation (chỉ trên tập train)

| Phép biến đổi | Tham số mặc định | Áp lên | Lý do | Rủi ro |
|---------------|-----------------|--------|-------|--------|
| Lật ngang | p = 0.5 | ảnh + mask | Patch cục bộ không có tính bất đối xứng trái/phải đáng kể | Thấp |
| Lật dọc | p = 0.0 | — | Hướng trước–sau có ý nghĩa giải phẫu (lưng/ngực) | Tắt mặc định |
| Xoay nhỏ | ±15°, p = 0.3 | ảnh (bilinear) + mask (**nearest**) | Bệnh nhân nằm hơi lệch | Góc xoay lớn tạo vùng trống ở góc; mask nội suy sai nếu không dùng nearest |
| Scale | ±10% | ảnh + mask | Biến thiên kích thước nốt và spacing | Scale lớn làm sai kích thước vật lý |
| Brightness/contrast | p = 0 (tắt) | chỉ ảnh | — | **Làm sai ý nghĩa HU**: chỉ bật thử nghiệm với biên độ nhỏ |
| Gaussian noise | p = 0 (tắt) | chỉ ảnh | Mô phỏng CT liều thấp | Biên độ phải thực tế |
| Elastic deformation | **không dùng** | — | — | **[NOT RECOMMENDED]** Làm thay đổi hình thái nốt (bờ tua gai, bờ đa thùy), vốn là đặc tính lâm sàng quan trọng |
| Random crop | (đã có qua jitter) | — | — | — |

**Nguyên tắc:** phép biến đổi **hình học** áp **đồng thời** lên ảnh và mask (mask dùng nội suy nearest). Phép biến đổi **cường độ** chỉ áp lên ảnh. **Không** augment tập validation/test.

**[HYPOTHESIS]** H4: augmentation hình học nhẹ cải thiện khả năng tổng quát (kiểm tra trong ablation).

## Đầu ra của pipeline

```
data/processed/
├── images/<patient_id>/<sample_id>.npy     float16 [128,128] ∈ [0,1]
├── masks/<patient_id>/<sample_id>.npy      uint8   [128,128] ∈ {0,1}
└── metadata/
    ├── samples.csv     một dòng mỗi patch: patient_id, nodule_id, slice_index, patch_origin_yx,
    │                   pixel_spacing_yx, is_positive, is_edge_slice, + metadata ở [04] mục 6
    └── manifest.json   dataset_version, config hash, thời điểm tạo, thống kê
```
