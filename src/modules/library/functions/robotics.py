# src/modules/library/functions/robotics.py
#
# Student-friendly robotics blocks for OhStem Motor Driver V2.
# Each function manages a shared driver singleton so students
# never have to worry about I2C init — just drag, drop, and run.

import time
from src.modules.library.functions.motor_driver_v2 import (
    MotorDriverV2, M1, M2, M3, M4, E1, E2, S1, S2, S3, S4, ALL,
)

# ── Shared driver singleton ──────────────────────────────────
_driver = None
_driver_init_attempted = False

# Pin-name lookup so students type strings like "M1" or "E2"
_PIN_MAP = {
    "M1": M1, "M2": M2, "M3": M3, "M4": M4,
    "E1": E1, "E2": E2,
}

_SERVO_MAP = {
    "S1": S1, "S2": S2, "S3": S3, "S4": S4,
}

def _get_driver():
    """Return the shared MotorDriverV2 instance, or None if hardware is absent."""
    global _driver, _driver_init_attempted
    if _driver is None and not _driver_init_attempted:
        _driver_init_attempted = True
        try:
            _driver = MotorDriverV2(bus=1)
        except (RuntimeError, OSError) as e:
            print(f"[Robotics] ORC Hub not found: {e}")
            print("[Robotics] Connect the ORC Hub and restart to enable motor control.")
            _driver = None
    return _driver


def _resolve_pin(pin):
    """Accept 'M1', 'E2', etc. as string or the raw bitmask constant."""
    if isinstance(pin, str):
        key = pin.strip().upper()
        if key in _PIN_MAP:
            return _PIN_MAP[key]
        raise ValueError(f"Unknown motor pin '{pin}'. Use M1-M4 or E1-E2.")
    return pin


def _resolve_servo(pin):
    """Accept 'S1'-'S4' as string or the raw index constant."""
    if isinstance(pin, str):
        key = pin.strip().upper()
        if key in _SERVO_MAP:
            return _SERVO_MAP[key]
        raise ValueError(f"Unknown servo pin '{pin}'. Use S1-S4.")
    return pin


# ── Public blocks (dragged into student code) ────────────────

def DC_Run(pin, speed, time_ms=None):
    """
    Run a DC motor or encoder motor.

    Parameters
    ----------
    pin : str
        Motor port — 'M1', 'M2', 'M3', 'M4', 'E1', or 'E2'.
    speed : int
        Power level from -100 to 100.
        Positive = forward, Negative = backward.
    time_ms : int or None
        Duration in milliseconds.  Leave blank to run forever
        (until DC_Stop is called).

    Examples
    --------
    DC_Run('M1', 50)           # M1 forward 50 % — runs forever
    DC_Run('E1', -80, 2000)    # E1 backward 80 % for 2 seconds
    """
    md = _get_driver()
    if md is None:
        print("[Robotics] Cannot run motor — ORC Hub not connected.")
        return
    port = _resolve_pin(pin)
    md.set_motors(port, speed)

    if time_ms is not None and int(time_ms) > 0:
        time.sleep(int(time_ms) / 1000)
        md.stop(port)


def DC_Stop(pin=None):
    """
    Stop a DC motor (or all motors).

    Parameters
    ----------
    pin : str or None
        Motor port — 'M1', 'M2', 'M3', 'M4', 'E1', or 'E2'.
        Leave blank to stop ALL motors at once.

    Examples
    --------
    DC_Stop('M1')    # stop only M1
    DC_Stop()        # stop every motor
    """
    md = _get_driver()
    if md is None:
        print("[Robotics] Cannot stop motor — ORC Hub not connected.")
        return
    if pin is None or str(pin).strip() == "":
        md.stop(ALL)
    else:
        md.stop(_resolve_pin(pin))


def Get_Speed(pin):
    """
    Read the current speed of an encoder motor in RPM.
    Only works with encoder ports (E1 or E2).

    Parameters
    ----------
    pin : str
        Encoder port — 'E1' or 'E2'.

    Returns
    -------
    float
        Speed in RPM (revolutions per minute).

    Examples
    --------
    rpm = Get_Speed('E1')
    print(rpm)   # e.g. 120.5
    """
    md = _get_driver()
    if md is None:
        print("[Robotics] Cannot read speed — ORC Hub not connected.")
        return 0.0
    port = _resolve_pin(pin)
    return md.get_speed_rpm(port)


def Set_Servo(pin, angle):
    """
    Rotate a servo to the specified angle.

    Parameters
    ----------
    pin : str
        Servo port — 'S1', 'S2', 'S3', or 'S4'.
    angle : int
        Target angle from 0 to 180 degrees.

    Examples
    --------
    Set_Servo('S1', 90)    # center position
    Set_Servo('S2', 0)     # fully left
    """
    md = _get_driver()
    if md is None:
        print("[Robotics] Cannot set servo — ORC Hub not connected.")
        return
    idx = _resolve_servo(pin)
    md.set_servo(idx, int(angle))


def Sweep_Servo(pin='S1', start_angle=0, end_angle=180, step=10, delay=0.05):
    """
    Smoothly sweep a servo motor across an angle range.

    Iterates from start_angle to end_angle in increments of step,
    calling Set_Servo at each position with a delay pause between steps.

    Parameters
    ----------
    pin : str
        Servo port — 'S1', 'S2', 'S3', or 'S4'.
    start_angle : int
        Starting angle (0–180).
    end_angle : int
        Ending angle (0–180).
    step : int
        Angle increment per step.
    delay : float
        Seconds to pause between each step.

    Returns
    -------
    None
    """
    try:
        md = _get_driver()
        if md is None:
            print("[Robotics] ORC Hub not connected. Sweep cancelled.")
            return
        start_angle = int(start_angle)
        end_angle = int(end_angle)
        step = int(step)
        if step <= 0:
            print("[Robotics] Step must be positive.")
            return
        for angle in range(start_angle, end_angle + 1, step):
            Set_Servo(pin, angle)
            time.sleep(float(delay))
    except Exception as e:
        print(f"[Robotics] Error in Sweep_Servo: {e}")
