from typing import Protocol, Optional, List
from cv2.typing import MatLike
from dataclasses import dataclass
from pathlib import Path
import gc

class VisOp(Protocol):
    def apply(self) -> None: ...
    computed_image: MatLike #_typing.Union[cv2.mat_wrapper.Mat, NumPyArrayNumeric]
    next: Optional["VisOp"]
    previous: Optional["VisOp"]

class PanelSession():
    current: Optional[VisOp]
    tail: Optional[VisOp]
    timeline_size: int
    image_paths: List[Path]
    MAX_OPERATIONS: int = 50

    def __init__(self):
        self.current = None
        self.tail = None
        self.timeline_size = 0
        self.image_paths = []

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

    def load_image_paths(self, src: str | Path) -> int:
        src = Path(src)

        if not src.is_dir(): return 0

        valid_extensions = {'.jp2','.png','.jpeg','.jpg','.webp'}

        self.image_paths.clear()
        for path in src.iterdir():
            if path.is_file() and path.suffix.lower() in valid_extensions:
                self.image_paths.append(path)

        self.image_paths.sort()

        return len(self.image_paths)