# TITLE: Motor Speed Dashboard
# TITLE_VI: Bảng Điều Khiển Tốc Độ Động Cơ
# LEVEL: Advanced
# ICON: 🏎️
# COLOR: #f97316
# DESC: Monitor motor speeds on a live dashboard.
# DESC_VI: Theo dõi tốc độ động cơ trên bảng điều khiển trực tiếp.
# ORDER: 38
# ============================================================

import camera
import display
import image
import logic
import robotics
import variables

# ⚠️ WARNING: This example requires ORC Hub hardware (Motor Driver V2) connected via I2C


# Step 1: Create variables to store RPM readings for two motors
rpm_motor1 = variables.Create_Decimal(value = 0.0)
rpm_motor2 = variables.Create_Decimal(value = 0.0)

# Step 2: Start the camera for the live dashboard background
capture_camera = camera.Init_Camera()
print("[OK] Motor Speed Dashboard active!")

# Step 3: Read encoder speeds and display on the dashboard
while True:
    camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # Read RPM from encoder motors E1 and E2
    rpm_motor1 = robotics.Get_Speed(pin = 'E1')
    rpm_motor2 = robotics.Get_Speed(pin = 'E2')

    # Draw gauge background rectangles for each motor
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 10, y = 380, width = 200, height = 80, color = 'blue')
    camera_frame = display.Draw_Rectangle(camera_frame = camera_frame, x = 430, y = 380, width = 200, height = 80, color = 'blue')

    # Overlay RPM readings on the dashboard
    camera_frame = image.draw_text(input_image = camera_frame, text = f'Motor E1: {rpm_motor1:.1f} RPM', x = 20, y = 420)
    camera_frame = image.draw_text(input_image = camera_frame, text = f'Motor E2: {rpm_motor2:.1f} RPM', x = 440, y = 420)

    # Threshold check: warn if any motor exceeds safe speed
    if rpm_motor1 > 100 or rpm_motor2 > 100:
        camera_frame = image.draw_text(input_image = camera_frame, text = 'WARNING: High Speed!', x = 180, y = 350)
        logic.Print_Message(message = f"Speed warning! E1={rpm_motor1:.1f} E2={rpm_motor2:.1f}")

    # Show FPS for dashboard refresh rate
    camera_frame = display.Show_FPS(camera_frame = camera_frame)

    # Stream the dashboard and track RPM values
    display.Show_Image(camera_frame = camera_frame)
    display.Observe_Variable(var_name = 'E1 RPM', var_value = round(rpm_motor1, 1))
    display.Observe_Variable(var_name = 'E2 RPM', var_value = round(rpm_motor2, 1))

camera.Close_Camera(capture_camera = capture_camera)
