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


def adjust_brightness(input_image, factor=1.5):
    """
    Adjust image brightness by a factor. Clamps to 0-255.

    Parameters
    ----------
    input_image : ndarray
        The source image.
    factor : float
        Brightness multiplier (>1 brighter, <1 darker).

    Returns
    -------
    ndarray
        Brightness-adjusted image (uint8).
    """
    adjusted = np.clip(input_image.astype(np.float32) * float(factor), 0, 255)
    return adjusted.astype(np.uint8)


def rotate_image(input_image, angle=90):
    """
    Rotate image around center without cropping.

    Parameters
    ----------
    input_image : ndarray
        The source image to rotate.
    angle : int
        Rotation angle in degrees (positive = counter-clockwise).

    Returns
    -------
    ndarray
        Rotated image with expanded canvas to avoid cropping.
    """
    h, w = input_image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, float(angle), 1.0)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    new_w, new_h = int(h * sin + w * cos), int(h * cos + w * sin)
    M[0, 2] += (new_w - w) / 2
    M[1, 2] += (new_h - h) / 2
    return cv2.warpAffine(input_image, M, (new_w, new_h))


def crop_image(input_image, x=0, y=0, width=100, height=100):
    """
    Crop a rectangular region from the image.

    Parameters
    ----------
    input_image : ndarray
        The source image.
    x, y : int
        Top-left corner of the crop region.
    width, height : int
        Size of the crop region.

    Returns
    -------
    ndarray
        Cropped image region.
    """
    return input_image[int(y):int(y) + int(height), int(x):int(x) + int(width)]


def draw_text(input_image, text="Hello", x=10, y=30):
    """
    Draw text on the image at the specified position.

    Parameters
    ----------
    input_image : ndarray
        The source image.
    text : str
        Text to overlay.
    x, y : int
        Position of the text baseline.

    Returns
    -------
    ndarray
        Image with text overlay.
    """
    cv2.putText(input_image, str(text), (int(x), int(y)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return input_image


def convert_to_hsv(input_image):
    """
    Convert a BGR image to HSV color space.

    Parameters
    ----------
    input_image : ndarray
        A color (BGR) image.

    Returns
    -------
    ndarray
        HSV image (H x W x 3).
    """
    return cv2.cvtColor(input_image, cv2.COLOR_BGR2HSV)
