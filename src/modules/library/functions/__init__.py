# src/modules/library/functions/__init__.py
# Public API for all student-callable library functions.

from .camera_blocks import (
    Init_Camera,
    Get_Camera_Frame,
    Close_Camera,
    Save_Frame,
    Load_Image,
)

from .ai_vision_blocks import (
    Load_YuNet_Model,
    Run_YuNet_Model,
    Load_ONNX_Model,
    Run_ONNX_Model,
    Load_Engine_Model,
    Run_Engine_Model,
)

from .drawing_blocks import (
    Draw_Detections,
    Draw_Detections_MultiClass,
    Draw_Engine_Detections,
    Update_Dashboard,
)

from .display_blocks import (
    Show_FPS,
    Show_Image,
    Observe_Variable,
    Draw_Rectangle,
    Draw_Circle,
)

from .image_processing import (
    convert_to_gray,
    resize_image,
    apply_blur,
    detect_edges,
    flip_image,
    adjust_brightness,
    rotate_image,
    crop_image,
    draw_text,
    convert_to_hsv,
)

from .logic_blocks import (
    Wait_Seconds,
    Print_Message,
)

from .variables import (
    Create_Text,
    Create_Number,
    Create_Decimal,
    Create_Boolean,
    Create_List,
)
