# Data assumptions & decisions log

Mọi giả định về dữ liệu đều được ghi ở đây **trước khi** dùng trong code.
Mỗi mục có trạng thái:

- `ASSUMED`: lấy từ tài liệu công bố, **chưa** kiểm chứng trên bản dữ liệu đã tải.
- `VERIFIED (PHASE xx)`: đã kiểm chứng; ghi kèm số liệu thực tế và đường dẫn tới báo cáo.
- `DECIDED (PHASE xx)`: quyết định thiết kế, có lý do.
- `OPEN`: chưa quyết định.

---

## A. Về dataset LIDC-IDRI

| ID | Giả định | Nguồn | Trạng thái |
|----|----------|-------|------------|
| A1 | 1010 bệnh nhân (TCIA), 1018 case CT (Armato 2011); trên TCIA có 1,308 study/series (gồm cả X-quang), 244,527 ảnh, 133.16 GB, CC BY 3.0. | TCIA (đối chiếu ngày 2026-10-04); Armato et al., 2011 | Số công bố ĐÃ XÁC MINH; số thực tế trên bản tải → PHASE 02 |
| A2 | Collection có cả ảnh X-quang ngực (CR/DX). Phiên bản này **chỉ dùng series có Modality = CT**. | TCIA collection page | ASSUMED → kiểm chứng ở PHASE 02 |
| A3 | Mỗi CT scan có 1 file XML chứa annotation của tối đa 4 bác sĩ chẩn đoán hình ảnh lồng ngực (thuộc nhiều trung tâm khác nhau). Bác sĩ được ẩn danh và không cố định giữa các scan, nên không thể theo dõi "bác sĩ số 1" qua nhiều bệnh nhân. | Armato et al., 2011 | ASSUMED → kiểm chứng ở PHASE 02/04 |
| A4 | Quy trình đọc 2 pha: blinded, rồi unblinded (mỗi bác sĩ xem kết quả của người khác rồi tự chỉnh sửa). **Không ép buộc đồng thuận**, nên bất đồng giữa các bác sĩ là đặc tính của dữ liệu chứ không phải lỗi. | Armato et al., 2011 | ASSUMED |
| A5 | Ba loại tổn thương: *nodule ≥ 3 mm* (có contour + đặc điểm), *nodule < 3 mm* (chỉ có tâm), *non-nodule ≥ 3 mm* (chỉ có tâm). **Chỉ loại đầu tiên dùng được cho phân đoạn.** | LIDC XML documentation | ASSUMED → kiểm chứng ở PHASE 04 |
| A6 | ID nodule trong XML **không liên kết giữa các bác sĩ**; cần gom cụm theo không gian để xác định cùng một nodule vật lý. | Armato et al., 2011; pylidc | ASSUMED → PHASE 05 |
| A7 | Contour có thể có `inclusion = FALSE` (vùng loại trừ/lỗ). | LIDC XML documentation | ASSUMED → PHASE 04/06 |
| A8 | Contour được vẽ sao cho đường biên nằm sát **bên ngoài** nodule. | LIDC documentation | ASSUMED → kiểm chứng trực quan ở PHASE 07 |
| A9 | Độ dày lát cắt và pixel spacing khác nhau giữa các scan (khoảng ~0.6–5 mm theo z). | Armato et al., 2011 | ASSUMED → đo thực tế ở PHASE 02 |
| A10 | Trường `malignancy` (1–5) là **đánh giá chủ quan** của bác sĩ, **không** phải kết quả giải phẫu bệnh. Dự án **không** dùng trường này làm nhãn ung thư. | LIDC documentation | DECIDED (PHASE 00) |

## B. Về ground truth

| ID | Quyết định | Lý do | Trạng thái |
|----|-----------|-------|------------|
| B1 | Không mặc định 1 patient = 1 mask. Mỗi patient có 0..N nodule, mỗi nodule có 1..4 annotation. | A3, A6 | DECIDED (PHASE 00) |
| B2 | Mặc định: majority voting **≥ 50% số bác sĩ đọc scan** (≥ 2/4), theo sơ đồ pipeline của đề tài (`consensus.denominator = all_readers`). Lựa chọn thay thế: tính trên số bác sĩ đã vẽ nodule (`nodule_readers`, tương đương pylidc `consensus(clevel=0.5)`), union, intersection. | Với `nodule_readers`, nodule chỉ có 2 người vẽ sẽ thành union, tức chỉ cần 1 phiếu. `all_readers` khắt khe hơn và loại được nodule chỉ 1 bác sĩ thấy. | DECIDED (PHASE 00), kiểm chứng phân bố số reader ở PHASE 05–06 |
| B3 | Lưu `radiologist_count`, bản đồ số phiếu đồng ý (0..4) và IoU giữa từng cặp bác sĩ để phân tích bất đồng. | Yêu cầu đề tài | DECIDED (PHASE 00) |
| B4 | Tự viết XML parser thay vì phụ thuộc hoàn toàn vào `pylidc` (cần cơ sở dữ liệu riêng, ít được bảo trì). Có thể dùng `pylidc` để **đối chiếu chéo** kết quả. | Minh bạch, kiểm soát được | DECIDED (PHASE 00), xem lại ở PHASE 04 |
| B5 | Ngưỡng gom cụm `cluster_distance_mm` | | OPEN → PHASE 05 |

## C. Về tiền xử lý & huấn luyện

| ID | Quyết định | Lý do | Trạng thái |
|----|-----------|-------|------------|
| C1 | Mô hình 2D, huấn luyện trên patch (mặc định 128×128). | GPU 4 GB (RTX 3050 Laptop); nodule nhỏ so với slice 512×512 | DECIDED (PHASE 00), xem lại ở PHASE 10 |
| C2 | Cửa sổ phổi WL = −600, WW = 1500. | Cửa sổ phổi thông dụng trong lâm sàng | DECIDED (PHASE 00), xem lại ở PHASE 09 |
| C3 | Chia dữ liệu **chỉ theo bệnh nhân**; không có tùy chọn chia theo slice. | Tránh data leakage | DECIDED (PHASE 00) |
| C4 | Bài toán là *segmentation* (kèm phát hiện ở mức patch/slice). Kết quả **không** phải chẩn đoán ung thư. | Phạm vi đề tài | DECIDED (PHASE 00) |
| C5 | Có resample in-plane hay không | | OPEN → PHASE 09 |
| C6 | Cách tính metric khi GT rỗng | | OPEN → PHASE 19 |

---

## Nhật ký thay đổi

| Ngày | Phase | Thay đổi |
|------|-------|----------|
| 2026-10-04 | 00 | Tạo tài liệu, ghi nhận các giả định ban đầu. |
| 2026-10-04 | 00 | Bộ tài liệu kỹ thuật docs/00–20; xác minh trích dẫn; failure analysis 2 trục; thêm `evaluation.failure_thresholds`, `evaluation.detection`. |
