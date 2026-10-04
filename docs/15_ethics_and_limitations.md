# 15 — Ethics & Limitations

## 1. Medical AI limitation statement

Đoạn dưới đây được đưa **nguyên văn** (hoặc tương đương) vào khóa luận, README và demo:

> Đây là **nghiên cứu học thuật**. Hệ thống phân đoạn **nốt phổi** trên ảnh CT của bộ dữ liệu công khai LIDC-IDRI.
> Kết quả **không phải chẩn đoán y khoa**, **không** cho biết nốt lành tính hay ác tính, và **không thay thế** đánh giá của bác sĩ chẩn đoán hình ảnh.
> Hiệu năng đo trên LIDC-IDRI **không đảm bảo** hiệu năng trên dữ liệu của bệnh viện, máy chụp hay quy trình khác.
> Hệ thống chưa được thẩm định lâm sàng hay kiểm định ngoài (external validation), và **không được** sử dụng cho mục đích chăm sóc bệnh nhân.

## 2. Đạo đức dữ liệu

| Vấn đề | Thực hành |
|--------|-----------|
| Quyền riêng tư | **[FACT]** Dữ liệu TCIA đã được khử định danh. Không tìm cách tái định danh; không kết nối với nguồn dữ liệu khác để xác định danh tính |
| Giấy phép | **[FACT]** LIDC-IDRI phát hành theo CC BY 3.0; **bắt buộc** trích dẫn dữ liệu (DOI 10.7937/K9/TCIA.2015.LO9QL9SX) và paper mô tả |
| Phân phối lại | Không commit ảnh DICOM hay dữ liệu đã xử lý lên GitHub (`.gitignore` đã chặn). Chỉ phân phối mã nguồn và danh sách ID bệnh nhân của split |
| Đồng thuận bệnh nhân | Thuộc trách nhiệm của dự án thu thập gốc (LIDC/IDRI). **Không** hiển thị "Patient consent: confirmed" trong demo, vì project không có thông tin này (xem [16](16_demo_application.md)) |

## 3. Đạo đức nghiên cứu

- **Không tạo số liệu giả.** Mọi bảng và hình kết quả được sinh từ pipeline, có đường dẫn file nguồn.
- **Không chọn lọc kết quả:** báo cáo mọi experiment trong kế hoạch, kể cả kết quả âm tính; báo cáo mean ± std, không báo cáo seed tốt nhất.
- **Không tuyên bố quá mức:** không viết "chẩn đoán ung thư", "phát hiện ung thư", "chính xác như bác sĩ", "vượt SOTA".
- **Thuật ngữ:** "nốt phổi", không dùng "khối u phổi" ([00](00_project_overview.md) mục 0).
- **Minh bạch:** công bố mã nguồn, config, split; ghi lại mọi thay đổi sau khi đã xem kết quả test.

## 4. Giới hạn (tổng hợp)

### 4.1 Dữ liệu
| ID | Giới hạn |
|----|----------|
| D1 | Ground truth là đồng thuận của bác sĩ trên ảnh, không có xác nhận giải phẫu bệnh ở mức pixel |
| D2 | Bất đồng lớn giữa các bác sĩ: chỉ 928/2669 tổn thương ≥ 3 mm được cả 4 bác sĩ đánh dấu (Armato et al., 2011) |
| D3 | Không có contour cho nốt < 3 mm, nên khả năng với nốt rất nhỏ không được đánh giá |
| D4 | Dữ liệu thu thập trước 2011, từ một số trung tâm tại Mỹ, nhiều thế hệ máy chụp: **domain shift** so với bệnh viện Việt Nam hiện nay (máy, quy trình liều thấp, thuật toán tái tạo, đặc điểm dân số, tỉ lệ bệnh lý như lao) |
| D5 | Độ dày lát không đồng nhất |

### 4.2 Phương pháp
| ID | Giới hạn |
|----|----------|
| M1 | Model 2D, không dùng ngữ cảnh giữa các lát |
| M2 | Huấn luyện trên patch quanh nốt: Dice trên patch **lạc quan hơn** so với bài toán thực tế (phải tự tìm nốt trên toàn scan) |
| M3 | Hyperparameter không tinh chỉnh toàn diện (cố ý, để so sánh công bằng) |
| M4 | Chỉ 2 kiến trúc, 2 loss; không so sánh với các phương pháp hiện đại khác trong cùng điều kiện |

### 4.3 Đánh giá
| ID | Giới hạn |
|----|----------|
| E1 | Chỉ đánh giá nội bộ (internal test split); **không có external validation** |
| E2 | 3 seed: ước lượng biến thiên còn thô |
| E3 | Nhãn vessel-adjacent và pleural-adjacent trong failure analysis là heuristic |
| E4 | Không đánh giá với người dùng (bác sĩ), không đo lợi ích lâm sàng hay thời gian tiết kiệm |
| E5 | Không so sánh trực tiếp được với con số của các paper khác (khác GT, khác tập nốt, khác split) |

## 5. Điều kiện cần trước khi có thể nghĩ đến ứng dụng thực tế

Nêu trong phần "Hướng phát triển" để cho thấy hiểu biết về khoảng cách từ nghiên cứu đến lâm sàng:
1. External validation trên dữ liệu đa trung tâm, có dữ liệu địa phương.
2. Đánh giá phát hiện đầy đủ (FROC) trên toàn scan.
3. Hiệu chỉnh xác suất (calibration) và định lượng độ không chắc chắn.
4. Nghiên cứu đọc phim có bác sĩ tham gia (reader study).
5. Tuân thủ quy định về thiết bị y tế dùng phần mềm (software as a medical device) của cơ quan quản lý.
