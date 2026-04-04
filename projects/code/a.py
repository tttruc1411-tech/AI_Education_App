from src.modules.library.functions.ai_blocks import Update_Dashboard
from src.modules.library.functions.ai_blocks import Init_Camera
from src.modules.library.functions.ai_blocks import Get_Camera_Frame
capture_camerattt = Init_Camera()
while True:
    # 🔵 Start Loop
    camera_frame = Get_Camera_Frame(capture_camera = None)