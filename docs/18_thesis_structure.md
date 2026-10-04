# 18 — Thesis Structure

Khung đề xuất cho một khóa luận khoảng 60–80 trang. Mỗi chương ghi rõ tài liệu kỹ thuật nào là nguồn nội dung.

## Phần mở đầu
- Lời cam đoan, lời cảm ơn, tóm tắt (tiếng Việt và tiếng Anh, ≤ 1 trang mỗi bản; phải có con số kết quả chính **thật**)
- Mục lục, danh mục hình, danh mục bảng, **danh mục từ viết tắt và thuật ngữ** (CT, HU, DICOM, ROI, DSC, IoU, HD95, GGO, …)

---

## CHƯƠNG 1 — Tổng quan (khoảng 8–10 trang)
**Nguồn:** [00](00_project_overview.md), [01](01_problem_definition.md)

| | Nội dung |
|---|---|
| **Mục tiêu chương** | Người đọc hiểu vấn đề, vì sao quan trọng, khóa luận làm gì và **không** làm gì |
| **Nội dung** | 1.1 Bối cảnh: ung thư phổi, tầm soát CT liều thấp, vai trò của nốt phổi · 1.2 Phân biệt detection / segmentation / malignancy classification / diagnosis · 1.3 Phát biểu bài toán · 1.4 Mục tiêu tổng quát và cụ thể · 1.5 Phạm vi và giới hạn phạm vi · 1.6 Đóng góp · 1.7 Bố cục khóa luận |
| **Hình** | H1.1 Ví dụ lát CT có nốt phổi (từ LIDC, có contour) · H1.2 Sơ đồ tổng quan pipeline |
| **Bảng** | B1.1 Phân biệt 4 khái niệm (từ [00] mục 0) |
| **Biểu đồ** | — |
| **Kết quả** | — |

## CHƯƠNG 2 — Cơ sở lý thuyết (khoảng 15–18 trang)
**Nguồn:** [02](02_literature_review.md), [03](03_dataset_specification.md) mục 2, [07](07_unet_baseline.md), [08](08_proposed_model.md), [09](09_training_strategy.md) mục 2, [10](10_evaluation_protocol.md) mục 2

| | Nội dung |
|---|---|
| **Mục tiêu chương** | Trang bị kiến thức nền để hiểu chương 3; chỉ ra khoảng trống nghiên cứu |
| **Nội dung** | 2.1 Ảnh CT: nguyên lý, HU, windowing, DICOM, spacing · 2.2 Nốt phổi: định nghĩa, phân loại theo đậm độ, vị trí · 2.3 CNN và phân đoạn ngữ nghĩa · 2.4 U-Net · 2.5 Cơ chế attention, Attention U-Net · 2.6 Hàm loss cho phân đoạn mất cân bằng · 2.7 Metric đánh giá · 2.8 Các nghiên cứu liên quan trên LIDC-IDRI và LUNA16 · 2.9 Khoảng trống nghiên cứu |
| **Hình** | H2.1 Thang HU và ảnh hưởng của windowing (cùng lát, 3 cửa sổ) · H2.2 Kiến trúc U-Net · H2.3 Attention gate · H2.4 Minh họa Dice/IoU/HD95 |
| **Bảng** | B2.1 Bảng HU các mô · B2.2 So sánh loss · B2.3 Bảng tổng quan tài liệu (Paper, Year, Dataset, Model, Task, Metrics, Result, Limitation) · B2.4 Vì sao không so sánh trực tiếp con số giữa các paper |
| **Biểu đồ** | — |
| **Kết quả** | — |

## CHƯƠNG 3 — Dữ liệu và phương pháp (khoảng 15–20 trang)
**Nguồn:** [03](03_dataset_specification.md)–[09](09_training_strategy.md), [14](14_reproducibility.md)

| | Nội dung |
|---|---|
| **Mục tiêu chương** | Mô tả đủ chi tiết để người khác **tái lập** được |
| **Nội dung** | 3.1 Dataset LIDC-IDRI và quy trình annotation · 3.2 Xây dựng ground truth: gom cụm, polygon → mask, so sánh các phương án đồng thuận, lựa chọn majority ≥ 2/4 · 3.3 Tiền xử lý: HU, window, chuẩn hóa, lung ROI, patch, augmentation · 3.4 Xây dựng tập dữ liệu và chia theo bệnh nhân · 3.5 Kiến trúc U-Net baseline · 3.6 Attention U-Net · 3.7 Hàm loss · 3.8 Protocol huấn luyện · 3.9 Protocol đánh giá: metric, đơn vị đánh giá, thống kê · 3.10 Thiết kế thực nghiệm và ablation · 3.11 Môi trường và tái lập |
| **Hình** | H3.1 Cấu trúc thư mục DICOM + XML · H3.2 Pipeline annotation (XML → contour → mask từng bác sĩ → đồng thuận) · H3.3 Ví dụ 4 contour bác sĩ + vote map + mask GT · H3.4 Pipeline tiền xử lý (ảnh từng bước) · H3.5 Ví dụ patch dương/âm · H3.6 Sơ đồ chia tập theo bệnh nhân · H3.7 Kiến trúc chi tiết hai model (kích thước tensor) |
| **Bảng** | B3.1 Thống kê dataset (R1) · B3.2 So sánh phương án ground truth · B3.3 Tham số tiền xử lý · B3.4 Thống kê train/val/test · B3.5 Hyperparameter · B3.6 Ma trận thực nghiệm · B3.7 Môi trường phần cứng và phần mềm |
| **Biểu đồ** | C3.1 Phân bố đường kính nốt · C3.2 Phân bố số bác sĩ đánh dấu mỗi nốt · C3.3 Phân bố slice thickness |
| **Kết quả** | Kết quả của bước xây dựng dữ liệu (số nốt, bất đồng giữa các bác sĩ). **Không** đưa kết quả model vào chương này |

## CHƯƠNG 4 — Thực nghiệm và đánh giá (khoảng 15–20 trang)
**Nguồn:** [10](10_evaluation_protocol.md)–[13](13_failure_analysis.md), [17](17_results_template.md)

| | Nội dung |
|---|---|
| **Mục tiêu chương** | Trình bày kết quả **trung thực**, trả lời từng giả thuyết H1–H6 |
| **Nội dung** | 4.1 Quá trình huấn luyện (curves, hội tụ, thời gian, VRAM) · 4.2 Mốc tham chiếu con người · 4.3 Kết quả chính 4 experiment · 4.4 Kiểm định thống kê và trả lời H1–H3 · 4.5 Ablation bổ sung (H4) · 4.6 Phân tích phân tầng (H5, H6) · 4.7 Đánh giá phát hiện thứ cấp · 4.8 Failure analysis · 4.9 Thảo luận: diễn giải, so sánh có điều kiện với các nghiên cứu khác, mối đe dọa tính hợp lệ (threats to validity) |
| **Hình** | H4.1 Curves train/val · H4.2 Panel CT/GT/Pred/Overlay (ca chọn theo quy tắc) · H4.3 Attention maps · H4.4 Ví dụ 8 nhóm lỗi |
| **Bảng** | R2–R8 trong [17](17_results_template.md) |
| **Biểu đồ** | C4.1 Boxplot Dice theo nốt × 4 experiment · C4.2 Dice theo nhóm kích thước · C4.3 Bảng chéo lỗi × bối cảnh (heatmap) · C4.4 (tùy chọn) FROC |
| **Kết quả** | **Toàn bộ** kết quả thực nghiệm, mỗi bảng ghi nguồn file |

## CHƯƠNG 5 — Kết luận và hướng phát triển (khoảng 3–5 trang)
**Nguồn:** [15](15_ethics_and_limitations.md)

| | Nội dung |
|---|---|
| **Mục tiêu chương** | Tổng kết đóng góp **đã chứng minh được**, thừa nhận giới hạn, đề xuất hướng tiếp |
| **Nội dung** | 5.1 Kết quả đạt được so với mục tiêu O1–O8 · 5.2 Trả lời các câu hỏi nghiên cứu · 5.3 Hạn chế (dữ liệu, phương pháp, đánh giá) · 5.4 Hướng phát triển: 2.5D/3D, hard negative mining, mô hình hóa bất đồng giữa bác sĩ (Probabilistic U-Net), external validation trên dữ liệu Việt Nam, calibration · 5.5 Tuyên bố giới hạn y khoa |
| **Hình / Bảng** | B5.1 Đối chiếu mục tiêu và kết quả |
| **Kết quả** | Tóm tắt, không thêm kết quả mới |

---

## Phụ lục
- A. Cấu trúc mã nguồn và hướng dẫn chạy (rút từ README)
- B. File config đầy đủ của các experiment
- C. Bảng kết quả chi tiết theo seed
- D. Thêm ví dụ failure cases
- E. Đặc tả XML của LIDC (rút gọn)

## Tài liệu tham khảo
Chỉ dùng tài liệu đã xác minh ([02](02_literature_review.md) mục 0). Thống nhất một chuẩn trích dẫn (IEEE hoặc APA) theo quy định của khoa. **Bắt buộc** trích dẫn dataset (DOI TCIA) và Armato et al. (2011).

## Lịch viết đề xuất
Viết **chương 3 song song với triển khai** (mỗi phase xong thì viết mục tương ứng ngay khi còn nhớ chi tiết). Chương 2 viết trong lúc chờ huấn luyện. Chương 4 viết sau khi có kết quả. Chương 1 và tóm tắt viết **cuối cùng**.
