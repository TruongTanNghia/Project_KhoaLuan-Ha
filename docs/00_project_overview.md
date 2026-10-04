# 00 — Project Overview

> **Đề tài:** Ứng dụng kỹ thuật học sâu dựa trên kiến trúc U-Net để phát hiện và phân đoạn nốt phổi trên ảnh CT
> **Dataset:** LIDC-IDRI (TCIA) · **Bài toán chính:** phân đoạn nhị phân nốt phổi · **Model:** U-Net (baseline), Attention U-Net (đề xuất)

---

## 0. Bốn khái niệm KHÔNG được đánh đồng

Đây là điểm hội đồng gần như chắc chắn sẽ kiểm tra. Toàn bộ khóa luận phải dùng thuật ngữ nhất quán theo bảng này.

| Khái niệm | Câu hỏi được trả lời | Đầu ra | Ground truth cần có | LIDC-IDRI có cung cấp? | Trong đề tài này? |
|-----------|----------------------|--------|---------------------|------------------------|-------------------|
| **Nodule detection** (phát hiện nốt) | *Ở đâu* có nốt phổi? | Tọa độ / bounding box / vùng ứng viên + điểm tin cậy | Vị trí nốt | **Có**: tâm và contour do bác sĩ đánh dấu | **Phụ** (đánh giá thứ cấp, xem mục 6) |
| **Nodule segmentation** (phân đoạn nốt) | *Pixel nào* thuộc nốt? | Mask nhị phân | Contour/mask từng pixel | **Có**: contour cho nốt ≥ 3 mm | **Chính** |
| **Malignancy classification** (phân loại mức nghi ngờ ác tính) | Nốt này *nghi ngờ ác tính* đến mức nào? | Nhãn/điểm nguy cơ | Nhãn ác tính (lý tưởng là giải phẫu bệnh) | **Một phần**: chỉ có *điểm đánh giá chủ quan 1–5* của bác sĩ trên ảnh, phần lớn **không** có xác nhận giải phẫu bệnh | **Không** |
| **Lung cancer diagnosis** (chẩn đoán ung thư phổi) | Bệnh nhân *có ung thư phổi* không? | Kết luận chẩn đoán | Giải phẫu bệnh, theo dõi lâm sàng | **Không** đủ cho mục đích này | **Không** |

- **[FACT]** Theo định nghĩa của Fleischner Society, *nodule* là một đám mờ tròn hoặc không đều, bờ rõ hoặc không rõ, đường kính **≤ 3 cm**; tổn thương > 3 cm gọi là *mass* (khối) (Hansell et al., 2008).
- **[FACT]** Phần lớn nốt phổi phát hiện trên CT là **lành tính**. "Nốt phổi" **không** đồng nghĩa với "u" hay "ung thư".
- **[DECISION]** Trong khóa luận dùng "**nốt phổi**" (pulmonary/lung nodule). **Không** dùng "khối u phổi", "u phổi" hay "ung thư" để gọi đối tượng được phân đoạn.
- **[NOT RECOMMENDED]** Hiển thị hay diễn giải output của model là "chẩn đoán", "phát hiện ung thư" hay "xác suất ác tính".

---

## 1. Bài toán

Cho một ảnh CT ngực, xác định **chính xác vùng pixel** thuộc về mỗi nốt phổi (≥ 3 mm) trên từng lát cắt axial. Đầu ra là một mask nhị phân có cùng kích thước với ảnh đầu vào.

Diễn đạt dễ hiểu: bác sĩ chẩn đoán hình ảnh vẽ đường viền quanh nốt phổi trên từng lát CT, còn model học cách tự vẽ đường viền đó.

## 2. Động cơ nghiên cứu

- **[FACT]** Năm 2022, ung thư phổi là ung thư được chẩn đoán nhiều nhất (gần 2.5 triệu ca mới, 12.4%) và là nguyên nhân tử vong do ung thư hàng đầu (khoảng 1.8 triệu ca tử vong, 18.7%) trên toàn thế giới (Bray et al., 2024).
- **[FACT]** Thử nghiệm NLST cho thấy tầm soát bằng CT liều thấp giúp giảm tử vong do ung thư phổi so với X-quang ngực ở nhóm nguy cơ cao (National Lung Screening Trial Research Team, 2011).
- **[FACT]** Hướng xử trí nốt phổi phát hiện tình cờ phụ thuộc nhiều vào **kích thước** và **loại đậm độ** (đặc, bán đặc, kính mờ) của nốt (MacMahon et al., 2017 — Fleischner guidelines).
- **Hệ quả:** đo kích thước/thể tích nốt cần một đường viền chính xác. Vẽ tay tốn thời gian và **khác nhau giữa các bác sĩ** (inter-observer variability). Đây chính là chỗ phân đoạn tự động có giá trị.
- **[FACT]** LIDC-IDRI ghi nhận rõ sự bất đồng này: các bác sĩ đọc độc lập và **không** bị ép đạt đồng thuận (Armato et al., 2011). Vì vậy bài toán còn có một khía cạnh nghiên cứu: *làm sao xây ground truth từ nhiều ý kiến khác nhau*.

## 3. Ý nghĩa thực tiễn

| Ý nghĩa | Mức độ khóa luận đạt được |
|---------|---------------------------|
| Hỗ trợ đo kích thước và thể tích nốt một cách nhất quán | Có thể minh họa: tính đường kính và diện tích từ mask dự đoán. **[LIMITATION]** chưa so sánh với đo đạc lâm sàng. |
| Giảm thời gian vẽ contour thủ công | Chỉ ở mức nguyên mẫu, chưa đo thời gian thực tế với bác sĩ. |
| Nền tảng cho các bước sau (theo dõi tăng trưởng, phân tích hình thái) | Ngoài phạm vi; nêu trong hướng phát triển. |
| Giáo dục: pipeline mở, tái lập được trên dữ liệu công khai | **Có**. Đây là đóng góp thực tế nhất của khóa luận. |

## 4. Mục tiêu tổng quát

Xây dựng và đánh giá một pipeline học sâu **tái lập được**, phân đoạn nốt phổi trên ảnh CT từ dữ liệu LIDC-IDRI, và so sánh U-Net với một biến thể cải tiến (Attention U-Net) theo một giao thức đánh giá nghiêm ngặt.

## 5. Mục tiêu cụ thể (đo lường được)

| ID | Mục tiêu | Tiêu chí hoàn thành |
|----|----------|---------------------|
| O1 | Xây pipeline chuyển DICOM + XML thành ground truth đồng thuận nhiều bác sĩ, có lưu lại mức độ bất đồng | 100% ROI của nốt ≥ 3 mm khớp được lát cắt; metadata có `radiologist_count` và bản đồ phiếu |
| O2 | Chia dữ liệu theo bệnh nhân, không leakage | Kiểm tra tự động: tập bệnh nhân giữa train/val/test rời nhau |
| O3 | Huấn luyện U-Net baseline | Có checkpoint tốt nhất; kết quả test được sinh tự động |
| O4 | Huấn luyện Attention U-Net trong **cùng điều kiện** | Config chỉ khác ở kiến trúc (kiểm tra tự động) |
| O5 | Đánh giá bằng Dice, IoU, Precision, Recall, HD95, có khoảng tin cậy và kiểm định thống kê | Bảng kết quả kèm CI 95%; kiểm định Wilcoxon theo cặp |
| O6 | Ablation 2 × 2 (kiến trúc × loss) | 4 cấu hình × 3 seed |
| O7 | Phân tích lỗi theo loại lỗi và đặc điểm nốt | 8 nhóm (xem [13](13_failure_analysis.md)), có ví dụ và thống kê |
| O8 | Demo minh họa | Ứng dụng chạy cục bộ, có cảnh báo "không phải chẩn đoán" |

## 6. Phạm vi

### Trong phạm vi
- CT ngực của LIDC-IDRI (Modality = CT).
- Nốt **≥ 3 mm** có contour (chỉ loại này có ground truth pixel-level).
- Model **2D** trên lát cắt axial, huấn luyện theo **patch** quanh nốt cùng patch âm.
- Phân đoạn nhị phân: nốt / nền.

### Ngoài phạm vi
- MRI, X-quang ngực (CR/DX) có trong collection.
- Nốt < 3 mm và non-nodule (chỉ có tọa độ tâm, không có contour).
- Phân loại ác tính, chẩn đoán ung thư.
- Model 3D, hệ thống CAD phát hiện đầy đủ theo chuẩn LUNA16 (FROC/CPM).
- Đánh giá trên dữ liệu bệnh viện khác (external validation). Nêu là hạn chế.

### ⚠️ Vấn đề phạm vi: chữ "phát hiện" trong tên đề tài

Tên đề tài có cả "**phát hiện**" và "**phân đoạn**". Nếu model chỉ được huấn luyện và đánh giá trên patch **đã được cắt quanh nốt có sẵn**, thì model **không** phát hiện gì cả, vì vị trí nốt đã được cho trước. Hội đồng có thể chỉ ra điểm này.

| Phương án | Mô tả | Chi phí | Rủi ro |
|-----------|-------|---------|--------|
| **A** | Chỉ phân đoạn patch quanh nốt; tên đề tài giữ nguyên | Thấp | Tên đề tài không khớp nội dung, dễ bị hỏi vặn |
| **B** | Phân đoạn là nhiệm vụ chính. **Thêm đánh giá phát hiện thứ cấp**: chạy model trên toàn bộ lát cắt (sliding window, giới hạn trong vùng phổi) của các bệnh nhân test, đo *per-nodule sensitivity* và *false positives per scan* | Trung bình | Số false positive có thể cao; phải báo cáo trung thực |
| **C** | Xây hệ thống phát hiện đầy đủ (sinh ứng viên + giảm false positive, FROC/CPM như LUNA16) | Rất cao | Vượt phạm vi khóa luận, dễ không hoàn thành |

**Khuyến nghị: Phương án B.** Phân đoạn vẫn là đóng góp chính; phần "phát hiện" được hiểu là *khả năng model định vị nốt khi chạy trên toàn lát cắt*, đo bằng metric phát hiện chuẩn (sensitivity, FP/scan). Cách này giữ được tên đề tài mà không tuyên bố quá khả năng thực. Patch âm trong lúc huấn luyện (đã có trong config, `roi.negative_ratio`) là điều kiện cần để phương án B khả thi.

## 7. Đầu vào

| Mức | Đầu vào | Định dạng |
|-----|---------|-----------|
| Dữ liệu gốc | Series CT (DICOM) + file XML annotation | `.dcm`, `.xml` |
| Model (huấn luyện) | Patch 2D đã tiền xử lý: 1 kênh, 128 × 128, giá trị trong [0, 1] sau windowing | tensor `float32 [B, 1, 128, 128]` |
| Model (suy luận) | Lát cắt axial (512 × 512) hoặc cả series | sliding window theo patch 128 × 128 |

## 8. Đầu ra

| Mức | Đầu ra |
|-----|--------|
| Model | Bản đồ xác suất `[0, 1]` cho mỗi pixel, rồi mask nhị phân sau khi áp ngưỡng τ (chọn trên tập validation) |
| Hậu xử lý | Các thành phần liên thông = ứng viên nốt, kèm diện tích (mm²), đường kính lớn nhất (mm), vị trí |
| Báo cáo | Metric (CSV/JSON), hình overlay, các ca thất bại |

**[DECISION]** Mọi đầu ra đều mang dòng cảnh báo: *"Kết quả phân đoạn nốt phổi phục vụ nghiên cứu, không phải chẩn đoán."*

## 9. Dataset

LIDC-IDRI là dataset CT ngực công khai lớn nhất có contour nốt phổi do **nhiều bác sĩ** vẽ độc lập. Chi tiết ở [03_dataset_specification.md](03_dataset_specification.md).
**[FACT]** 1010 bệnh nhân (TCIA), 1018 case CT, mỗi case được 4 bác sĩ đọc theo quy trình hai pha (Armato et al., 2011; McNitt-Gray et al., 2007).

## 10. Model

| Vai trò | Model | Lý do |
|---------|-------|-------|
| Baseline | **U-Net 2D** (Ronneberger et al., 2015) | Chuẩn mực trong phân đoạn ảnh y khoa, là điểm so sánh mà hội đồng nào cũng chấp nhận |
| Đề xuất | **Attention U-Net 2D** (Oktay et al., 2018) | Thay đổi **tối thiểu và có lý do** so với baseline (attention gate trên skip connection) → so sánh được nhân quả |

**[DECISION]** Chỉ dùng **hai** kiến trúc. Thêm UNet++, TransUNet, nnU-Net, v.v. sẽ làm loãng câu hỏi nghiên cứu, mà GPU 4 GB và thời gian khóa luận không đủ để chạy công bằng nhiều seed.

## 11. Metrics

| Metric | Vai trò |
|--------|---------|
| Dice, IoU | Mức trùng khớp vùng (chính) |
| Precision, Recall | Tách over-segmentation và under-segmentation |
| HD95 (mm) | Sai số biên, đo bằng đơn vị vật lý |
| Per-nodule sensitivity, FP/scan | Đánh giá phát hiện thứ cấp (phương án B) |

**[NOT RECOMMENDED]** Pixel accuracy: nền chiếm > 99% pixel nên model dự đoán toàn nền vẫn đạt accuracy rất cao. Chi tiết ở [10_evaluation_protocol.md](10_evaluation_protocol.md).

## 12. Đóng góp dự kiến (expected contribution)

Phát biểu trung thực, không phóng đại:

1. **Pipeline tái lập được** từ LIDC-IDRI gốc (DICOM + XML) đến mask đồng thuận, có metadata về bất đồng giữa các bác sĩ và mã nguồn mở.
2. **So sánh có kiểm soát** giữa U-Net và Attention U-Net (cùng dữ liệu, cùng split, cùng hyperparameter, nhiều seed, kiểm định thống kê). Kết luận có thể là "attention **không** cải thiện đáng kể". Đó vẫn là một kết quả hợp lệ.
3. **Phân tích lỗi phân tầng** theo kích thước, loại đậm độ và vị trí (cạnh mạch máu, cạnh màng phổi) của nốt, cùng mức đồng thuận giữa các bác sĩ.
4. **Đặt kết quả của model cạnh mức đồng thuận giữa các bác sĩ** (inter-observer agreement) như một mốc tham chiếu: model không thể được kỳ vọng "chính xác hơn" chính ground truth vốn đã không chắc chắn.

**[NOT RECOMMENDED]** Tuyên bố "vượt state-of-the-art". Các paper khác dùng định nghĩa ground truth, tập nốt và cách chia dữ liệu khác nhau, nên so sánh con số trực tiếp là **không hợp lệ** (xem [02](02_literature_review.md), mục 4).

---

## Architecture overview

```
┌─────────────────────────── DATA LAYER (src/data) ─────────────────────────────┐
│ data/raw/LIDC-IDRI                                                            │
│   ├─ DICOM ──► dicom_loader ──► CTVolume (raw, spacing, z, SOP UID)           │
│   └─ XML ────► xml_parser ────► reader annotations (≤4 bác sĩ / scan)         │
│                      │                                                        │
│      data_validator (chạy TRƯỚC; lỗi chặn → DỪNG)                             │
│                      ▼                                                        │
│      annotation_processor: gom cụm annotation → nốt vật lý; ROI → slice       │
│                      ▼                                                        │
│      mask_generator: polygon → mask từng bác sĩ → majority ≥2/4 + vote map    │
│                      ▼                                                        │
│      hu_converter → preprocessing (window, normalize, lung ROI, patch)        │
│                      ▼                                                        │
│      dataset_split (THEO BỆNH NHÂN) → data/splits/{train,val,test}.csv        │
└───────────────────────────────────────────────────────────────────────────────┘
                       ▼
┌──────────── LEARNING LAYER (src/datasets, models, losses, training) ──────────┐
│ LungNoduleDataset + augmentation → U-Net | Attention U-Net (model_factory)    │
│ loss: BCE | BCE+Dice → Trainer (AdamW, cosine, AMP, early stopping, ckpt)     │
└───────────────────────────────────────────────────────────────────────────────┘
                       ▼
┌──────────── EVALUATION LAYER (src/metrics, evaluation, inference) ────────────┐
│ evaluator: Dice/IoU/Prec/Rec/HD95 per-nodule + CI + test thống kê             │
│ failure_analysis · visualization · predict (sliding window) · app (demo)      │
└───────────────────────────────────────────────────────────────────────────────┘
  configs/*.yaml điều khiển mọi tầng · experiments/<exp>/ lưu toàn bộ vết thí nghiệm
```

## Tài liệu tham khảo của mục này

- Armato S.G. III et al. (2011). *Medical Physics*, 38(2), 915–931. doi:10.1118/1.3528204
- Hansell D.M. et al. (2008). Fleischner Society: Glossary of terms for thoracic imaging. *Radiology*, 246(3), 697–722. doi:10.1148/radiol.2462070712
- MacMahon H. et al. (2017). Guidelines for management of incidental pulmonary nodules detected on CT images: Fleischner Society 2017. *Radiology*, 284(1), 228–243. doi:10.1148/radiol.2017161659
- National Lung Screening Trial Research Team (2011). Reduced lung-cancer mortality with low-dose computed tomographic screening. *NEJM*, 365(5), 395–409. doi:10.1056/NEJMoa1102873
- Ronneberger O., Fischer P., Brox T. (2015). U-Net. *MICCAI*. doi:10.1007/978-3-319-24574-4_28
- Oktay O. et al. (2018). Attention U-Net. *MIDL*. arXiv:1804.03999
- Bray F. et al. (2024). Global cancer statistics 2022: GLOBOCAN estimates. *CA Cancer J Clin*, 74(3), 229–263. doi:10.3322/caac.21834
- McNitt-Gray M.F. et al. (2007). *Academic Radiology*, 14(12), 1464–1474. doi:10.1016/j.acra.2007.07.021
