"""PyTorch Dataset for preprocessed lung-nodule samples.

Responsibility
--------------
Serve (image, mask, metadata) tensors for one split, with optional
augmentation applied identically to image and mask.

Planned public API
------------------
class LungNoduleDataset(torch.utils.data.Dataset):
    __init__(self, split: str, cfg: dict, transform=None)
    __getitem__(i) -> {'image': [1,H,W] float32, 'mask': [1,H,W] float32, 'meta': dict}
build_dataloaders(cfg) -> dict[str, DataLoader]
build_transforms(cfg, train: bool)  # PHASE 13

Status: NOT IMPLEMENTED — scheduled for PHASE 12-13.
"""

# TODO(PHASE 12-13):
#   1. Filter samples.csv by patient_id in data/splits/<split>.csv (never by sample).
#   2. Re-assert patient disjointness at construction time.
#   3. PHASE 13: geometric augmentations must transform mask with nearest-neighbour
#      interpolation; intensity augmentations apply to the image only.
#   4. Use seed_worker + make_generator from src.utils.seed for reproducible loading.
