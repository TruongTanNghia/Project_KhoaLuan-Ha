"""MODEL 01 — U-Net baseline (Ronneberger et al., MICCAI 2015).

Responsibility
--------------
2D encoder-decoder with skip connections for binary segmentation.

Planned public API
------------------
class UNet(nn.Module): __init__(in_channels, out_channels, base_channels, depth,
    norm, dropout); forward(x) -> logits [B, out_channels, H, W]

Status: NOT IMPLEMENTED — scheduled for PHASE 14.
"""

# TODO(PHASE 14):
#   1. Blocks: (Conv3x3 -> Norm -> ReLU) x 2; MaxPool down; ConvTranspose/upsample up.
#   2. Use padding=1 so output size == input size (image_size must be divisible by
#      2**depth; validate in __init__/forward and raise a clear error).
#   3. Return LOGITS (no sigmoid) — sigmoid is applied in loss/metrics/inference.
#   4. Expose shared building blocks so attention_unet.py reuses them (fair comparison).
#   5. Test: forward shape, parameter count logged, a single batch can be overfitted.
