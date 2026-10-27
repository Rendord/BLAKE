from dataclasses import dataclass


@dataclass(frozen=True)
class RenderJob:
    index: int
    resolution: tuple[int, int]
    device_pixel_ratio: float
    priority: int
#   history_hash: int

@dataclass(frozen=True)
class Settings:
    index: int