# Experiments

Mỗi thư mục con là **một experiment**, gồm:

| File / thư mục            | Nguồn gốc                               |
|---------------------------|-----------------------------------------|
| `config.yaml`             | Viết tay — chỉ chứa khác biệt so với `configs/` |
| `resolved_config.yaml`    | Sinh tự động khi train (config cuối cùng đã merge) |
| `run_info.json`           | Sinh tự động: seed, git commit, thời gian, môi trường |
| `history.csv`             | Sinh tự động: loss/metric theo epoch    |
| `summary.json`            | Sinh tự động: best_epoch, best_val_dice, test_* |
| `tensorboard/`            | Sinh tự động                            |

**Không ghi kết quả thủ công.** Bảng tổng hợp
`results/metrics/experiments_summary.csv` được tạo bởi script, đọc từ các
`summary.json`.

## Thiết kế ablation 2 × 2

|                     | BCE      | BCE + Dice |
|---------------------|----------|------------|
| **U-Net**           | exp01    | exp02      |
| **Attention U-Net** | exp03    | exp04      |

- exp01 ↔ exp02 và exp03 ↔ exp04: tác động của **loss**.
- exp01 ↔ exp03 và exp02 ↔ exp04: tác động của **attention gate**.
- Mọi experiment dùng **cùng** `dataset_version`, cùng split, cùng seed.
- Khuyến nghị chạy mỗi experiment với ≥ 3 seed để báo cáo mean ± std.
