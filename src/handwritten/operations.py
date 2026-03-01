from dataclasses import dataclass
from typing import Protocol
import numpy as np
import cv2

class VisOpProtocol(Protocol):
    def apply(self) -> np.ndarray: ...
    def signature(self) -> tuple: ...

class VisOp(VisOpProtocol):
    registry: dict[str, type["VisOp"]] = {}

    label = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is VisOp:
            return
        name = cls.label or cls.__name__
        VisOp.registry[name] = cls

    @classmethod
    def create(cls, label:str, **kwargs) -> "VisOp":
        return cls.registry[label](**kwargs)

@dataclass(frozen=True)
class ThresholdOp(VisOp):
    """
    Binary thresholding operation.
    """
    threshold_value: int = 128
    label = "Threshold"

    def apply(self, img: np.ndarray) -> np.ndarray:
        _, result = cv2.threshold(img, self.threshold_value, 255, cv2.THRESH_BINARY)
        return result
    
    def signature(self):
        return tuple(self.label, self.threshold_value)

@dataclass(frozen=True)
class MorphOpenOp(VisOp):
    """
    Morphological opening operation (erosion followed by dilation).
    """
    kernel_size: int = 3
    label = "Morph Open"

    def apply(self, img: np.ndarray) -> np.ndarray:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, self.kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=1)
    
    def signature(self):
        return tuple(self.label, self.kernel_size)


@dataclass(frozen=True)
class MorphCloseOp(VisOp):
    """
    Morphological closing operation (dilation followed by erosion).
    """
    kernel_size: int = 3
    label = "Morph Close"

    def apply(self, img: np.ndarray) -> np.ndarray:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, self.kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    def signature(self):
        return tuple(self.label, self.kernel_size)


@dataclass(frozen=True)
class InvertOp(VisOp):
    """
    Image inversion operation.

    Inverts grayscale values: 255 - pixel_value.
    """
    label = "Invert"

    def apply(self, img: np.ndarray) -> np.ndarray:
        return 255 - img
    
    def signature(self):
        return tuple(self.label)


