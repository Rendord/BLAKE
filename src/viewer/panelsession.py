from typing import Protocol, Optional
from PyQt6.QtCore import Qt
import numpy as np
from cv2.typing import MatLike
from dataclasses import dataclass
import gc
from viewer.operations import VisOp


class TimeLineNode():
    history_hash: int
    op: VisOp
    label: str
    strength: int
    next: Optional["TimeLineNode"]
    previous: Optional["TimeLineNode"]

    @property
    def is_root(self) -> bool:
        return False

    def __init__(self, op: VisOp | None, next: Optional["TimeLineNode"], previous: Optional["TimeLineNode"]):
        self.op = op
        self.strength = 1
        if op is not None:
            self.label = op.label
        self.previous = previous
        self.next = next
        self.genHash()

    def genHash(self):
        if self.previous is not None:
            self.history_hash = hash((self.previous.history_hash, self.op.signature()))
        else:
            self.history_hash = hash(self.label)

    def propogateHistory(self):
        node = self

        while node is not None:
            node.calculateStrength()
            node.genHash()
            node = node.next

    def calculateStrength(self):
        if isinstance(self.previous.op, type(self.op)):
            self.strength = self.previous.strength + 1
        # else:
        #     self.strength = 0 #not sure if we want removing an iteration to maintain a new order 

    def findStartOfStack(self):
        node = self
        while not node.is_root and isinstance(node.previous.op, type(self.op)):
            node = node.previous

        if node.previous is not None:
            return node.previous.history_hash
        else:
            return node.history_hash
        
    def debug_print(self):
        print(f"node type: {type(self)}")
        print(f"node op type: {type(self)} with strength {self.strength}")
        string = f"next node: {type(self.next)}"
        if self.next is not None:
            string += f"operation: {type(self.next.op)} and hash: {self.next.history_hash}"
        print(string)
        string = f"next node: {type(self.previous)}"
        if self.previous is not None:
            string += f"operation: {type(self.previous.op)} and hash: {self.previous.history_hash}"
        print(string)

class RootNode(TimeLineNode):
    label = "Root"
    strength = 0
    def __init__(self):
        super().__init__(op=None, previous=None, next=None)  

    @property
    def is_root(self) -> bool:
        return True

class OperationTimeline():
    current: Optional[TimeLineNode]
    tail: Optional[TimeLineNode]
    timeline_size: int
    MAX_OPERATIONS: int = 50
    #lru_cache

    def __init__(self):
        super().__init__()
        self.tail = RootNode()
        self.current = self.tail
        self.timeline_size = 0

    def insertNode(self, vis_op:VisOp) -> None:
        cur = self.current
        #insert operation into timeline
        insertion = TimeLineNode(op=vis_op,previous=cur,next=cur.next)
        if cur.next is not None:
            cur.next.previous = insertion
        cur.next = insertion
        insertion.propogateHistory()
        #print(insertion.strength)
        print("hash at time of insertion: " + str(insertion.history_hash))

        # if self.timeline_size >= self.MAX_OPERATIONS:
        #     #pop oldest
        #     old_tail = self.tail
        #     self.tail = old_tail.next
        #     self.tail.previous = None
        #     del old_tail
        #     gc.collect()
        # else:
        self.timeline_size += 1

    def removeCurrent(self) -> None:
        #remove operation into timeline
        cur = self.current

        if cur.previous is None:
            return

        cur.previous.next = cur.next 

        if cur.next is not None:
            cur.next.previous = cur.previous
            self.current = cur.next
            self.current.propogateHistory()
            if isinstance(cur.next, type(self.current)) and cur.strength == self.current.strength:
                print("recalculated strength of next node is same as removed node")
        else: 
            self.current = cur.previous

        cur.next = None
        cur.previous = None

        self.timeline_size -= 1

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
