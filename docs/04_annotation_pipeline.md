# 04 — Annotation Pipeline: DICOM + XML → Ground-truth mask

Code: `src/data/xml_parser.py` (PHASE 04), `annotation_processor.py` (05), `mask_generator.py` (06), `evaluation/visualization.py` (07).

## 1. Luồng xử lý

```
DICOM series ──► CTVolume: lát sắp theo z, map SOPInstanceUID → slice_index, spacing
     +
XML ─────────► readingSession × K (K ≤ 4 bác sĩ)
                   └─ unblindedReadNodule (≥3 mm) ─ roi × n (mỗi roi = 1 lát)
                                                       └─ edgeMap: [(x,y), …], inclusion
     ▼
[1] ROI → slice_index        qua imageSOP_UID (dự phòng: imageZposition ± ½ spacing)
     ▼
[2] Gom cụm theo bác sĩ      annotation của các bác sĩ khác nhau → cùng 1 nốt vật lý
     ▼
[3] Contour → Polygon        chuỗi điểm (x=cột, y=hàng) khép kín
     ▼
[4] Polygon → mask bác sĩ    tô đa giác; trừ vùng inclusion=FALSE
     ▼
[5] Mask bác sĩ → GT         majority ≥ 2/4 + vote map (0..4) + IoU từng cặp bác sĩ
     ▼
[6] QC trực quan             CT + contour từng bác sĩ + mask đồng thuận (PHASE 07)
```

## 2. Chi tiết từng bước

### [1] Ánh xạ ROI → lát cắt
- **Chính:** `imageSOP_UID` → `slice_index` qua bản đồ SOP UID của series.
- **Dự phòng:** `imageZposition` khớp với z của lát gần nhất, sai lệch < ½ slice spacing.
- **Kiểm soát:** ghi log mọi lần dùng dự phòng và mọi ROI không khớp được. **Gate:** nếu số ROI không khớp > 0 ở nốt ≥ 3 mm thì **DỪNG** và điều tra trước khi đi tiếp.

### [2] Gom cụm annotation thành nốt vật lý
**[FACT]** `noduleID` chỉ có nghĩa bên trong phiên của một bác sĩ, nên phải ghép annotation giữa các bác sĩ.

Thuật toán đề xuất:
1. Với mỗi annotation, tính **tâm 3D theo mm** (dùng spacing thật, không dùng pixel).
2. Ghép cặp các annotation có khoảng cách tâm < `cluster_distance_mm` (mặc định 5 mm, **[ASSUMPTION]**, kiểm chứng ở PHASE 05). Dùng single-linkage hoặc connected components trên đồ thị.
3. **Ràng buộc:** mỗi cụm có tối đa 1 annotation của mỗi bác sĩ. Cụm vi phạm thì đánh dấu `ambiguous`, ghi vào báo cáo bất đồng, **không** tự gộp.
4. Kiểm chứng: so phân bố `radiologist_count` với số liệu công bố (928 nốt được cả 4 bác sĩ đánh dấu, Armato 2011). Nếu khác nhiều thì xem lại ngưỡng.

**Tham chiếu:** thư viện `pylidc` có hàm `cluster_annotations()` làm việc tương tự. **[DECISION]** Project tự cài đặt để minh bạch, và dùng `pylidc` để **đối chiếu chéo** trên một mẫu ngẫu nhiên (ví dụ 50 bệnh nhân).

### [3]–[4] Contour → polygon → mask
- Tô đa giác bằng `skimage.draw.polygon(rows=y, cols=x, shape)`.
- `inclusion = FALSE` → `mask_k &= ~polygon` (trừ ra).
- **Biên contour:** **[FACT]** theo tài liệu LIDC, contour được vẽ để biên nằm **ngay ngoài** nốt. Tùy chọn `include_contour_boundary`:
  - `true` (mặc định): tô cả biên, mask hơi lớn hơn nốt khoảng 1 pixel. Đơn giản, tương thích với `pylidc`.
  - `false`: loại biên, sát nốt hơn, nhưng nốt rất nhỏ có thể mất gần hết diện tích.
  - **[DECISION]** giữ `true` cho baseline. Ghi rõ trong khóa luận. Kiểm tra trực quan ở PHASE 07.

### [5] Gộp nhiều bác sĩ thành ground truth

#### So sánh các phương án

Ký hiệu $v(u)$ là số bác sĩ tô pixel $u$, $K$ là số bác sĩ đọc scan.

| Phương án | Quy tắc | Ưu điểm | Nhược điểm | Ảnh hưởng lên kết quả |
|-----------|---------|---------|------------|------------------------|
| **Union** | $v(u) \ge 1$ | Không bỏ sót vùng bác sĩ nào nghi ngờ; recall-oriented | Giữ cả annotation của **một** bác sĩ (có thể là nhận định thiểu số); mask phình to; nhiều nốt "chỉ 1 người thấy" | Mask lớn: model học xu hướng over-segment; Dice tăng giả tạo với nốt lớn; nhiều nốt khó (nhiễu nhãn) |
| **Intersection** | $v(u) = K$ (hoặc = số bác sĩ vẽ nốt đó) | Chỉ giữ vùng chắc chắn nhất | Mask nhỏ, co về lõi; nốt nhỏ có thể **biến mất**; rất phụ thuộc người vẽ nhỏ nhất | Model học xu hướng under-segment; tập nốt bị lệch về nốt dễ, lớn → kết quả lạc quan, không đại diện |
| **Majority voting** | $v(u) \ge \lceil 0.5K \rceil$ (≥ 2/4) | Cân bằng; giảm ảnh hưởng của ý kiến ngoại lai; dễ giải thích; thông dụng trong các nghiên cứu dùng LIDC | Với $K = 4$, ngưỡng 2/4 "hòa" (2 có, 2 không) vẫn tính là nốt; mất thông tin về độ không chắc chắn | Mức trung tính; là điểm tham chiếu phổ biến |
| **Consensus kiểu pylidc** | $v(u) / K_j \ge 0.5$, với $K_j$ = số bác sĩ **vẽ nốt đó** | Có sẵn trong thư viện | Với nốt chỉ 2 người vẽ, quy tắc thành **union** (1/2 ≥ 0.5); nốt chỉ 1 người vẽ vẫn được giữ | Bao gồm nhiều nốt có độ đồng thuận thấp. Cần lọc thêm theo `radiologist_count` |
| **STAPLE** (Warfield et al., 2004) | Ước lượng EM đồng thời GT và độ tin cậy từng bác sĩ | Có cơ sở thống kê; trọng số theo chất lượng từng người đọc | Phức tạp; bác sĩ trong LIDC **ẩn danh và không cố định giữa các scan**, nên mỗi scan chỉ có ≤ 4 người, ước lượng không ổn định | Khó giải thích trước hội đồng; lợi ích không rõ ràng |
| *Consensus thật* (bác sĩ thống nhất một contour) | — | Lý tưởng | **[FACT]** LIDC **không** có bước này | Không khả thi |

#### Khuyến nghị

**Khuyến nghị: Majority voting ≥ 2/4 bác sĩ đọc scan** (`method: majority`, `level: 0.5`, `denominator: all_readers`).

Lý do:
1. **Hợp lệ về khoa học:** ground truth phản ánh ý kiến của ít nhất một nửa hội đồng đọc, loại bỏ các vùng chỉ một bác sĩ thấy (nhiễu nhãn).
2. **Lọc nốt ngầm định:** nốt chỉ 1 bác sĩ đánh dấu không bao giờ đạt 2 phiếu, nên tự động bị loại khỏi tập *nốt dương*. Cần ghi nhận các nốt này (chúng vẫn có thể bị model phát hiện → không nên phạt là FP trong đánh giá phát hiện, xem [01](01_problem_definition.md) mục 5).
3. **Giải thích được:** hội đồng nào cũng hiểu "đa số". Tương thích tinh thần với LUNA16 (nốt được ≥ 3/4 bác sĩ chấp nhận; Setio et al., 2017) nhưng ít khắt khe hơn, nên giữ được nhiều nốt khó hơn.
4. **Không mất thông tin:** vẫn lưu **vote map 0..4** và **IoU từng cặp bác sĩ**, cho phép phân tích kết quả theo mức đồng thuận.

**[NOT RECOMMENDED]**
- Union làm GT chính: chèn nhận định thiểu số vào nhãn, model bị dạy over-segment.
- Intersection làm GT chính: tập nốt bị lệch về nốt lớn, dễ, nên kết quả **lạc quan giả tạo**.
- STAPLE: chi phí lớn, lợi ích không chứng minh được trong điều kiện bác sĩ ẩn danh.

**Tùy chọn (chỉ khi còn thời gian):** chạy lại **mô hình tốt nhất** với GT = union và GT = intersection, để đo **độ nhạy của kết quả theo định nghĩa ground truth**. Đây là phân tích độ nhạy (sensitivity analysis), không phải experiment chính.

**[LIMITATION]** Scan có $K \ne 4$ (nếu có) làm ngưỡng thực tế thay đổi (ví dụ $K = 3$ → ≥ 2/3). Ghi log và báo cáo số lượng ở PHASE 05.

### [6] Metadata bắt buộc cho mỗi mẫu

| Cột | Ý nghĩa |
|-----|---------|
| `patient_id`, `study_uid`, `series_uid` | Truy vết nguồn |
| `slice_index`, `z_mm` | Vị trí lát |
| `nodule_id` | ID nốt vật lý (sau gom cụm), duy nhất trong toàn project |
| `radiologist_count` | Số bác sĩ đã đánh dấu nốt (1..4) |
| `n_readers_scan` | Số bác sĩ đọc scan ($K$) |
| `mask_source` | Ví dụ `majority@0.5/all_readers` |
| `nodule_diameter_mm` | Đường kính lớn nhất trong mặt phẳng (từ mask đồng thuận) |
| `nodule_area_mm2` | Diện tích trên lát |
| `mean_pairwise_iou` | Mức đồng thuận hình học giữa các bác sĩ (cho nốt có ≥ 2 bác sĩ) |
| `subtlety_median`, `texture_median` | Đặc điểm để phân tầng |
| `mask_empty_after_consensus` | `True` nếu nốt bị loại vì không đủ phiếu |

## 3. Kiểm tra chất lượng (PHASE 07)

| Kiểm tra | Cách làm | Tiêu chí đạt |
|----------|----------|--------------|
| Trục x/y không bị đảo | Vẽ contour lên ảnh CT | Contour bao quanh nốt trên ảnh |
| Lát cắt đúng | Contour xuất hiện đúng lát có nốt | 100% trên ≥ 20 nốt ngẫu nhiên |
| Exclusion | Tìm ca có `inclusion=FALSE`, vẽ ra | Lỗ được trừ đúng |
| Đồng thuận | Màu khác nhau cho từng bác sĩ + mask GT | GT nằm trong vùng ≥ 2 contour |
| Đối chiếu pylidc | Dice giữa mask của project và mask của pylidc trên mẫu ngẫu nhiên | Dice ≈ 1 (sai khác phải giải thích được) |

**Gate:** bất kỳ tiêu chí nào không đạt thì **DỪNG**, không chuyển sang tiền xử lý.

## 4. Inter-observer agreement như mốc tham chiếu

Tính **Dice giữa từng cặp bác sĩ** trên các nốt có ≥ 2 annotation. Phân bố này là **mốc tham chiếu con người**:

- **[HYPOTHESIS]** H6: Dice của model so với GT đồng thuận nằm cùng khoảng với Dice giữa các bác sĩ.
- Khi viết khóa luận: so model với mức đồng thuận giữa người với người, thay vì chỉ đưa ra một con số Dice trơ trọi.
- **[LIMITATION]** So sánh này không hoàn toàn cân bằng: GT được tạo từ chính các bác sĩ đó (mỗi bác sĩ là một phần của GT). Một cách so công bằng hơn là *leave-one-reader-out* (so từng bác sĩ với đồng thuận của những người còn lại). Nên làm nếu còn thời gian.
