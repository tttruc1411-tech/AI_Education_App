from src.modules.library.functions.ai_blocks import Draw_Detections_MultiClass
from src.modules.library.functions.ai_blocks import Close_Camera
from src.modules.library.functions.ai_blocks import Update_Dashboard
from src.modules.library.functions.ai_blocks import Init_Camera
from src.modules.library.functions.ai_blocks import Get_Camera_Frame
capture_camerattt = Init_Camera()
while True:
    # 🔵 Start Loop

    camera_frame = Get_Camera_Frame(capture_camera = capture_camerattt)
    Update_Dashboard(camera_frame = camera_frame, var_name = 'Objects', var_value = 1)



Close_Camera(capture_camera = capture_camerattt)