"""Display and visualization blocks for the AI Coding Lab Function Library."""

import cv2
import numpy as np
import time
import base64
import sys

_prev_time = 0  # module-level state for FPS calculation


def Show_FPS(camera_frame):
    """Calculate and overlay FPS on the frame. Returns the annotated frame."""
    global _prev_time
    current_time = time.time()
    fps = 1.0 / (current_time - _prev_time) if _prev_time > 0 else 0
    _prev_time = current_time
    cv2.putText(camera_frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return camera_frame


def Show_Image(camera_frame):
    """Stream a camera frame to the Live Feed panel."""
    if camera_frame is not None:
        ok, buffer = cv2.imencode('.jpg', camera_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if ok:
            img_b64 = base64.b64encode(buffer).decode('utf-8')
            print(f"IMG:{img_b64}")
    sys.stdout.flush()


def Observe_Variable(var_name="Result", var_value=None):
    """Display a variable's value in the Results panel."""
    print(f"VAR:{var_name}:{var_value}")
    sys.stdout.flush()


def Draw_Rectangle(camera_frame, x=0, y=0, width=100, height=100, color="green"):
    """Draw a colored rectangle on the frame."""
    color_map = {"green": (0, 255, 0), "red": (0, 0, 255), "blue": (255, 0, 0),
                 "yellow": (0, 255, 255), "white": (255, 255, 255)}
    bgr = color_map.get(color.lower(), (0, 255, 0))
    cv2.rectangle(camera_frame, (int(x), int(y)),
                  (int(x) + int(width), int(y) + int(height)), bgr, 2)
    return camera_frame


def Draw_Circle(camera_frame, center_x=0, center_y=0, radius=50, color="green"):
    """Draw a colored circle on the frame."""
    color_map = {"green": (0, 255, 0), "red": (0, 0, 255), "blue": (255, 0, 0),
                 "yellow": (0, 255, 255), "white": (255, 255, 255)}
    bgr = color_map.get(color.lower(), (0, 255, 0))
    cv2.circle(camera_frame, (int(center_x), int(center_y)), int(radius), bgr, 2)
    return camera_frame


# ── Color name lookup shared by drawing functions ─────────────
COLOR_MAP = {
    "green": (0, 255, 0),
    "red": (0, 0, 255),
    "blue": (255, 0, 0),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "yellow": (0, 255, 255),
}


def Draw_Line(camera_frame, x1, y1, x2, y2, color='green'):
    """
    Draw a colored line on the camera frame.

    Parameters
    ----------
    camera_frame : ndarray
        The image to draw on.
    x1, y1 : int
        Starting point coordinates.
    x2, y2 : int
        Ending point coordinates.
    color : str
        Color name — 'green', 'red', 'blue', 'white', 'black', or 'yellow'.

    Returns
    -------
    ndarray
        The frame with the line drawn, or None on failure.
    """
    try:
        bgr = COLOR_MAP.get(color.lower(), (0, 255, 0))
        cv2.line(camera_frame, (int(x1), int(y1)), (int(x2), int(y2)), bgr, 2)
        return camera_frame
    except Exception as e:
        print(f"[Display] Error in Draw_Line: {e}")
        return None


def Draw_Text_Box(camera_frame, text, x, y, bg_color='blue', text_color='white'):
    """
    Draw text with a filled background rectangle on the camera frame.

    Parameters
    ----------
    camera_frame : ndarray
        The image to draw on.
    text : str
        The text string to display.
    x, y : int
        Top-left corner of the text box.
    bg_color : str
        Background rectangle color name.
    text_color : str
        Text color name.

    Returns
    -------
    ndarray
        The frame with the text box drawn, or None on failure.
    """
    try:
        bg_bgr = COLOR_MAP.get(bg_color.lower(), (255, 0, 0))
        txt_bgr = COLOR_MAP.get(text_color.lower(), (255, 255, 255))
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.6
        thickness = 2
        (tw, th), baseline = cv2.getTextSize(str(text), font, scale, thickness)
        x, y = int(x), int(y)
        # Draw filled rectangle behind text
        cv2.rectangle(camera_frame, (x, y), (x + tw + 10, y + th + baseline + 10), bg_bgr, -1)
        # Draw text on top
        cv2.putText(camera_frame, str(text), (x + 5, y + th + 5), font, scale, txt_bgr, thickness)
        return camera_frame
    except Exception as e:
        print(f"[Display] Error in Draw_Text_Box: {e}")
        return None


def Stack_Images(image1, image2, direction='horizontal'):
    """
    Stack two images side-by-side (horizontal) or top-bottom (vertical).
    Automatically resizes the second image to match dimensions for stacking.

    Parameters
    ----------
    image1 : ndarray
        First image.
    image2 : ndarray
        Second image.
    direction : str
        'horizontal' for side-by-side, 'vertical' for top-bottom.

    Returns
    -------
    ndarray
        The combined image, or None on failure.
    """
    try:
        if direction.lower() == 'horizontal':
            # Match heights
            if image1.shape[0] != image2.shape[0]:
                print("[Display] Resizing images to match for stacking.")
                image2 = cv2.resize(image2, (image2.shape[1], image1.shape[0]))
            # Ensure same number of channels
            if len(image1.shape) != len(image2.shape):
                if len(image1.shape) == 2:
                    image1 = cv2.cvtColor(image1, cv2.COLOR_GRAY2BGR)
                if len(image2.shape) == 2:
                    image2 = cv2.cvtColor(image2, cv2.COLOR_GRAY2BGR)
            return np.hstack((image1, image2))
        else:
            # Match widths
            if image1.shape[1] != image2.shape[1]:
                print("[Display] Resizing images to match for stacking.")
                image2 = cv2.resize(image2, (image1.shape[1], image2.shape[0]))
            # Ensure same number of channels
            if len(image1.shape) != len(image2.shape):
                if len(image1.shape) == 2:
                    image1 = cv2.cvtColor(image1, cv2.COLOR_GRAY2BGR)
                if len(image2.shape) == 2:
                    image2 = cv2.cvtColor(image2, cv2.COLOR_GRAY2BGR)
            return np.vstack((image1, image2))
    except Exception as e:
        print(f"[Display] Error in Stack_Images: {e}")
        return None
