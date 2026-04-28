# src/modules/library/functions/camera_blocks.py
#
# Student-friendly camera functions.
# Usage: import camera
# Then:  camera.Init_Camera(), camera.Get_Camera_Frame(), etc.

import sys
import os
import cv2


def Init_Camera(camera_id=0):
    """
    Opens the camera and checks for errors.
    Returns the capture object.
    """
    capture_camera = cv2.VideoCapture(camera_id)
    if not capture_camera.isOpened():
        print(f"ERROR: Could not open camera {camera_id}.")
        print("TIP: Make sure no other app is using the camera.")
        sys.exit()
    return capture_camera


def Get_Camera_Frame(capture_camera):
    """
    Reads a single frame from the camera.
    Returns the frame if successful, or None if the camera can't be read.
    """
    if capture_camera is None:
        return None
    ret, camera_frame = capture_camera.read()
    if not ret:
        print("ERROR: Cannot access camera frame.")
        print("TIP: Check if the camera was accidentally disconnected.")
        return None
    return camera_frame


def Close_Camera(capture_camera):
    """
    Successfully releases the camera and closes any OpenCV windows.
    """
    if capture_camera is not None:
        capture_camera.release()
    cv2.destroyAllWindows()
    print("[OK] Camera released and windows closed.")


def Save_Frame(camera_frame, file_path="snapshot.jpg"):
    """
    Save a camera frame to disk as an image file.
    Images are saved to projects/data/saved/ by default.
    """
    if camera_frame is None:
        print("ERROR: No frame to save.")
        return
    # Auto-create the saved folder inside projects/data/
    save_dir = os.path.join("projects", "data", "saved")
    os.makedirs(save_dir, exist_ok=True)
    # If the path is just a filename (no directory), put it in the saved folder
    if os.path.dirname(file_path) == "":
        file_path = os.path.join(save_dir, file_path)
    cv2.imwrite(file_path, camera_frame)
    print(f"[OK] Frame saved to {file_path}")


def Load_Image(file_path="image.jpg"):
    """
    Load an image from disk. Returns the image or None if not found.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: File '{file_path}' not found!")
        return None
    img = cv2.imread(file_path)
    if img is None:
        print(f"ERROR: Could not read '{file_path}' as an image.")
        return None
    print(f"[OK] Image loaded from {file_path}")
    return img

import time


def Set_Camera_Resolution(capture_camera, width=640, height=480):
    """
    Set the camera capture resolution.

    Parameters
    ----------
    capture_camera : cv2.VideoCapture
        The camera capture object from Init_Camera.
    width : int
        Desired frame width in pixels.
    height : int
        Desired frame height in pixels.

    Returns
    -------
    None
    """
    try:
        if capture_camera is None:
            print("[Camera] No camera initialized.")
            return
        capture_camera.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        capture_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
        print(f"[OK] Camera resolution set to {int(width)}x{int(height)}")
    except Exception as e:
        print(f"[Camera] Error in Set_Camera_Resolution: {e}")


def Capture_Snapshot(capture_camera, countdown=0):
    """
    Capture a single frame from the camera with an optional countdown.

    Parameters
    ----------
    capture_camera : cv2.VideoCapture
        The camera capture object from Init_Camera.
    countdown : int
        Number of seconds to count down before capturing. 0 = immediate.

    Returns
    -------
    ndarray or None
        The captured frame, or None on failure.
    """
    try:
        if capture_camera is None:
            print("[Camera] No camera initialized.")
            return None
        countdown = int(countdown)
        if countdown > 0:
            for i in range(countdown, 0, -1):
                print(f"[Camera] Capturing in {i}...")
                time.sleep(1)
        ret, camera_frame = capture_camera.read()
        if not ret:
            print("[Camera] Failed to capture snapshot.")
            return None
        print("[OK] Snapshot captured!")
        return camera_frame
    except Exception as e:
        print(f"[Camera] Error in Capture_Snapshot: {e}")
        return None
