# 13 — Failure Analysis

Code: `src/evaluation/failure_analysis.py` (PHASE 21). Output: `results/failure_cases/`.

## 1. Thiết kế: hai trục độc lập

Tám nhóm được yêu cầu thực ra thuộc **hai loại khác nhau**. Trộn chúng vào một danh sách phân loại loại trừ lẫn nhau là sai về phương pháp, vì một nốt có thể vừa *nhỏ*, vừa *sát màng phổi*, vừa bị *under-segmentation*.

| Trục | Câu hỏi | Nhóm | Loại trừ lẫn nhau? |
|------|---------|------|--------------------|
| **A. Loại lỗi (kết quả)** | Model sai *như thế nào*? | 1 Correct · 2 Under-seg · 3 Over-seg · 4 Missed · 5 Boundary error | **Có**: mỗi nốt thuộc đúng 1 nhóm |
| **B. Đặc điểm nốt (bối cảnh)** | Nốt *thuộc loại nào*? | 6 Small · 7 Vessel-adjacent · 8 Pleural-adjacent (+ texture, mức đồng thuận) | **Không**: nhiều nhãn |

Phân tích chính là **bảng chéo A × B**, ví dụ: "trong các nốt sát màng phổi, bao nhiêu % bị under-segmentation, so với nốt không sát màng phổi?". Bảng này biến failure analysis từ "trưng bày ảnh xấu" thành **bằng chứng định lượng**.

## 2. Quy tắc gán nhóm trục A (định trước, cố định trên validation)

Áp dụng theo thứ tự trên từng **nốt** (metric 3D theo nốt):

| # | Nhóm | Điều kiện |
|---|------|-----------|
| 4 | **Missed nodule** | Dice < 0.1 (dự đoán rỗng hoặc gần như không chồng lấn) |
| 1 | **Correct segmentation** | Dice ≥ t_good (đề xuất: 0.8 hoặc phân vị 75 của Dice giữa các bác sĩ) |
| 2 | **Under-segmentation** | Recall < Precision − δ (δ = 0.2) |
| 3 | **Over-segmentation** | Precision < Recall − δ |
| 5 | **Boundary error** | Các trường hợp còn lại: Dice trung bình, Precision ≈ Recall, sai số chủ yếu ở biên (HD95 cao so với đường kính nốt) |

**[DECISION]** Ngưỡng t_good và δ được **chốt trên tập validation** trước khi chạy test, rồi ghi vào config (`evaluation.failure_thresholds`). Không đổi ngưỡng sau khi xem kết quả test.

## 3. Quy tắc gán nhãn trục B

| # | Nhãn | Cách xác định | Độ tin cậy |
|---|------|---------------|------------|
| 6 | **Small nodule** | Đường kính lớn nhất của mask GT < 6 mm | Cao (đo trực tiếp) |
| 7 | **Vessel-adjacent** | **[ASSUMPTION — heuristic]** LIDC không có annotation mạch máu. Đề xuất: bộ lọc vesselness (Frangi) trên vòng bao 2–5 mm quanh nốt; vượt ngưỡng → gắn nhãn. **Kiểm chứng:** xem tay một mẫu ngẫu nhiên khoảng 50 nốt, báo cáo tỉ lệ đồng ý | Trung bình–thấp |
| 8 | **Pleural-adjacent (juxtapleural)** | Khoảng cách từ biên mask GT đến biên mask phổi (đã closing) < 2 mm | Trung bình (phụ thuộc chất lượng mask phổi) |
| + | Texture | Trung vị điểm `texture` của các bác sĩ: đặc / bán đặc / kính mờ | Cao (từ XML), nhưng là đánh giá chủ quan |
| + | Mức đồng thuận | `radiologist_count`, `mean_pairwise_iou` | Cao |

## 4. Đặc tả từng nhóm

Cột **Example** chỉ có ảnh **sau khi** chạy PHASE 21 (`results/failure_cases/<group>/`). Tài liệu này **không** chứa ví dụ giả.

### 1. Correct segmentation
- **Example:** *(sinh tự động: 5 ca có Dice cao nhất và 5 ca ở trung vị của nhóm)*
- **Cause hypothesis:** nốt đặc, cỡ trung bình, bờ rõ, nằm giữa nhu mô.
- **Evidence:** phân bố kích thước/texture của nhóm so với toàn bộ.
- **Possible solution:** — (đây là nhóm tham chiếu).
- **Limitation:** "Đúng" nghĩa là khớp với đồng thuận, không phải khớp với giải phẫu bệnh.

### 2. Under-segmentation
- **Example:** *(sinh tự động)*
- **Cause hypothesis:** (a) phần kính mờ của nốt bán đặc bị bỏ qua (tương phản thấp); (b) BCE thiên về nền; (c) GT được vẽ rộng (biên ngoài, xem [04](04_annotation_pipeline.md)).
- **Evidence:** tỉ lệ under-seg theo texture; so EXP-01 với EXP-02 (Dice loss có giảm under-seg?).
- **Possible solution:** Dice/Tversky loss (β > α); đa cửa sổ HU (ABL-B).
- **Limitation:** Ranh giới phần kính mờ vốn đã là nơi bác sĩ bất đồng nhiều nhất.

### 3. Over-segmentation
- **Example:** *(sinh tự động)*
- **Cause hypothesis:** model "tràn" sang mạch máu hoặc thành ngực dính liền nốt; ngưỡng τ thấp.
- **Evidence:** tỉ lệ over-seg theo nhãn vessel-adjacent và pleural-adjacent; vị trí pixel FP so với mask phổi.
- **Possible solution:** attention gate (H1b); hậu xử lý (giữ thành phần liên thông chứa xác suất cực đại); tinh chỉnh τ trên val.
- **Limitation:** Hậu xử lý có thể cắt mất nốt thật dính mạch máu.

### 4. Missed nodule
- **Example:** *(sinh tự động)*
- **Cause hypothesis:** nốt rất nhỏ (gần 3 mm), kính mờ mờ nhạt, subtlety thấp, scan lát dày.
- **Evidence:** tỉ lệ bỏ sót theo kích thước, subtlety, slice thickness.
- **Possible solution:** ngữ cảnh 2.5D/3D; tăng tỉ lệ mẫu nốt nhỏ khi huấn luyện; giảm τ (đổi lại có thêm FP).
- **Limitation:** Nốt có `radiologist_count = 2` vốn đã gây tranh cãi giữa các bác sĩ.

### 5. Boundary error
- **Example:** *(sinh tự động)*
- **Cause hypothesis:** nốt bờ tua gai (spiculated) hoặc bờ đa thùy; độ phân giải pixel hạn chế; quy ước vẽ biên ngoài.
- **Evidence:** HD95 so với đường kính; tương quan với điểm margin/spiculation/lobulation.
- **Possible solution:** loss nhạy biên (boundary loss); độ phân giải cao hơn.
- **Limitation:** Sai số ±1 pixel nằm trong mức biến thiên giữa các bác sĩ. Không nên coi là lỗi lâm sàng.

### 6. Small nodule failure (< 6 mm)
- **Example:** *(sinh tự động)*
- **Cause hypothesis:** quá ít pixel (khoảng 4–8 px đường kính); Dice rất nhạy với sai lệch 1 pixel; pooling làm mất tín hiệu.
- **Evidence:** Dice theo nhóm kích thước; so với Dice giữa các bác sĩ trên cùng nhóm.
- **Possible solution:** attention gate (H1); NSD thay vì Dice cho nhóm này; độ phân giải cao hơn.
- **Limitation:** Dice thấp trên nốt nhỏ một phần là **do bản chất metric**, không hẳn do model kém. Phải nói rõ khi diễn giải.

### 7. Vessel-adjacent nodule
- **Example:** *(sinh tự động)*
- **Cause hypothesis:** trên lát 2D, mạch máu cắt ngang có hình tròn và HU tương tự nốt đặc; model 2D không thấy được mạch máu là cấu trúc dạng ống kéo dài.
- **Evidence:** Precision và tỉ lệ over-seg ở nhóm này so với nhóm còn lại; bản đồ attention.
- **Possible solution:** ngữ cảnh 2.5D/3D (nhiều lát liền kề làm kênh đầu vào); hard-negative mining tại mạch máu.
- **Limitation:** Nhãn "vessel-adjacent" là heuristic, có sai số; phải báo cáo tỉ lệ đồng ý khi kiểm tra tay.

### 8. Pleural-adjacent (juxtapleural) nodule
- **Example:** *(sinh tự động)*
- **Cause hypothesis:** nốt dính thành ngực có cùng HU với mô mềm thành ngực, nên khó xác định ranh giới; mask phổi có thể cắt mất nốt.
- **Evidence:** under/over-seg trong nhóm này; % tâm nốt nằm ngoài mask phổi trước khi closing.
- **Possible solution:** mask phổi tốt hơn (closing hoặc convex hull từng phần); không dùng mask phổi để xóa pixel đầu vào.
- **Limitation:** Chính các bác sĩ cũng thường bất đồng về ranh giới nốt và màng phổi.

## 5. Đầu ra

```
results/failure_cases/
├── summary_by_error_type.csv       nhóm A: số lượng, %, theo từng experiment
├── crosstab_error_x_context.csv    bảng chéo A × B (+ texture, đồng thuận)
├── <group>/<nodule_id>.png         panel: CT | GT | Pred | Overlay (+ attention map với EXP-03/04)
└── vessel_label_review.csv         kết quả kiểm tra tay heuristic mạch máu
```

**[DECISION]** Ví dụ trong khóa luận được chọn theo **quy tắc cố định** (ví dụ 3 ca ở trung vị nhóm + 2 ca tệ nhất), **không** chọn tay những ca "đẹp" hay "ấn tượng".
