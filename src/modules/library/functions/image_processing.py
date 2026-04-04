# src/modules/library/functions/image_processing.py
#
# ============================================================
#  AI Coding Lab — Image Processing Functions
#  Student-friendly wrappers around OpenCV.
#  Students call these clean names; OpenCV is hidden inside.
# ============================================================

import cv2
import numpy as np


def convert_to_gray(input_image):
    """
    Convert a color (BGR) image to grayscale.

    Parameters
    ----------
    input_image : ndarray
        A color image loaded with cv2.imread or from a camera frame.

    Returns
    -------
    ndarray
        A single-channel (H x W) grayscale image.
    """
    return cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)


def resize_image(input_image, width, height):
    """
    Resize an image to the given width and height.

    Parameters
    ----------
    input_image : ndarray
        The source image to resize.
    width : int
        Target width in pixels.
    height : int
        Target height in pixels.

    Returns
    -------
    ndarray
        The resized image (height x width x channels).
    """
    return cv2.resize(input_image, (width, height))


def apply_blur(input_image, kernel_size=5):
    """
    Apply Gaussian blur to smooth an image.

    Parameters
    ----------
    input_image : ndarray
        The source image to blur.
    kernel_size : int, optional
        Size of the Gaussian kernel (must be odd, default 5).

    Returns
    -------
    ndarray
        The blurred image, same shape as input.
    """
    # Kernel size must be odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(input_image, (kernel_size, kernel_size), 0)


def detect_edges(input_image, threshold1=100, threshold2=200):
    """
    Detect edges in an image using the Canny algorithm.

    Parameters
    ----------
    input_image : ndarray
        The source image (color or grayscale).
    threshold1 : int, optional
        Lower threshold for the hysteresis procedure (default 100).
    threshold2 : int, optional
        Upper threshold for the hysteresis procedure (default 200).

    Returns
    -------
    ndarray
        A binary edge map (same H x W as input, single channel).
    """
    # Canny works best on grayscale
    if len(input_image.shape) == 3:
        gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = input_image
    return cv2.Canny(gray, threshold1, threshold2)


def flip_image(input_image, direction="horizontal"):
    """
    Flip an image horizontally or vertically.

    Parameters
    ----------
    input_image : ndarray
        The source image to flip.
    direction : str, optional
        'horizontal' (default) flips left-right.
        'vertical' flips upside-down.
        'both' flips on both axes.

    Returns
    -------
    ndarray
        The flipped image, same shape as input.
    """
    flip_codes = {
        "horizontal": 1,
        "vertical": 0,
        "both": -1,
    }
    code = flip_codes.get(direction, 1)
    return cv2.flip(input_image, code)
