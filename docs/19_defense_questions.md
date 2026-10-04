# 19 — Defense Questions

38 câu hỏi hội đồng có thể đặt ra, chia theo 13 nhóm. Mỗi câu gồm: **Q** (câu hỏi), **A** (câu trả lời tốt nhất, nói được trong khoảng 30 giây), **T** (giải thích kỹ thuật, để đào sâu khi cần), **F** (câu hỏi tiếp theo có thể bị hỏi).
Chỗ nào ghi *[số liệu từ R…]* thì thay bằng kết quả thật trong [17](17_results_template.md) trước khi bảo vệ.

---

## A. Dataset

**A1. Q:** Vì sao chọn LIDC-IDRI?
**A:** Đây là bộ CT ngực công khai lớn nhất có contour nốt phổi do nhiều bác sĩ vẽ độc lập. Nó là nền của LUNA16 và của nhiều nghiên cứu, nên kết quả có thể đặt trong bối cảnh chung.
**T:** 1010 bệnh nhân, 1018 case; 4 bác sĩ mỗi case, đọc 2 pha; giấy phép CC BY 3.0.
**F:** Vậy sao không dùng LUNA16 cho gọn? → LUNA16 phục vụ *phát hiện* (chỉ có tọa độ tâm trong annotation chính thức), còn khóa luận cần contour để phân đoạn và muốn tự kiểm soát cách xây ground truth.

**A2. Q:** Dataset có bao nhiêu nốt sau khi xử lý? Vì sao khác số liệu công bố?
**A:** *[số liệu từ R1]*. Khác vì tôi chỉ giữ nốt ≥ 3 mm đạt đa số ≥ 2/4 bác sĩ. Bài gốc báo cáo 2669 tổn thương được ≥ 1 bác sĩ đánh dấu là nốt ≥ 3 mm.
**T:** Bảng phân bố theo `radiologist_count` (1/2/3/4) giải thích phần chênh lệch.
**F:** Bỏ nốt chỉ 1 bác sĩ thấy có làm mất thông tin không? → Có, đó là đánh đổi có chủ đích (giảm nhiễu nhãn); các nốt này được loại khỏi patch âm và không bị tính là FP.

**A3. Q:** Dữ liệu có phải chẩn đoán ung thư không?
**A:** Không. Annotation là vị trí và contour nốt do bác sĩ vẽ trên ảnh. Trường "malignancy" là điểm đánh giá chủ quan 1–5, phần lớn không có xác nhận giải phẫu bệnh. Khóa luận không dùng trường này.
**F:** Vậy làm sao mở rộng sang chẩn đoán? → Cần dữ liệu có kết quả giải phẫu bệnh hoặc theo dõi dài hạn; đó là bài toán khác.

## B. Annotation

**B1. Q:** Có 4 bác sĩ, vậy ground truth là của ai?
**A:** Là đồng thuận đa số: một pixel thuộc nốt khi ít nhất 2/4 bác sĩ tô pixel đó. Tôi vẫn lưu bản đồ số phiếu và mức đồng thuận để phân tích.
**T:** $Y(u) = 1[v(u) \ge \lceil 0.5K \rceil]$; so sánh với union, intersection, STAPLE ở [04](04_annotation_pipeline.md).
**F:** Sao không dùng intersection cho "chắc chắn"? → Intersection làm mask co lại và loại các nốt khó, nên tập test lệch về nốt dễ và kết quả lạc quan giả tạo.

**B2. Q:** Làm sao biết annotation của các bác sĩ là cùng một nốt?
**A:** ID nốt trong XML không liên kết giữa các bác sĩ, nên tôi gom cụm theo khoảng cách tâm 3D tính bằng mm, với ràng buộc mỗi cụm có tối đa 1 annotation của mỗi bác sĩ. Kết quả được đối chiếu với pylidc.
**F:** Ngưỡng khoảng cách chọn thế nào? → Kiểm chứng bằng phân bố khoảng cách và so với số liệu công bố; ghi trong DATA_ASSUMPTIONS.

**B3. Q:** Contour được vẽ ở trong hay ngoài biên nốt?
**A:** Theo quy ước của LIDC, contour nằm ngay ngoài nốt. Tôi giữ cả pixel biên (tương thích pylidc) và kiểm tra trực quan; điều này làm mask lớn hơn khoảng 1 pixel.
**F:** Ảnh hưởng gì lên Dice? → Với nốt nhỏ, ±1 pixel tác động đáng kể; đây là lý do báo cáo cả HD95 và phân tầng theo kích thước.

**B4. Q:** Mức bất đồng giữa các bác sĩ cao đến đâu, và nó ý nghĩa gì với kết quả?
**A:** *[số liệu từ R2]*. Đây là "trần" thực tế: không thể kỳ vọng model khớp với GT tốt hơn nhiều so với mức các bác sĩ khớp với nhau.
**T:** iW-Net báo cáo IoU giữa các bác sĩ là 0.59 trên LIDC.

## C. Medical imaging

**C1. Q:** HU là gì, vì sao phải đổi sang HU?
**A:** HU là thang suy giảm tia X chuẩn hóa theo nước (nước = 0, không khí = −1000). Giá trị lưu trữ phụ thuộc máy, còn HU thì so sánh được giữa các máy, nên windowing chỉ có nghĩa trên HU.
**F:** Nếu RescaleIntercept sai thì sao? → Kiểm tra histogram mỗi series: đỉnh khí ≈ −1000.

**C2. Q:** Vì sao chọn cửa sổ −600/1500?
**A:** Đây là cửa sổ phổi lâm sàng, bao gồm dải từ khí đến mô mềm: nốt đặc, nốt kính mờ và nhu mô đều phân biệt được, còn xương thì bão hòa.
**F:** Có thử cửa sổ khác không? → Ablation ABL-B (thêm kênh cửa sổ trung thất) *[nếu đã làm]*.

**C3. Q:** Slice thickness và slice spacing khác nhau thế nào?
**A:** Thickness là bề dày vật lý mà lát đại diện, spacing là khoảng cách giữa tâm hai lát. Tôi tính spacing từ ImagePositionPatient vì có trường hợp tái tạo chồng lấp.

**C4. Q:** Nốt kính mờ khác nốt đặc thế nào, model xử lý ra sao?
**A:** Nốt kính mờ có HU chỉ cao hơn nhu mô một chút nên tương phản thấp. Kết quả phân tầng theo texture *[R6]* cho thấy …
**F:** Cải thiện bằng cách nào? → Đa cửa sổ HU, loss ưu tiên recall, nhiều mẫu kính mờ hơn.

## D. U-Net & kiến trúc

**D1. Q:** Skip connection có tác dụng gì?
**A:** Pooling làm mất chi tiết vị trí. Skip connection đưa đặc trưng độ phân giải cao từ encoder sang decoder để vẽ biên chính xác, điều đặc biệt quan trọng với nốt chỉ vài pixel.

**D2. Q:** Attention gate hoạt động như thế nào?
**A:** Nó dùng đặc trưng ngữ cảnh từ decoder để tính hệ số 0–1 cho từng pixel của skip connection, giữ vùng liên quan và làm yếu vùng nền như mạch máu hay thành ngực.
**T:** $\alpha = \sigma(\psi^T \text{ReLU}(W_x x + W_g g))$, $\hat{x} = \alpha \odot x$.
**F:** Attention map có giải thích được model không? → Chỉ cho biết vùng được tăng trọng số, không phải giải thích nhân quả.

**D3. Q:** Attention U-Net hơn U-Net vì có nhiều tham số hơn?
**A:** Không. Số tham số chỉ tăng khoảng 1% *[số thật từ PHASE 18]*. Mọi điều kiện khác giống nhau và được kiểm tra tự động.

**D4. Q:** Sao dùng 2D mà không dùng 3D?
**A:** Ba lý do: GPU 4 GB, độ dày lát không đồng nhất, và để so sánh sạch trong thời gian khóa luận. Đổi lại, model không thấy mạch máu là cấu trúc ống kéo dài, và điều này hiện rõ trong failure analysis.
**F:** Có giải pháp trung gian không? → 2.5D: đưa các lát kề vào làm kênh; đây là hướng phát triển.

**D5. Q:** Sao không dùng Transformer hay nnU-Net?
**A:** Câu hỏi nghiên cứu là đóng góp của một thay đổi cụ thể (attention gate). Thêm nhiều kiến trúc sẽ làm loãng câu hỏi, và tài nguyên không đủ để chạy công bằng với nhiều seed.

## E. Loss

**E1. Q:** Vì sao kết hợp BCE và Dice?
**A:** BCE cho gradient ổn định theo từng pixel nhưng bị nền chi phối. Dice tối ưu trực tiếp mức chồng lấn và không nhạy với tỉ lệ nền. Kết hợp giữ ưu điểm của cả hai; ablation đo đóng góp thực tế *[R4]*.

**E2. Q:** Sao không dùng Focal hay Tversky?
**A:** Chúng thêm siêu tham số và nhân số experiment, mà không trả lời câu hỏi nghiên cứu chính. Tôi chỉ xem xét Tversky nếu failure analysis cho thấy under-segmentation có hệ thống.

**E3. Q:** Dice loss xử lý patch âm (mask rỗng) thế nào?
**A:** Với hằng số làm trơn ε = 1, dự đoán rỗng trên mask rỗng cho loss ≈ 0, tức không phạt; còn dự đoán ra vùng thì bị phạt. Có test đơn vị cho trường hợp này.

## F. Training

**F1. Q:** Hyperparameter được chọn thế nào? Có tinh chỉnh không?
**A:** Dùng giá trị chuẩn (AdamW 3e-4, cosine) và **giống nhau** cho mọi experiment, để so sánh công bằng. Không tinh chỉnh riêng cho từng model và không dùng tập test.

**F2. Q:** Làm sao biết model không overfit?
**A:** Early stopping theo val Dice, theo dõi curve train/val, và đánh giá trên tập test bệnh nhân hoàn toàn riêng biệt.

**F3. Q:** Huấn luyện trên GPU 4 GB như thế nào?
**A:** Patch 128 × 128, base 32 kênh, mixed precision, batch 16. VRAM đỉnh thực tế: *[số liệu]*.

## G. Metrics

**G1. Q:** Vì sao không dùng accuracy?
**A:** Pixel nền chiếm hơn 99%, nên một model dự đoán toàn nền vẫn có accuracy trên 99%. Accuracy không phản ánh khả năng phân đoạn nốt.

**G2. Q:** Dice và IoU khác nhau thế nào? Báo cáo cả hai có thừa không?
**A:** Trên từng mẫu, IoU = Dice/(2 − Dice), nên chúng không độc lập. Tôi báo cáo cả hai vì thông lệ và để so được với các nghiên cứu khác, nhưng thông tin bổ sung thật sự đến từ Precision/Recall (loại lỗi) và HD95 (sai số biên).

**G3. Q:** HD95 là gì, sao không dùng HD (max)?
**A:** HD95 là phân vị 95 của khoảng cách giữa hai biên, đo bằng mm. Dùng phân vị 95 thay cho max để không bị một pixel ngoại lệ chi phối.
**F:** HD95 khi model dự đoán rỗng? → Không xác định; báo cáo riêng số ca và đưa vào nhóm "missed".

**G4. Q:** Tính metric theo lát hay theo nốt?
**A:** Theo nốt là chính (ghép các lát thành 3D cục bộ), để mỗi nốt có trọng số như nhau. Theo lát thì nốt lớn, nhiều lát sẽ chi phối kết quả.

**G5. Q:** Dice của bạn thấp hơn paper X đạt 0.88, giải thích thế nào?
**A:** Con số không so sánh trực tiếp được: khác định nghĩa ground truth, khác tập nốt, khác đơn vị tính và cách chia dữ liệu. So sánh có giá trị là giữa các model trong cùng pipeline, và với mức đồng thuận giữa các bác sĩ trên cùng dữ liệu.
**F:** Vậy đánh giá chất lượng tuyệt đối bằng gì? → Bằng mốc tham chiếu con người *[R2]*.

## H. Experimental design

**H1. Q:** Thiết kế ablation thế nào, vì sao là 2 × 2?
**A:** Thiết kế giai thừa 2 × 2 (kiến trúc × loss) cho biết hiệu ứng chính của từng thành phần **và** tương tác giữa chúng, với chỉ 4 cấu hình. Ablation dạng chuỗi thì phụ thuộc thứ tự thêm thành phần.

**H2. Q:** Vì sao cần 3 seed? Kết quả khác nhau bao nhiêu giữa các seed?
**A:** Để phân biệt cải thiện thật với dao động ngẫu nhiên. Std giữa các seed: *[R3]*. Tôi chỉ kết luận khi chênh lệch lớn hơn std và có ý nghĩa thống kê.

**H3. Q:** Dùng kiểm định thống kê nào? Vì sao?
**A:** Wilcoxon signed-rank theo cặp trên Dice từng nốt (cùng nốt, hai model). Kiểm định này không giả định phân phối chuẩn, vì phân phối Dice thường lệch. Hiệu chỉnh Holm cho nhiều so sánh, kèm CI bootstrap theo bệnh nhân.

## I. Data leakage

**I1. Q:** Làm sao đảm bảo không có data leakage?
**A:** Chia theo **bệnh nhân**: mọi lát và mọi scan của một người nằm trong đúng một tập. Có kiểm tra tự động ở 3 nơi; ngưỡng τ và checkpoint chọn trên val; test chỉ chạy một lần.
**F:** Bệnh nhân có 2 scan thì sao? → Chia theo patient_id nên cả 2 scan cùng tập.

**I2. Q:** Chia ngẫu nhiên theo slice thì sai ở đâu?
**A:** Các lát kề nhau gần như giống hệt. Lát *i* ở train và lát *i+1* ở test thì model chỉ cần nhớ, nên kết quả bị thổi phồng và không phản ánh khả năng trên bệnh nhân mới.

**I3. Q:** Còn dạng leakage nào khác không?
**A:** Chọn hyperparameter, ngưỡng hay checkpoint theo test; chuẩn hóa bằng thống kê tính trên toàn dataset; xem ảnh test khi thiết kế phương pháp. Tôi tránh tất cả: chuẩn hóa theo cửa sổ cố định, mọi lựa chọn đều dựa trên val.

## J. Generalization

**J1. Q:** Model dùng được ở bệnh viện Việt Nam không?
**A:** Chưa thể khẳng định. LIDC thu thập tại Mỹ, trước 2011, với máy và quy trình khác, nên có domain shift. Cần external validation trên dữ liệu địa phương trước.

**J2. Q:** Model chạy trên toàn scan (không có patch quanh nốt) thì sao?
**A:** Đó là phần đánh giá phát hiện thứ cấp: per-nodule sensitivity *[R7]* với FP/scan *[R7]*. FP chủ yếu ở mạch máu và màng phổi, vì model 2D thiếu ngữ cảnh 3D.

**J3. Q:** Model có hoạt động trên CT liều thấp không?
**A:** Không được đánh giá riêng. LIDC gồm scan từ nhiều quy trình khác nhau, nhưng tôi không phân tầng theo liều (thông tin liều trong header không nhất quán [ASSUMPTION, kiểm tra ở PHASE 02]). Đây là giới hạn.

## K. Limitations

**K1. Q:** Hạn chế lớn nhất của khóa luận là gì?
**A:** (1) Ground truth là đồng thuận của bác sĩ, không có giải phẫu bệnh; (2) model 2D; (3) chưa có external validation.

**K2. Q:** Dice trên patch có quá lạc quan không?
**A:** Có, vì vị trí nốt đại khái đã được cho trước. Vì vậy tôi báo cáo thêm đánh giá trên toàn lát và nói rõ đây là "phân đoạn khi đã biết vùng quan tâm".

## L. Ethics

**L1. Q:** Có vấn đề đạo đức nào với dữ liệu không?
**A:** Dữ liệu đã khử định danh, giấy phép CC BY 3.0, tôi trích dẫn đầy đủ và không phân phối lại ảnh. Kết quả không được dùng cho chẩn đoán.

**L2. Q:** Nếu bác sĩ dựa vào model mà bỏ sót nốt thì sao?
**A:** Đó là lý do hệ thống được trình bày là nguyên mẫu nghiên cứu, có cảnh báo rõ ràng. Một công cụ lâm sàng cần reader study, calibration, external validation và đạt quy định về thiết bị y tế.

## M. Future work

**M1. Q:** Nếu có thêm 6 tháng, bạn làm gì đầu tiên?
**A:** Chuyển sang 2.5D hoặc 3D để giảm FP ở mạch máu (nguồn lỗi chính theo failure analysis), rồi external validation.

**M2. Q:** Có thể khai thác sự bất đồng giữa các bác sĩ không?
**A:** Có. Có thể mô hình hóa phân bố các phân đoạn hợp lý thay vì một mask duy nhất, ví dụ Probabilistic U-Net (Kohl et al., 2018), vốn được phát triển và đánh giá trên chính LIDC.

**M3. Q:** Từ phân đoạn có thể tiến tới đánh giá nguy cơ không?
**A:** Mask cho phép đo kích thước và thể tích, là đầu vào cho theo dõi tăng trưởng theo hướng dẫn Fleischner. Đánh giá nguy cơ ác tính cần dữ liệu có nhãn giải phẫu bệnh và là một bài toán khác.

---

## Chuẩn bị
- In sẵn: bảng R1–R4, 1 trang hình failure cases, bảng phân biệt 4 khái niệm.
- Tập trả lời câu G5, I1 và K2 cho trôi chảy. Đây là những câu thường gặp nhất và dễ bị hỏi vặn nhất.
