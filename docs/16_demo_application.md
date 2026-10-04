# 16 — Demo Application

Code: `app/app.py` (PHASE 23), dùng `src/inference/predict.py` (PHASE 22).

## 1. Mục đích

Minh họa trực quan pipeline trong buổi bảo vệ: tải một series CT, xem kết quả phân đoạn nốt phổi trên từng lát, cùng các số đo hình học tính từ mask. Demo **không** phải công cụ lâm sàng.

## 2. Phản biện bản mockup UI hiện có (`img-demo/UI-DEMO.jpg`)

Bản mockup có bố cục tốt (vùng xem chính, ba mặt cắt, metadata DICOM, thanh lát cắt, khối số đo). Tuy vậy, một số thành phần **sai về khoa học hoặc gây hiểu lầm**, phải sửa trước khi cài đặt:

| # | Thành phần trong mockup | Vấn đề | Khuyến nghị |
|---|------------------------|--------|-------------|
| 1 | **"Dice: 0.872 / IoU: 0.791"** hiển thị cho ca đang xem | Dice/IoU **cần ground truth**. Với ca mới (chưa có annotation) thì **không thể tính**. Hiển thị số này với ca mới là **bịa số** | Chỉ hiển thị Dice/IoU khi ca thuộc **tập test LIDC có GT**, với nhãn "So với ground truth (đồng thuận ≥ 2/4 bác sĩ)". Với ca ngoài: ẩn hẳn |
| 2 | **"Conf: 98.4%"** | Xác suất sigmoid **không phải** độ tin cậy đã hiệu chỉnh (model chưa được calibration). Con số một giá trị cho cả model là vô nghĩa | **[NOT RECOMMENDED]** Bỏ. Có thể hiển thị *xác suất cực đại của ứng viên* kèm ghi chú "điểm của model, chưa hiệu chỉnh" |
| 3 | Nhãn **"Sagittal (khối u)"** | Sai thuật ngữ: "khối u" hàm ý ác tính, đối tượng ở đây là nốt phổi | "Sagittal" |
| 4 | Ô thứ hai ghi **"Coronal (Axial)"** | Nhãn mặt cắt sai | "Coronal" |
| 5 | Diện tích 12.46 mm², đường kính 4.21 mm, thể tích 18.73 mm³ | **Không nhất quán** về hình học: hình tròn đường kính 4.21 mm có diện tích ≈ 13.9 mm²; khối cầu đường kính đó có thể tích ≈ 39 mm³. Cho thấy đây là số đặt chỗ | Mọi số đo phải **tính từ mask** × spacing thật; ghi rõ định nghĩa (đường kính lớn nhất trên lát, thể tích = số voxel × thể tích voxel) |
| 6 | **"Patient Consent: Confirmed"** | Project không có và không quản lý thông tin đồng thuận. Dữ liệu là dữ liệu công khai đã khử định danh | **[NOT RECOMMENDED]** Bỏ. Thay bằng "Dữ liệu: LIDC-IDRI (công khai, đã khử định danh)" |
| 7 | Mô hình phổi **3D phát sáng** ở trung tâm | Cần phân đoạn phổi 3D + render; không phải đóng góp của khóa luận; dễ tạo ấn tượng "sản phẩm thương mại" vượt thực tế | Thay bằng lát axial lớn với overlay. 3D là tùy chọn cuối cùng |
| 8 | "A.I. Model Active", "AI for Better Healthcare" | Văn phong quảng cáo | Văn phong học thuật, trung tính |
| 9 | Không có dòng cảnh báo | Thiếu disclaimer | Disclaimer cố định ở chân trang, luôn hiển thị |

Bản phác thảo sơ đồ pipeline (`img-demo/image.png`) cũng có bảng ablation với **số liệu minh họa** (Dice 0.84–0.89) và tiêu đề "khối u phổi … MRI/CT". Phải sửa trước khi dùng trong khóa luận hoặc slide ([00](00_project_overview.md) mục 0).

## 3. Phương án phạm vi

| Phương án | Nội dung | Công sức | Đánh giá |
|-----------|----------|----------|----------|
| **A. Tối thiểu** | Upload series (zip) → chọn lát bằng slider → CT (cửa sổ phổi) / mask / overlay; bảng ứng viên (vị trí, đường kính, diện tích) | Thấp | Đủ để minh họa |
| **B. Chuẩn** | A + 3 mặt cắt (axial/coronal/sagittal, đúng tỉ lệ spacing) + biểu đồ diện tích dự đoán theo lát + chế độ "ca test có GT" hiển thị GT, prediction và Dice | Trung bình | **Khuyến nghị** |
| C. Đầy đủ | B + render 3D, tài khoản, lưu lịch sử | Cao | **[NOT RECOMMENDED]** Không tăng giá trị khoa học |

**Khuyến nghị: Phương án B**, cài bằng **Gradio**. Lý do: Gradio có sẵn thành phần ảnh/slider/file upload, chạy cục bộ bằng một lệnh, ít mã giao diện, giúp tập trung vào pipeline. Streamlit cũng phù hợp, nhưng mô hình chạy lại toàn bộ script mỗi lần tương tác bất tiện hơn với volume CT lớn.

## 4. Đặc tả chức năng (phương án B)

| Khu vực | Nội dung | Nguồn dữ liệu |
|---------|----------|---------------|
| Đầu vào | Upload `.zip` một series DICOM, **hoặc** chọn một bệnh nhân trong tập test LIDC | `src/inference/predict.py` |
| Thông tin ảnh | Patient ID (ẩn danh của LIDC), Series UID (rút gọn), số lát, pixel spacing, slice spacing | Header DICOM |
| Vùng xem chính | Lát axial, cửa sổ phổi; overlay prediction (đỏ); nếu có GT: GT (xanh lá), vùng trùng (vàng); chú giải màu | |
| Slider lát | Kèm biểu đồ diện tích dự đoán theo lát, để nhảy nhanh đến lát có ứng viên | |
| 3 mặt cắt | Axial / Coronal / Sagittal tại vị trí ứng viên được chọn; tỉ lệ khung theo spacing thật | |
| Bảng ứng viên | ID, lát trung tâm, tọa độ (x, y, z), đường kính lớn nhất (mm), diện tích lớn nhất (mm²), thể tích (mm³), điểm cực đại của model | Tính từ mask |
| Đánh giá (chỉ ca có GT) | Dice, IoU, Precision, Recall, HD95 **của ca này** so với GT đồng thuận | `src/metrics` |
| Thông tin model | Tên model, run_id, dataset_version, ngưỡng τ | `summary.json` |
| Chân trang | **Disclaimer** (xem [15](15_ethics_and_limitations.md) mục 1) | Cố định |

## 5. Yêu cầu kỹ thuật

- Demo **chỉ gọi** `src/inference` và `src/evaluation.visualization`. Không viết lại tiền xử lý (để tránh sai lệch giữa demo và đánh giá).
- Đường dẫn checkpoint lấy từ config, không hard-code.
- Thời gian xử lý một series trên GPU 4 GB: đo và ghi lại (sliding window toàn scan có thể mất vài chục giây). Hiển thị thanh tiến trình.
- Không lưu dữ liệu người dùng upload sau phiên làm việc.

## 6. Kịch bản demo khi bảo vệ (khoảng 3 phút)

1. Mở một ca **test** có GT, nốt đặc cỡ trung bình: cho thấy overlay GT và prediction, các số đo, Dice của ca.
2. Mở một ca **khó** (nốt kính mờ hoặc sát màng phổi): cho thấy lỗi, nối sang phần failure analysis.
3. Chỉ vào disclaimer: nhấn mạnh đây là phân đoạn nốt phổi phục vụ nghiên cứu, không phải chẩn đoán.

**[DECISION]** Các ca demo được chọn từ tập test theo quy tắc nêu trong khóa luận (một ca ở trung vị Dice, một ca thuộc nhóm lỗi), **không** chọn ca đẹp nhất.
