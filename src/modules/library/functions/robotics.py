# src/modules/library/functions/robotics.py
#
# Helper functions to control devices via the OH STEM ORC Hub.
# These are stubs to be implemented by the user later.

def Move_Robot(motor_pin, motor_speed):
    """
    Moves the robot using a specific motor pin and power level.
    - motor_pin: The hub port/pin number
    - motor_speed: The power level (-100 to 100)
    """
    # [IMPLEMENTATION PENDING]
    # This will send a signal to the ORC Hub via serial/USB
    print(f"[ORC HUB] Move -> Pin: {motor_pin}, Speed: {motor_speed}")
    pass

def Turn_Robot(turn_direction, turn_speed):
    """
    Rotates the robot in a specific direction.
    - turn_direction: 'left' or 'right'
    - turn_speed: The turning power (0 to 100)
    """
    # [IMPLEMENTATION PENDING]
    print(f"[ORC HUB] Turn -> {turn_direction.upper()} at Speed: {turn_speed}")
    pass
