from typing import Tuple
from dataclasses import dataclass
from viewer.panelsession import TimeLineNode

@dataclass(frozen=True)
class RenderJob():
    index: int
    resolution: Tuple[int, int]
    priority: int
#   history_hash: int