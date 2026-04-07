from src.modules.library.functions.ai_blocks import Update_Dashboard
from src.modules.library.functions.ai_blocks import Close_Camera
from src.modules.library.functions.ai_blocks import Draw_Engine_Detections
from src.modules.library.functions.ai_blocks import Run_Engine_Model
from src.modules.library.functions.ai_blocks import Get_Camera_Frame
from src.modules.library.functions.ai_blocks import Load_Engine_Model
from src.modules.library.functions.ai_blocks import Init_Camera


capture_camera = Init_Camera()
engine_model = Load_Engine_Model(model_path = 'projects/model/yolov10n.engine')
while True:
    # 🔵 Start Loop
    # Add your code here
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)
    engine_results = Run_Engine_Model(engine_model = engine_model, camera_frame = camera_frame)    

    # 🔴 End Loop
    obj_count = Draw_Engine_Detections(camera_frame = camera_frame, results = engine_results, classes = "Object")
    Update_Dashboard(camera_frame = camera_frame, var_name = 'Objects', var_value = obj_count)
    

Close_Camera(capture_camera = capture_camera)