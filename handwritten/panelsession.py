from typing import Protocol, List, Optional
from typing import List
from cv2.typing import MatLike
from dataclasses import dataclass, field
import gc

class VisOp(Protocol):
    def apply(self) -> None: ...
    computed_image: MatLike #_typing.Union[cv2.mat_wrapper.Mat, NumPyArrayNumeric]
    next: Optional["VisOp"]
    previous: Optional["VisOp"]

@dataclass(slots=True)
class PanelSession():
    current: Optional[VisOp] = None
    tail: Optional[VisOp] = None
    timeline_size: int = 0
    path: str = ""
    MAX_OPERATIONS: int = 50

    def insertOp(self, insertion:VisOp) -> None:
        #insert operation into timeline
        cur = self.current
        if cur.next is not None:
            cur.next.previous = insertion
        insertion.next = cur.next
        cur.next = insertion
        insertion.previous = cur

        if self.timeline_size >= self.MAX_OPERATIONS:
            #pop oldest
            old_tail = self.tail
            self.tail = old_tail.next
            self.tail.previous = None
            del old_tail
            gc.collect()
        else:
            self.timeline_size += 1

    def ascend(self) -> None:        
        cur = self.current
        if cur.next is not None:
            self.current = cur.next
        #else: pass
    
    def descend(self) -> None:        
        cur = self.current
        if cur.previous is not None:
            self.current = cur.previous
        #else: pass


