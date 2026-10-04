# 02 — Literature Review

## 0. Trạng thái xác minh

Thông tin thư mục (tác giả, venue, DOI) và **kết quả định lượng** trong tài liệu này đã được đối chiếu với nguồn gốc vào ngày **2026-10-04**: bản ghi PubMed, trang abstract arXiv, metadata Crossref/DataCite, trang collection của TCIA (bản lưu trữ ngày 2026-02-11). Cột "Xác minh" cho biết mức độ:

- ✅ **Đã xác minh**: đọc trực tiếp abstract/toàn văn trên nguồn gốc; trích đúng nguyên văn.
- ⚠️ **Một phần**: metadata đã xác minh, nhưng kết quả định lượng **chưa** xác minh được từ nguồn gốc.
- **[VERIFY REQUIRED]**: chưa xác minh. **Không đưa vào khóa luận.**

> Trước khi nộp khóa luận, sinh viên phải **tự mở** từng DOI và đối chiếu lại số liệu sẽ trích. Không được trích lại số liệu từ tài liệu này mà không kiểm tra.

## 1. Nền tảng kiến trúc

| Paper | Year | Dataset | Model | Task | Input | Metrics | Main result | Limitation | Xác minh |
|-------|------|---------|-------|------|-------|---------|-------------|------------|----------|
| Ronneberger, Fischer, Brox — *U-Net: Convolutional Networks for Biomedical Image Segmentation*, MICCAI. doi:10.1007/978-3-319-24574-4_28 | 2015 | ISBI cell tracking / EM segmentation | U-Net 2D | Phân đoạn ảnh y sinh | Ảnh 2D | IoU, warping error | Kiến trúc encoder–decoder + skip connection huấn luyện được với ít ảnh nhờ augmentation mạnh | Không phải dữ liệu CT/phổi; 2D | ✅ (DOI) |
| Çiçek, Abdulkadir, Lienkamp, Brox, et al. — *3D U-Net: Learning Dense Volumetric Segmentation from Sparse Annotation*, MICCAI, pp. 424–432. doi:10.1007/978-3-319-46723-8_49 | 2016 | Xenopus kidney (confocal) | 3D U-Net | Phân đoạn 3D | Volume 3D | IoU | Mở rộng U-Net sang 3D, học được từ annotation thưa | Tốn bộ nhớ; không phải phổi | ✅ (metadata) |
| Milletari, Navab, Ahmadi — *V-Net*, 3DV, pp. 565–571. doi:10.1109/3DV.2016.79 | 2016 | MRI tuyến tiền liệt (PROMISE12) | V-Net 3D | Phân đoạn 3D | Volume | Dice, HD | Đề xuất **Dice loss** để xử lý mất cân bằng lớp | Không phải phổi | ✅ (metadata) |
| Oktay, Schlemper, Le Folgoc, et al. — *Attention U-Net: Learning Where to Look for the Pancreas*, MIDL. arXiv:1804.03999 | 2018 | CT bụng (tụy) | Attention U-Net | Phân đoạn | CT 3D | Dice, precision, recall | Attention gate trên skip connection cải thiện phân đoạn tụy so với U-Net | Không phải phổi; cơ quan khác về hình thái | ✅ (arXiv) |
| Schlemper, Oktay, Schaap, et al. — *Attention gated networks: Learning to leverage salient regions in medical images*, Med Image Anal 53:197–207. doi:10.1016/j.media.2019.01.012 | 2019 | Siêu âm thai (phân loại), **2 bộ CT bụng 3D** (phân đoạn) | AG-Sononet, Attention U-Net | Phân loại + phân đoạn | 2D/3D | Dice, … | Attention gate tổng quát cho nhiều tác vụ | **Không** có dữ liệu phổi | ✅ |
| Isensee, Jaeger, Kohl, et al. — *nnU-Net*, Nature Methods 18:203–211. doi:10.1038/s41592-020-01008-z | 2021 | Nhiều bộ dữ liệu y khoa | U-Net tự cấu hình | Phân đoạn | 2D/3D | Dice | U-Net cấu hình đúng cách là baseline rất mạnh | Tốn tài nguyên; ít phù hợp GPU 4 GB | ✅ (DOI) |

## 2. Dataset & benchmark

| Paper | Year | Dataset | Task | Nội dung chính | Xác minh |
|-------|------|---------|------|----------------|----------|
| McNitt-Gray, Armato, Meyer, et al. — Acad Radiol 14(12):1464–74. doi:10.1016/j.acra.2007.07.021 | 2007 | LIDC | Quy trình thu thập | Quy trình đọc 2 pha (blinded → unblinded) bởi 4 bác sĩ; "More than 500 CT scans have been read" (tại thời điểm công bố) | ✅ |
| Armato, McLennan, Bidaut, et al. — Med Phys 38(2):915–31. doi:10.1118/1.3528204 | 2011 | LIDC-IDRI | Mô tả dataset | "contains 1018 cases"; "Seven academic centers and eight medical imaging companies"; "7371 lesions marked 'nodule' by at least one radiologist. 2669 of these lesions were marked 'nodule ≥3 mm' by at least one radiologist, of which 928 (34.7%) received such marks from all four radiologists" | ✅ |
| TCIA collection page — doi:10.7937/K9/TCIA.2015.LO9QL9SX | 2015– | LIDC-IDRI | Phân phối | 1,010 subjects; 244,527 images; 133.16 GB; modalities DX, CT, CR; CC BY 3.0; Version 4 (2020-09-21) | ✅ (bản lưu trữ 2026-02-11) |
| Setio, Traverso, de Bel, et al. — *The LUNA16 challenge*, Med Image Anal 42:1–13. doi:10.1016/j.media.2017.06.015 | 2017 | LUNA16 (888 scan, tập con LIDC) | **Phát hiện** | Loại scan có slice thickness > 3 mm hoặc spacing không nhất quán → 888 scan; chuẩn tham chiếu: **1186 nốt ≥ 3 mm được ≥ 3/4 bác sĩ đánh dấu**; metric CPM = trung bình sensitivity tại 1/8, 1/4, 1/2, 1, 2, 4, 8 FP/scan; hệ thống kết hợp đạt "sensitivity of over 95% at fewer than 1.0 false positives per scan" | ✅ |

## 3. Phân đoạn nốt phổi (liên quan trực tiếp)

| Paper | Year | Dataset | Model | Task | Input | Metrics | Main result (trích abstract) | Limitation | Xác minh |
|-------|------|---------|-------|------|-------|---------|------------------------------|------------|----------|
| Wang S, Zhou M, Liu Z, et al. — *Central focused CNN (CF-CNN)*, Med Image Anal 40:172–183. doi:10.1016/j.media.2017.06.014 | 2017 | LIDC (893 nốt) + bộ độc lập GDGH (74 nốt) | CF-CNN (2 nhánh 3D + 2D) | Phân đoạn | Patch quanh nốt | Dice | "average dice scores of 82.15% and 80.02% for the two datasets"; chênh lệch so với độ nhất quán giữa các bác sĩ chỉ 1.98% | Giả định đã biết vị trí nốt (patch quanh nốt) | ✅ |
| Tong G, Li Y, Chen H, et al. — *Improved U-NET network for pulmonary nodules segmentation*, Optik 174:460–469. doi:10.1016/j.ijleo.2018.08.086 | 2018 | **Không nêu trong abstract** | U-Net cải tiến | Phân đoạn | — | — | Abstract **không có số liệu định lượng** | Không tái lập được từ abstract | ⚠️ — **không trích số liệu** |
| Kohl, Romera-Paredes, Meyer, et al. — *A Probabilistic U-Net for Segmentation of Ambiguous Images*, NeurIPS. arXiv:1806.05034 | 2018 | LIDC-IDRI, 4 annotation/ảnh; chia 722/144/144 **bệnh nhân** | Probabilistic U-Net | Phân đoạn **đa giả thuyết** (mô hình hóa bất đồng) | Crop 2D 180×180 ở 0.5 mm, huấn luyện trên crop 128×128 | Generalized energy distance | Mô hình hóa được phân bố các phân đoạn hợp lý thay vì một mask duy nhất | Không trực tiếp so sánh được bằng Dice | ✅ |
| Aresta G, Jacobs C, Araújo T, et al. — *iW-Net*, Sci Rep 9:11591. doi:10.1038/s41598-019-48004-8 | 2019 | LIDC-IDRI | iW-Net (tự động + tương tác) | Phân đoạn | Patch | IoU | "0.55 intersection over union vs the 0.59 inter-observer agreement" | Đánh giá IoU so với đồng thuận giữa các bác sĩ | ✅ |
| Keetha NV, Babu P SA, Annavarapu CSR — *U-Det*, arXiv:2003.09293 | 2020 | **LUNA16** (1186 nốt) | U-Net + Bi-FPN | Phân đoạn | Patch | DSC | "DSC of 82.82%" | Chỉ là preprint; dùng LUNA16, không dùng LIDC đầy đủ | ✅ (preprint) |
| Usman M, Lee BD, Byon SS, et al. — *Volumetric lung nodule segmentation using adaptive ROI with multi-view residual learning*, Sci Rep 10:12839. doi:10.1038/s41598-020-69817-y | 2020 | LIDC-IDRI | Deep Residual U-Net, đa góc nhìn | Phân đoạn 3D | ROI thích nghi | Dice | "average dice score of 87.5%" | Pipeline phức tạp; ROI dựa vào vị trí nốt | ✅ |
| Wu Z, Li X, Zuo J — *RAD-UNet*, Front Oncol 13:1084096. doi:10.3389/fonc.2023.1084096 | 2023 | LIDC + bộ dữ liệu bệnh viện | U-Net + ResNet encoder + ASPP + attention kênh/không gian | Phân đoạn | 2D | mIoU, F1 | "mIoU reached 87.76% and 88.13%" | Ít được trích dẫn; định nghĩa mIoU (có tính cả lớp nền?) cần đọc kỹ | ✅ (abstract) |

## 4. Loss & đánh giá

| Paper | Nội dung liên quan | Xác minh |
|-------|-------------------|----------|
| Milletari et al. 2016 (V-Net) | Soft Dice loss | ✅ |
| Lin T-Y et al. 2017 — *Focal Loss for Dense Object Detection*, ICCV. arXiv:1708.02002 | Focal loss cho mất cân bằng lớp | ✅ (arXiv ID) |
| Salehi S.S.M. et al. 2017 — *Tversky loss function for image segmentation using 3D FCDN*, MLMI. arXiv:1706.05721 | Tversky loss, cân chỉnh FP/FN | ✅ (arXiv ID) |
| Warfield, Zou, Wells — *STAPLE*, IEEE TMI 23(7):903–21. doi:10.1109/TMI.2004.828354 | Ước lượng ground truth từ nhiều người vẽ | ✅ |
| Taha & Hanbury 2015 — *Metrics for evaluating 3D medical image segmentation*, BMC Med Imaging 15:29. doi:10.1186/s12880-015-0068-x | Phân tích và lựa chọn metric phân đoạn | [VERIFY REQUIRED] |
| Maier-Hein, Reinke, Godau, et al. — *Metrics Reloaded*, Nat Methods 21(2):195–212. doi:10.1038/s41592-023-02151-z | Khuyến nghị chọn metric theo đặc tính bài toán (vật thể nhỏ, biên, v.v.) | ✅ |

## 5. Bối cảnh lâm sàng

| Paper | Nội dung | Xác minh |
|-------|----------|----------|
| Bray F, Laversanne M, Sung H, et al. — *GLOBOCAN 2022*, CA Cancer J Clin 74(3):229–263. doi:10.3322/caac.21834 | Ung thư phổi là ung thư được chẩn đoán nhiều nhất năm 2022 ("almost 2.5 million new cases … 12.4%") và là nguyên nhân tử vong do ung thư hàng đầu ("1.8 million deaths (18.7%)") | ✅ |
| National Lung Screening Trial Research Team — NEJM 365:395–409. doi:10.1056/NEJMoa1102873 | Tầm soát bằng CT liều thấp giảm tử vong do ung thư phổi | [VERIFY REQUIRED] số liệu cụ thể trước khi trích |
| MacMahon H. et al. — Fleischner 2017, Radiology 284(1):228–243. doi:10.1148/radiol.2017161659 | Hướng xử trí nốt phổi theo kích thước và loại | [VERIFY REQUIRED] chi tiết |
| Hansell D.M. et al. — Fleischner Glossary, Radiology 246(3):697–722. doi:10.1148/radiol.2462070712 | Định nghĩa thuật ngữ (nodule ≤ 3 cm, mass > 3 cm) | [VERIFY REQUIRED] trích nguyên văn |

## 6. Tổng hợp và khoảng trống nghiên cứu

### 6.1 Những gì đã biết [FACT, từ các nguồn trên]
1. U-Net và biến thể là họ phương pháp chủ đạo cho phân đoạn nốt phổi.
2. Các phương pháp tốt trên LIDC báo cáo Dice khoảng 0.8–0.88 **trên patch quanh nốt**, với định nghĩa ground truth và tập nốt khác nhau.
3. **Bất đồng giữa các bác sĩ là đáng kể**: iW-Net báo cáo IoU giữa các bác sĩ là 0.59, và CF-CNN so sánh trực tiếp với độ nhất quán giữa các bác sĩ. Đây là mốc tham chiếu quan trọng.
4. LUNA16 dùng tiêu chuẩn ≥ 3/4 bác sĩ cho bài toán **phát hiện**.

### 6.2 Vì sao KHÔNG so sánh trực tiếp con số với các paper khác

| Yếu tố khác nhau | Ví dụ | Hệ quả |
|------------------|-------|--------|
| Định nghĩa GT | ≥ 2/4, ≥ 3/4, union, chọn 1 bác sĩ, 50% của người vẽ | Mask khác nhau → Dice khác nhau |
| Tập nốt | 893 nốt (CF-CNN), 1186 nốt (LUNA16), lọc theo kích thước | Nốt lớn hơn → Dice cao hơn |
| Đơn vị tính | Theo lát, theo nốt, theo patch; có tính patch âm hay không | Dice theo lát và theo nốt không tương đương |
| Chia dữ liệu | Theo bệnh nhân hay theo nốt/ảnh; có tập test cố định không | Chia theo ảnh làm Dice tăng do leakage |
| Metric | mIoU có thể tính trung bình cả lớp nền (luôn cao) | Không cùng thang đo |

**[DECISION]** Trong khóa luận: trình bày các con số của paper khác như **bối cảnh**, kèm bảng các khác biệt ở trên. **Không** kết luận "tốt hơn hay kém hơn paper X". So sánh có giá trị khoa học duy nhất là giữa các model **trong cùng pipeline** (U-Net vs Attention U-Net) và với **mức đồng thuận giữa các bác sĩ** trên cùng dữ liệu.

### 6.3 Khoảng trống mà khóa luận này nhắm tới

Đây là các khoảng trống phù hợp với quy mô khóa luận, **không** phải tuyên bố vượt SOTA:
1. **Tái lập minh bạch:** nhiều nghiên cứu không công bố đầy đủ cách gom annotation, cách chia tập và mã nguồn. Khóa luận cung cấp pipeline mở, có kiểm tra leakage tự động.
2. **So sánh có kiểm soát:** đánh giá đóng góp riêng của attention gate và Dice loss bằng ablation 2 × 2, nhiều seed, kiểm định thống kê.
3. **Phân tích theo nhóm nốt:** hiệu năng theo kích thước, đậm độ và vị trí, đặt cạnh mức đồng thuận giữa các bác sĩ.

## 7. Hướng dẫn tự xác minh một trích dẫn

1. Mở `https://doi.org/<DOI>` và kiểm tra tiêu đề, tác giả, năm, venue.
2. Đọc abstract (PubMed: `https://pubmed.ncbi.nlm.nih.gov/?term=<DOI>`).
3. Chỉ trích **số liệu có trong abstract hoặc toàn văn**, ghi rõ trang/bảng.
4. Không trích số liệu thấy trên blog, slide hay "bài tổng hợp" mà không có nguồn gốc.
5. Với preprint arXiv: ghi rõ là preprint.
6. Tránh các tạp chí có lịch sử rút bài hàng loạt.
