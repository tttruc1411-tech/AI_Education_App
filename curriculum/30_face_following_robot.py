# TITLE: Face-Following Robot
# TITLE_VI: Robot Theo Dõi Khuôn Mặt
# LEVEL: Advanced
# ICON: 🤖
# COLOR: #f97316
# DESC: Make a robot follow your face.
# DESC_VI: Làm robot theo dõi khuôn mặt của bạn.
# ============================================================
# ⚠️ WARNING: This example requires ORC Hub hardware (Motor Driver V2) connected via I2C

# Import camera blocks (Camera category)
from src.modules.library.functions.ai_blocks import Init_Camera, Get_Camera_Frame, Close_Camera
# Import AI face detection blocks (AI Vision category)
from src.modules.library.functions.ai_blocks import Load_YuNet_Model, Run_YuNet_Model, Draw_Detections
# Import display blocks (Display category)
from src.modules.library.functions.display_blocks import Show_Image, Observe_Variable
# Import robotics blocks (Robotics category)
from src.modules.library.functions.robotics import Set_Servo
# Import logic block (Logic category)
from src.modules.library.functions.logic_blocks import Print_Message

# Step 1: Load the AI face detection model
detector = Load_YuNet_Model(model_path = 'projects/model/face_detection_yunet_2023mar.onnx')

# Step 2: Start the camera — frame width is 640 pixels
capture_camera = Init_Camera()
servo_angle = 90  # Start servo at center position
print("[OK] Face-Following Robot ready!")

# Step 3: Track faces and move the servo to follow
while True:
    camera_frame = Get_Camera_Frame(capture_camera = capture_camera)

    # AI decision: detect faces in the frame
    Run_YuNet_Model(ai_detector = detector, camera_frame = camera_frame)
    _, faces = detector.detect(camera_frame)
    face_count = Draw_Detections(camera_frame = camera_frame, results = faces, label = 'Face')

    # AI logic: calculate face center and decide servo direction
    if faces is not None and len(faces) > 0:
        # Extract the first detected face bounding box [x, y, w, h, ...]
        face_x = int(faces[0][0])
        face_w = int(faces[0][2])
        face_center_x = face_x + face_w // 2

        # Decision: if face is left of center, pan servo left; otherwise pan right
        frame_center = 320  # Half of 640px frame width
        if face_center_x < frame_center - 50:
            servo_angle = min(servo_angle + 5, 180)  # Pan left
            Print_Message(message = "Panning LEFT to follow face")
        else:
            servo_angle = max(servo_angle - 5, 0)    # Pan right
            Print_Message(message = "Panning RIGHT to follow face")

        # Move the servo to track the face
        Set_Servo(pin = 'S1', angle = servo_angle)

    # Stream the feed and show current servo angle
    Show_Image(camera_frame = camera_frame)
    Observe_Variable(var_name = 'Servo Angle', var_value = servo_angle)

Close_Camera(capture_camera = capture_camera)
