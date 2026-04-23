"""Display and visualization blocks for the AI Coding Lab Function Library."""

import cv2
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
