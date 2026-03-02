from typing import Tuple
from dataclasses import dataclass
from handwritten.panelsession import TimeLineNode

@dataclass(frozen=True)
class RenderJob():
    index: int
    resolution: Tuple[int, int]
    priority: int
    timeline_tail: TimeLineNode
    #path: str