"""Build a model from cfg['model'].

Responsibility
--------------
Single entry point mapping cfg['model']['name'] -> model instance, so
scripts never import a concrete architecture directly.

Planned public API
------------------
build_model(model_cfg: dict) -> nn.Module
MODEL_REGISTRY: dict[str, type[nn.Module]]

Status: NOT IMPLEMENTED — scheduled for PHASE 14.
"""

# TODO(PHASE 14):
#   1. Register 'unet' in PHASE 14 and 'attention_unet' in PHASE 18.
#   2. Unknown name -> ValueError listing available models.
