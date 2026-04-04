# src/modules/library/functions/__init__.py
# Public API for all student-callable library functions.

from .image_processing import (
    convert_to_gray,
    resize_image,
    apply_blur,
    detect_edges,
    flip_image,
)

from .array_operations import (
    normalize_array,
    create_image_matrix,
    flatten_array,
    reshape_array,
    compute_statistics,
    one_hot_encode,
)

__all__ = [
    # Image Processing
    "convert_to_gray",
    "resize_image",
    "apply_blur",
    "detect_edges",
    "flip_image",
    # Array Operations
    "normalize_array",
    "create_image_matrix",
    "flatten_array",
    "reshape_array",
    "compute_statistics",
    "one_hot_encode",
]
