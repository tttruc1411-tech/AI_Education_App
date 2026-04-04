# src/modules/library/functions/array_operations.py
#
# ============================================================
#  AI Coding Lab — Array Operations Functions
#  Student-friendly NumPy wrappers.
#  Students call clean names; np complexity is hidden inside.
# ============================================================

import numpy as np


def normalize_array(arr):
    """
    Normalize array values to the 0–1 range using min-max scaling.

    Parameters
    ----------
    arr : ndarray
        Any NumPy array (1-D, 2-D, or higher).

    Returns
    -------
    ndarray
        Array of float64 with all values scaled between 0.0 and 1.0.

    Example
    -------
    >>> scores = np.array([10, 50, 90])
    >>> normalize_array(scores)
    array([0.  , 0.5 , 1.  ])
    """
    arr = np.array(arr, dtype=np.float64)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val == min_val:
        return np.zeros_like(arr, dtype=np.float64)
    return (arr - min_val) / (max_val - min_val)


def create_image_matrix(height, width, channels=3):
    """
    Create a blank (all-zero) image matrix of a given size.

    Parameters
    ----------
    height : int
        Number of pixel rows.
    width : int
        Number of pixel columns.
    channels : int, optional
        Number of color channels — 3 for BGR/RGB, 1 for grayscale (default 3).

    Returns
    -------
    ndarray
        Zero-filled uint8 array of shape (height, width, channels)
        or (height, width) when channels=1.

    Example
    -------
    >>> blank = create_image_matrix(480, 640)
    >>> blank.shape
    (480, 640, 3)
    """
    if channels == 1:
        return np.zeros((height, width), dtype=np.uint8)
    return np.zeros((height, width, channels), dtype=np.uint8)


def flatten_array(arr):
    """
    Flatten a multi-dimensional array into a 1-D array.

    Parameters
    ----------
    arr : ndarray
        Any NumPy array of arbitrary shape.

    Returns
    -------
    ndarray
        1-D array containing all elements in row-major (C) order.

    Example
    -------
    >>> img = np.ones((2, 3, 3), dtype=np.uint8)
    >>> flatten_array(img).shape
    (18,)
    """
    return np.array(arr).flatten()


def reshape_array(arr, new_shape):
    """
    Reshape an array to a new set of dimensions without changing its data.

    Parameters
    ----------
    arr : ndarray
        Source array to reshape.
    new_shape : tuple of int
        Target shape. One dimension may be -1 to let NumPy infer it.

    Returns
    -------
    ndarray
        View or copy reshaped to new_shape.

    Example
    -------
    >>> pixels = np.arange(12)
    >>> reshape_array(pixels, (3, 4))
    array([[ 0,  1,  2,  3],
           [ 4,  5,  6,  7],
           [ 8,  9, 10, 11]])
    """
    return np.array(arr).reshape(new_shape)


def compute_statistics(arr):
    """
    Compute descriptive statistics for a numeric array.

    Parameters
    ----------
    arr : ndarray
        Input numeric array (any shape).

    Returns
    -------
    dict
        Dictionary with keys:
        ``mean``, ``std``, ``min``, ``max``, ``median``, ``shape``.

    Example
    -------
    >>> stats = compute_statistics(np.array([1, 2, 3, 4, 5]))
    >>> stats['mean']
    3.0
    """
    arr = np.array(arr, dtype=np.float64)
    return {
        "mean":   float(np.mean(arr)),
        "std":    float(np.std(arr)),
        "min":    float(np.min(arr)),
        "max":    float(np.max(arr)),
        "median": float(np.median(arr)),
        "shape":  arr.shape,
    }


def one_hot_encode(labels, num_classes=None):
    """
    One-hot encode an integer label array.

    Parameters
    ----------
    labels : array-like of int
        1-D array of class indices, e.g. [0, 2, 1, 0].
    num_classes : int, optional
        Total number of classes. If None, inferred as max(labels) + 1.

    Returns
    -------
    ndarray
        2-D float32 array of shape (len(labels), num_classes) where each
        row has a single 1.0 at the class index and 0.0 elsewhere.

    Example
    -------
    >>> one_hot_encode([0, 2, 1], num_classes=3)
    array([[1., 0., 0.],
           [0., 0., 1.],
           [0., 1., 0.]], dtype=float32)
    """
    labels = np.array(labels, dtype=np.int32)
    if num_classes is None:
        num_classes = int(np.max(labels)) + 1
    result = np.zeros((len(labels), num_classes), dtype=np.float32)
    result[np.arange(len(labels)), labels] = 1.0
    return result
