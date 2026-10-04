# 03 — Dataset Specification: LIDC-IDRI

## 1. Tổng quan

| Thuộc tính | Giá trị | Nhãn / nguồn |
|------------|---------|--------------|
| Tên | Lung Image Database Consortium and Image Database Resource Initiative | [FACT] |
| Nhà phân phối | The Cancer Imaging Archive (TCIA) | [FACT] |
| Mục đích ban đầu | Tài nguyên tham chiếu để phát triển và đánh giá hệ thống CAD phát hiện/phân tích nốt phổi | [FACT] Armato et al., 2011 |
| Số bệnh nhân | 1010 | [FACT] trang TCIA (abstract của Armato 2011 chỉ nêu 1018 case) |
| Số case CT | 1018 (một số bệnh nhân có > 1 scan) | [FACT] Armato et al., 2011 |
| Số study / series trên TCIA | 1,308 / 1,308 (gồm cả X-quang) | [FACT] TCIA |
| Số ảnh | 244,527 | [FACT] TCIA |
| Dung lượng | 133.16 GB | [FACT] TCIA (Version 4, cập nhật 2020-09-21) |
| Modality | CT, CR, DX: collection có cả ảnh X-quang ngực | [FACT] TCIA |
| Định dạng | DICOM (ảnh) + XML (annotation) | [FACT] |
| Số bác sĩ đọc mỗi scan | 4 (trong tổng số 12 bác sĩ; 7 trung tâm học thuật và 8 công ty tham gia dự án) | [FACT] Armato et al., 2011; Kohl et al., 2018. Ngoại lệ (nếu có) được kiểm tra ở PHASE 02 |
| Giấy phép | Creative Commons Attribution 3.0 (CC BY 3.0); bắt buộc trích dẫn dữ liệu | [FACT] TCIA, DataCite |

**[FACT]** (Armato et al., 2011, abstract) 2669 tổn thương được ít nhất một bác sĩ đánh dấu là "nodule ≥ 3 mm", trong đó 928 tổn thương (34.7%) được **cả bốn** bác sĩ đánh dấu như vậy. Con số này cho thấy mức bất đồng giữa các bác sĩ là **rất lớn** và là đặc tính cốt lõi của dataset. Abstract cũng nêu 7371 tổn thương được ít nhất một bác sĩ đánh dấu là "nodule" (mọi kích thước). (Đã đối chiếu với abstract trên PubMed.)

## 2. Khái niệm nền tảng về ảnh CT

### 2.1 DICOM
**[FACT]** *Digital Imaging and Communications in Medicine*: chuẩn lưu trữ và trao đổi ảnh y tế. Mỗi file `.dcm` chứa **pixel data** của một lát cắt và **header** gồm các thẻ (tag) mô tả bệnh nhân, máy chụp và hình học ảnh.

Các tag quan trọng với project:

| Tag | Ý nghĩa | Dùng để |
|-----|---------|---------|
| `PatientID` | Mã bệnh nhân (`LIDC-IDRI-0001`, …) | **Chia tập theo bệnh nhân** |
| `StudyInstanceUID` | Định danh lần khám | Liên kết với XML |
| `SeriesInstanceUID` | Định danh series | Liên kết với XML, gom lát cắt |
| `SOPInstanceUID` | Định danh từng ảnh | XML tham chiếu ROI qua tag này |
| `Modality` | CT / CR / DX | Lọc chỉ lấy CT |
| `ImagePositionPatient` | Tọa độ (x, y, z) mm của góc trên-trái ảnh | **Sắp xếp lát cắt** theo z |
| `PixelSpacing` | Khoảng cách pixel (hàng, cột), mm | Đổi pixel → mm (diện tích, HD95) |
| `SliceThickness` | Độ dày lát danh nghĩa | Tham khảo; **không** dùng thay khoảng cách lát |
| `RescaleSlope`, `RescaleIntercept` | Hệ số đổi giá trị lưu trữ → HU | Chuyển sang HU |
| `Rows`, `Columns` | Kích thước ảnh | Kiểm tra nhất quán |

### 2.2 Study, Series, Slice

```
Patient (LIDC-IDRI-0001)
 └── Study  (một lần khám; StudyInstanceUID)
      └── Series (một lần tái tạo ảnh; SeriesInstanceUID)
           └── Slice / Instance (một ảnh 2D; SOPInstanceUID)  × ~100–500
```

- **Study:** một lần bệnh nhân đến chụp, có thể gồm nhiều series.
- **Series:** một bộ ảnh được tái tạo theo cùng tham số (ví dụ cùng kernel, cùng độ dày lát). Trong LIDC, annotation gắn với **một series CT cụ thể**.
- **Slice:** một ảnh 2D theo mặt phẳng axial (ngang).

### 2.3 Pixel spacing, slice thickness, slice spacing

| Đại lượng | Định nghĩa | Lưu ý cho LIDC |
|-----------|------------|----------------|
| Pixel spacing | Kích thước một pixel trong mặt phẳng axial (mm) | Khác nhau giữa các scan → một nốt 6 mm chiếm số pixel khác nhau |
| Slice thickness | Bề dày vật lý mà một lát cắt đại diện | **[ASSUMPTION]** khác nhau đáng kể giữa các scan. LUNA16 đã phải loại các scan có slice thickness > 3 mm (Setio et al., 2017). Phân bố thực tế đo ở PHASE 02 |
| Slice spacing | Khoảng cách giữa tâm hai lát liên tiếp, tính từ `ImagePositionPatient[2]` | Có thể **nhỏ hơn** thickness (tái tạo chồng lấp) |

**[DECISION]** Khoảng cách lát được tính từ chênh lệch `ImagePositionPatient[2]`, **không** lấy từ `SliceThickness`.
**[DECISION]** Thứ tự lát sắp theo `ImagePositionPatient[2]`, **không** theo `InstanceNumber` hay tên file.

### 2.4 Hounsfield Unit (HU)

**[FACT]** HU là thang đo suy giảm tia X tuyến tính, chuẩn hóa theo nước:

$$HU = 1000 \times \frac{\mu - \mu_{water}}{\mu_{water} - \mu_{air}}$$

Giá trị lưu trong DICOM được đổi sang HU bằng: `HU = stored_value × RescaleSlope + RescaleIntercept`.

| Mô | HU (xấp xỉ) [FACT, giá trị tham khảo thông dụng] |
|----|------|
| Không khí | −1000 |
| Nhu mô phổi (chứa khí) | khoảng −900 đến −500 |
| Mỡ | khoảng −100 đến −50 |
| Nước | 0 |
| Mô mềm, nốt đặc | khoảng +20 đến +80 |
| Xương | > +400 |

**Ý nghĩa với bài toán:** nốt đặc (mô mềm) nằm giữa nhu mô phổi chứa khí nên có độ tương phản cao. Nốt **kính mờ (ground-glass)** có HU chỉ cao hơn nhu mô một chút nên tương phản thấp, khó phân đoạn hơn. **[HYPOTHESIS]** H5, kiểm tra trong failure analysis.

## 3. Cấu trúc annotation XML

### 3.1 Quy trình đọc hai pha
**[FACT]** (Armato et al., 2011; McNitt-Gray et al., 2007)
1. **Blinded read:** mỗi bác sĩ đọc độc lập.
2. **Unblinded read:** mỗi bác sĩ xem kết quả *ẩn danh* của ba người còn lại rồi tự điều chỉnh annotation của mình.
3. **Không** có bước ép đạt đồng thuận. XML lưu kết quả **unblinded** của từng bác sĩ.

### 3.2 Ba loại tổn thương

| Loại | Điều kiện | Annotation | Dùng cho phân đoạn? |
|------|-----------|------------|---------------------|
| Nodule ≥ 3 mm | Bác sĩ đánh giá là nốt, đường kính ≥ 3 mm | **Contour đầy đủ** trên mỗi lát + 9 đặc điểm | **Có** |
| Nodule < 3 mm | Nốt nhỏ, không rõ là lành tính | Chỉ **tâm** (1 điểm) | Không |
| Non-nodule ≥ 3 mm | Tổn thương khác, không phải nốt | Chỉ **tâm** | Không (có thể dùng để phân tích FP) |

### 3.3 Cây XML (rút gọn)

```xml
<LidcReadMessage>
  <ResponseHeader>
    <StudyInstanceUID>…</StudyInstanceUID>
    <SeriesInstanceUid>…</SeriesInstanceUid>
  </ResponseHeader>
  <readingSession>                       <!-- một bác sĩ -->
    <servicingRadiologistID>…</servicingRadiologistID>
    <unblindedReadNodule>
      <noduleID>…</noduleID>             <!-- chỉ có nghĩa TRONG phiên của bác sĩ này -->
      <characteristics>                  <!-- chỉ có với nodule ≥ 3 mm -->
        <subtlety/> <internalStructure/> <calcification/> <sphericity/>
        <margin/> <lobulation/> <spiculation/> <texture/> <malignancy/>
      </characteristics>
      <roi>                              <!-- một contour trên một lát -->
        <imageZposition>…</imageZposition>
        <imageSOP_UID>…</imageSOP_UID>
        <inclusion>TRUE</inclusion>      <!-- FALSE = vùng loại trừ -->
        <edgeMap><xCoord>…</xCoord><yCoord>…</yCoord></edgeMap>  <!-- lặp lại -->
      </roi>
    </unblindedReadNodule>
    <nonNodule> … <locus><xCoord/><yCoord/></locus> </nonNodule>
  </readingSession>
  <!-- tối đa 4 readingSession -->
</LidcReadMessage>
```

**[ASSUMPTION]** Tên thẻ và namespace có thể khác nhẹ giữa các file (chữ hoa/thường, phiên bản). Parser phải phát hiện namespace tự động và kiểm tra trên **toàn bộ** XML ở PHASE 04.

### 3.4 Các điểm bẫy (gotchas) đã biết

| # | Bẫy | Hệ quả nếu bỏ qua | Xử lý |
|---|-----|-------------------|-------|
| G1 | `noduleID` **không liên kết** giữa các bác sĩ | Đếm 1 nốt thành 4 nốt; không tính được đồng thuận | Gom cụm theo không gian ([04](04_annotation_pipeline.md)) |
| G2 | `inclusion = FALSE` | Mask bị lấp mất lỗ (ví dụ vùng hang) | Trừ vùng này khỏi mask của bác sĩ đó |
| G3 | Contour vẽ sát **bên ngoài** nốt | Mask lớn hơn thực tế khoảng 1 pixel | Tùy chọn `include_contour_boundary`, kiểm tra trực quan ở PHASE 07 |
| G4 | `edgeMap` là (x = cột, y = hàng) | Mask bị lật/xoay | Test đơn vị + hình QC |
| G5 | Collection chứa XML của X-quang (không phải CT) | Parser lỗi hoặc gán nhầm | Bỏ qua root khác `LidcReadMessage` |
| G6 | ROI tham chiếu `imageSOP_UID` không có trong series | ROI "mồ côi" | Dự phòng bằng `imageZposition`; ghi log; **DỪNG** nếu tỉ lệ lỗi đáng kể |
| G7 | `malignancy` là điểm **chủ quan** 1–5 | Bị dùng sai thành nhãn ung thư | **Không** dùng làm nhãn; chỉ lưu metadata (nếu cần) |

### 3.5 Chín đặc điểm (characteristics)

**[FACT]** Mỗi nodule ≥ 3 mm được bác sĩ chấm: *subtlety, internalStructure, calcification, sphericity, margin, lobulation, spiculation, texture, malignancy*.

**[DECISION]** Chỉ dùng **subtlety** (độ khó thấy) và **texture** (đặc / bán đặc / kính mờ) làm biến **phân tầng** trong failure analysis. Mỗi nốt lấy **trung vị** điểm của các bác sĩ. Không dùng đặc điểm nào làm nhãn huấn luyện.

## 4. Đơn vị dữ liệu trong project

```
patient_id ─┬─ series_uid (CT) ─┬─ nodule (sau khi gom cụm) ─┬─ slice_index ─ sample (patch)
            │                   │  radiologist_count ∈ {1..4} │
            │                   │  diameter_mm, texture, ...  │
```

**[DECISION]** Đơn vị **chia tập** là `patient_id`. Đơn vị **đánh giá chính** là `nodule` ([10](10_evaluation_protocol.md)).

## 5. Giới hạn của dataset

| ID | Giới hạn | Nhãn | Tác động |
|----|----------|------|----------|
| L1 | Ground truth là ý kiến bác sĩ trên ảnh, không có giải phẫu bệnh ở mức pixel | [LIMITATION] | "Đúng" mang tính đồng thuận, không tuyệt đối |
| L2 | Bất đồng lớn giữa các bác sĩ, nhất là với nốt nhỏ hoặc biên mờ | [LIMITATION] | Trần hiệu năng thực tế bị giới hạn bởi mức đồng thuận |
| L3 | Dữ liệu thu thập từ nhiều máy, nhiều quy trình khác nhau, chủ yếu tại Mỹ | [LIMITATION] | Domain shift khi áp dụng ở bệnh viện khác |
| L4 | Độ dày lát không đồng nhất | [LIMITATION] | Scan lát dày làm nốt nhỏ chỉ xuất hiện trên 1–2 lát |
| L5 | Không có contour cho nốt < 3 mm | [LIMITATION] | Không đánh giá được khả năng với nốt rất nhỏ |
| L6 | Dữ liệu cũ (thu thập trước 2011) | [LIMITATION] | Kỹ thuật CT hiện đại (liều thấp, tái tạo lặp) có thể khác |
| L7 | Mất cân bằng: pixel nốt chiếm tỉ lệ rất nhỏ | [FACT] | Cần patch-based và loss phù hợp |

## 6. Cách tải và tổ chức

1. Tải manifest `.tcia` của LIDC-IDRI từ trang TCIA, mở bằng **NBIA Data Retriever**.
2. Chọn định dạng thư mục "Descriptive Directory Name" (dễ đọc hơn).
3. Đặt vào `data/raw/LIDC-IDRI/` hoặc đặt biến môi trường `LIDC_IDRI_DIR`.
4. Chạy `python scripts/01_validate_raw_data.py`. Report thực tế sẽ được dùng để điền bảng thống kê ở mục 7.

**[ASSUMPTION]** Cấu trúc thư mục sau khi tải: `LIDC-IDRI-XXXX/<study>/<series>/*.dcm` cùng với file `.xml` trong cùng thư mục series. Kiểm chứng ở PHASE 02.

## 7. Thống kê sẽ được đo (điền ở PHASE 02–05, KHÔNG điền tay)

| Thống kê | Giá trị | File nguồn |
|----------|---------|------------|
| Số bệnh nhân có ít nhất 1 series CT | — | `data/interim/validation_report.json` |
| Số series CT hợp lệ | — | idem |
| Số file XML CT | — | idem |
| Phân bố pixel spacing / slice spacing | — | `results/metrics/raw_data_validation.csv` |
| Số nốt vật lý ≥ 3 mm theo số bác sĩ đánh dấu (1/2/3/4) | — | `data/interim/annotations/nodules.csv` |
| Số nốt còn lại sau majority ≥ 2/4 | — | idem |
| Phân bố đường kính nốt | — | idem |

## 8. Tài liệu tham khảo

- Armato S.G. III et al. (2011). *Medical Physics*, 38(2), 915–931. doi:10.1118/1.3528204
- Armato S.G. III et al. (2015). Data From LIDC-IDRI [Data set]. TCIA. doi:10.7937/K9/TCIA.2015.LO9QL9SX
- McNitt-Gray M.F. et al. (2007). The LIDC data collection process for nodule detection and annotation. *Academic Radiology*, 14(12), 1464–1474. doi:10.1016/j.acra.2007.07.021
- Kohl S.A.A. et al. (2018). A Probabilistic U-Net for segmentation of ambiguous images. *NeurIPS*. arXiv:1806.05034
- Clark K. et al. (2013). The Cancer Imaging Archive (TCIA). *J Digit Imaging*, 26(6), 1045–1057. doi:10.1007/s10278-013-9622-7

## 9. Ghi chú xác minh

Các số liệu từ TCIA đã được đối chiếu với trang collection (bản lưu trữ 2026-02-11) và DataCite vào ngày 2026-10-04. Số liệu *thực tế trên bản tải về* (số series CT, số XML, dung lượng) vẫn phải được đo ở PHASE 02 và ghi vào mục 7.
