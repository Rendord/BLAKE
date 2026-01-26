"""
Operation classes for manga panel image processing.

Defines an abstract Operation base class and 5 concrete operations:
- ThresholdOp: Binary thresholding (manual or OTSU)
- RotateOp: Rotation around center
- MorphOpenOp: Morphological opening
- MorphCloseOp: Morphological closing
- InvertOp: Image inversion
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Any
import numpy as np
import cv2


def rotate_image(img: np.ndarray, angle_deg: float) -> np.ndarray:
    """
    Rotate an image around its center by angle_deg degrees.
    Keeps original dimensions.

    Extracted from test_vectorization.py
    """
    h, w = img.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    rotated = cv2.warpAffine(
        img,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


@dataclass(frozen=True)
class Operation(ABC):
    """Abstract base class for image operations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable operation name for display."""
        pass

    @property
    def params(self) -> dict[str, Any]:
        """Return parameters as dictionary for UI display."""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @abstractmethod
    def apply(self, img: np.ndarray) -> np.ndarray:
        """Apply operation to image and return result."""
        pass


@dataclass(frozen=True)
class ThresholdOp(Operation):
    """
    Binary thresholding operation.

    If threshold_value == 0, uses OTSU automatic thresholding.
    Otherwise, uses manual threshold at the specified value.
    """
    threshold_value: int = 128

    @property
    def name(self) -> str:
        if self.threshold_value == 0:
            return "Threshold(OTSU)"
        return f"Threshold({self.threshold_value})"

    def apply(self, img: np.ndarray) -> np.ndarray:
        if self.threshold_value == 0:
            # OTSU automatic thresholding
            _, result = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            # Manual threshold
            _, result = cv2.threshold(img, self.threshold_value, 255, cv2.THRESH_BINARY)
        return result


@dataclass(frozen=True)
class RotateOp(Operation):
    """
    Rotation operation around image center.

    Maintains original image dimensions, fills borders with replication.
    """
    angle_deg: float = 0.0

    @property
    def name(self) -> str:
        return f"Rotate({self.angle_deg:.1f}°)"

    def apply(self, img: np.ndarray) -> np.ndarray:
        return rotate_image(img, self.angle_deg)


@dataclass(frozen=True)
class MorphOpenOp(Operation):
    """
    Morphological opening operation (erosion followed by dilation).

    Useful for removing small noise from the foreground.
    """
    kernel_size: int = 3

    @property
    def name(self) -> str:
        return f"MorphOpen({self.kernel_size}x{self.kernel_size})"

    def apply(self, img: np.ndarray) -> np.ndarray:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, self.kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=1)


@dataclass(frozen=True)
class MorphCloseOp(Operation):
    """
    Morphological closing operation (dilation followed by erosion).

    Useful for closing small holes in the foreground.
    """
    kernel_size: int = 3

    @property
    def name(self) -> str:
        return f"MorphClose({self.kernel_size}x{self.kernel_size})"

    def apply(self, img: np.ndarray) -> np.ndarray:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, self.kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=1)


@dataclass(frozen=True)
class InvertOp(Operation):
    """
    Image inversion operation.

    Inverts grayscale values: 255 - pixel_value.
    """

    @property
    def name(self) -> str:
        return "Invert"

    def apply(self, img: np.ndarray) -> np.ndarray:
        return 255 - img


def create_operation(op_type: str, **params) -> Operation:
    """
    Factory function for creating operations from UI.

    Args:
        op_type: Operation type name ('Threshold', 'Rotate', etc.)
        **params: Operation parameters

    Returns:
        Concrete Operation instance

    Raises:
        KeyError: If op_type is not recognized
    """
    op_classes = {
        'Threshold': ThresholdOp,
        'Rotate': RotateOp,
        'MorphOpen': MorphOpenOp,
        'MorphClose': MorphCloseOp,
        'Invert': InvertOp
    }

    if op_type not in op_classes:
        raise KeyError(f"Unknown operation type: {op_type}")

    return op_classes[op_type](**params)
