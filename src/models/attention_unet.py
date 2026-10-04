"""MODEL 02 — Attention U-Net (Oktay et al., MIDL 2018).

Responsibility
--------------
U-Net with additive attention gates on the skip connections, letting the
decoder suppress irrelevant regions (vessels, chest wall) around small nodules.

Planned public API
------------------
class AttentionGate(nn.Module): forward(skip, gating) -> gated skip
class AttentionUNet(nn.Module): same constructor/forward contract as UNet

Status: NOT IMPLEMENTED — scheduled for PHASE 18.
"""

# TODO(PHASE 18):
#   1. Reuse UNet building blocks so the ONLY difference is the attention gates.
#   2. Gate: W_x(skip) + W_g(gating) -> ReLU -> psi(1x1 conv) -> sigmoid -> alpha;
#      return skip * alpha. Optionally return alpha maps for visualisation.
#   3. Report parameter count vs. UNet in the thesis (fairness of comparison).
