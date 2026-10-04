# 14 — Reproducibility Protocol

Mục tiêu: một người khác, chỉ có repository, dữ liệu LIDC-IDRI từ TCIA và tài liệu này, chạy lại được mọi experiment và thu được kết quả **trong phạm vi biến thiên giữa các seed** đã báo cáo.

## 1. Môi trường phát triển (đo ngày 2026-10-04)

| Thành phần | Giá trị | Ghi chú |
|------------|---------|---------|
| OS | Windows 11 Home (10.0.26200) | |
| Python | 3.11.9 | |
| PyTorch | 2.5.1+cu124 | Bản đang có trong môi trường hệ thống; **chốt trong venv ở PHASE 01** |
| CUDA runtime (PyTorch) | 12.4 | |
| cuDNN | 9.1.0 (`90100`) | |
| GPU | NVIDIA GeForce RTX 3050 Laptop, 4 GB VRAM | |
| NVIDIA driver | 610.62 | |
| Các package khác | **Chốt ở PHASE 01** trong `requirements.txt` với version cố định (`==`) | Sau PHASE 01 thêm `requirements-lock.txt` (`pip freeze`) |

**[DECISION]** Mỗi lần chạy, `run_info.json` tự ghi lại thông tin môi trường **thực tế lúc chạy** (không dựa vào bảng này): phiên bản Python/PyTorch/CUDA/cuDNN, tên GPU, driver, `pip freeze` hash, git commit, git dirty flag.

## 2. Các thành phần cần cố định

| Thành phần | Cơ chế | Nơi lưu |
|------------|--------|---------|
| **Code** | Git commit hash; cảnh báo nếu working tree có thay đổi chưa commit (dirty) | `run_info.json` |
| **Dataset gốc** | TCIA LIDC-IDRI Version 4 (2020-09-21), DOI 10.7937/K9/TCIA.2015.LO9QL9SX | Tài liệu này + `validation_report.json` |
| **Dataset đã xử lý** | `project.dataset_version` + hash của config tiền xử lý + thống kê | `data/processed/metadata/manifest.json` |
| **Split** | 3 file CSV danh sách bệnh nhân + seed + hash; **commit vào git** | `data/splits/` |
| **Config** | Config đã resolve (sau kế thừa và override) | `experiments/<exp>/<run_id>/resolved_config.yaml` |
| **Seed** | `project.seed`, áp cho Python, NumPy, PyTorch, CUDA, worker DataLoader | `src/utils/seed.py` |
| **Checkpoint** | `best.pt`, `last.pt` chứa trọng số, optimizer, scheduler, scaler, epoch, config, dataset_version | `checkpoints/<run_id>/` |
| **Kết quả** | CSV/JSON sinh tự động | `results/metrics/`, `experiments/<exp>/<run_id>/summary.json` |

## 3. Quy ước Experiment ID

```
run_id = <experiment_name>__s<seed>__<YYYYMMDD-HHMMSS>__<git_short_hash>
ví dụ: exp04_attention_unet_dice__s42__20261120-091530__a1b2c3d
```

Một experiment (ví dụ `exp04_attention_unet_dice`) có nhiều run (mỗi seed một run). Bảng tổng hợp gom theo `experiment_name`.

## 4. Các trường bắt buộc trong `summary.json`

`experiment_name, run_id, model, dataset_version, image_size, batch_size, learning_rate, optimizer, loss, epochs (max), epochs_trained, seed, best_epoch, best_val_dice, test_dice, test_iou, test_precision, test_recall, test_hd95, n_test_nodules, n_nan_hd95, train_time_min, peak_vram_mb, git_commit`

Các trường `test_*` chỉ được ghi bởi `scripts/08_evaluate.py`, không bao giờ ghi tay.

## 5. Quy trình tái lập (từ đầu)

```bash
git clone <repo> && cd lung_nodule_unet
python -m venv .venv && .venv\Scripts\activate         # Windows
pip install -r requirements.txt
python scripts/00_check_project.py                     # PHASE 00 gate
$env:LIDC_IDRI_DIR = "D:\datasets\LIDC-IDRI"           # dữ liệu tải từ TCIA
python scripts/01_validate_raw_data.py   --config configs/base.yaml
python scripts/02_parse_annotations.py   --config configs/base.yaml
python scripts/03_generate_masks.py      --config configs/base.yaml
python scripts/04_preprocess_dataset.py  --config configs/base.yaml
python scripts/05_create_splits.py       --config configs/base.yaml   # hoặc dùng split đã commit
for seed in 42 1 2:
  python scripts/06_train_unet.py --config experiments/exp01_unet_baseline/config.yaml --set project.seed=$seed
  ... (exp02–exp04)
python scripts/08_evaluate.py --all
```

**[DECISION]** Để tái lập **đúng split**, dùng các file `data/splits/*.csv` đã commit thay vì tạo lại. `05_create_splits.py` phải từ chối ghi đè split đã tồn tại, trừ khi có cờ `--force`, và khi đó tăng `dataset_version`.

## 6. Giới hạn của tính tái lập

- **[LIMITATION]** Bật `deterministic=True` vẫn không đảm bảo kết quả **giống từng bit** giữa các GPU, driver hoặc phiên bản cuDNN khác nhau. Một số kernel CUDA không có phiên bản tất định (PyTorch chỉ cảnh báo, `warn_only=True`).
- **[LIMITATION]** AMP (float16) gây sai khác nhỏ giữa các phần cứng.
- **Hệ quả:** kết luận dựa trên **mean ± std qua nhiều seed**, không dựa trên một con số chính xác đến chữ số thập phân thứ 4.
- **Kiểm tra tái lập:** chạy lại EXP-01 seed 42 hai lần trên cùng máy. Chênh lệch `best_val_dice` phải rất nhỏ so với std giữa các seed. Ghi kết quả kiểm tra vào khóa luận.

## 7. Checklist trước khi công bố kết quả

- [ ] Mọi run có `resolved_config.yaml`, `run_info.json`, `history.csv`, `summary.json`
- [ ] Git working tree sạch lúc chạy các run cuối cùng (`git_dirty = false`)
- [ ] `requirements-lock.txt` được commit
- [ ] Split CSV và `split_manifest.json` được commit
- [ ] Bảng kết quả trong khóa luận khớp với `experiments_summary.csv`
- [ ] Checkpoint của các run được báo cáo được lưu trữ (ngoài git, ví dụ ổ đĩa hoặc release asset)
