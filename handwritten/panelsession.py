from typing import Protocol, Optional
from PyQt6.QtCore import Qt
from cv2.typing import MatLike
from cv2.typing import MatLike
import gc

class VisOp(Protocol):
    def apply(self) -> None: ...
    computed_image: MatLike #_typing.Union[cv2.mat_wrapper.Mat, NumPyArrayNumeric]
    next: Optional["VisOp"]
    previous: Optional["VisOp"]

class OperationTimeline():
    current: Optional[VisOp]
    tail: Optional[VisOp]
    timeline_size: int
    MAX_OPERATIONS: int = 50
    #lru_cache

    def __init__(self):
        super().__init__()
        self.current = None
        self.tail = None
        self.timeline_size = 0

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
