from typing import Tuple
from dataclasses import dataclass

@dataclass(frozen=True)
class RenderJob():
    index: int
    resolution: Tuple[int, int]
    priority: int
    #path: str