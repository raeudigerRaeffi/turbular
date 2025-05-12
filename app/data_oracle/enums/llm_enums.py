from .base_enum import BaseEnum


class Prompt_Type(BaseEnum):
    DYNAMIC = "CosineSim"  # see https://arxiv.org/abs/2308.15363
    FEW_SHOT = "FewShot"
    ZERO_SHOT = "ZeroShot"
    CUSTOM = "Custom"
