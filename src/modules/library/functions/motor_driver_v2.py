"""
Motor Driver V2 (OhStem) - Jetson Orin Nano Super
I2C driver using smbus2, ported from MicroPython (YoloUNO)

Hardware connection (3 wires):
    - SDA -> Pin 27
    - SCL -> Pin 28
    - GND -> Pin 30

Install:
    pip3 install smbus2 --break-system-packages

Run test:
    sudo python3 motor_driver_v2.py 1

Ports on Driver V2 board:
    M1, M2, M3, M4  - DC motor (2 wires: + and -)
    E1, E2           - Encoder DC motor (6 wires, can read speed)
    S1, S2, S3, S4   - Servo

Bitmask (from OhStem constants.py):
    M1 = 0x01 (1)     M2 = 0x02 (2)
    M3 = 0x04 (4)     M4 = 0x08 (8)
    E1 = 0x10 (16)    E2 = 0x20 (32)
    ALL = 0x3F (63)

Functions:
    md.set_motors(M1, 50)      # run M1 forward 50%
    md.set_motors(E1, 50)      # run E1 forward 50%
    md.set_motors(M1, -50)     # run M1 backward 50%
    md.stop()                  # stop all
    md.stop(M1)                # stop M1 only
    md.brake(M1)               # brake M1 (lock motor)
    md.set_servo(S1, 90)       # set servo S1 to 90 degrees
    md.get_speed(E1)           # read E1 speed (raw ticks)
    md.get_speed_rpm(E1)       # read E1 speed (RPM)
    md.battery()               # read battery voltage
    md.fw_version()            # read firmware version
"""

import time
from smbus2 import SMBus

# Motor bitmask (from OhStem constants.py)
M1  = 0x01   # 1
M2  = 0x02   # 2
M3  = 0x04   # 4
M4  = 0x08   # 8
E1  = 0x10   # 16 - encoder port 1 (independent from M1)
E2  = 0x20   # 32 - encoder port 2 (independent from M2)
ALL = 0x3F   # 63 - all ports

# Servo index
S1 = 0
S2 = 1
S3 = 2
S4 = 3

# Default I2C address
MDV2_DEFAULT_ADDRESS = 0x54

# Default encoder specs (OhStem encoder motor)
DEFAULT_PPR = 11
DEFAULT_GEAR_RATIO = 48 #34 DEFAULT
DEFAULT_TICKS_PER_REV = DEFAULT_PPR * 4 * DEFAULT_GEAR_RATIO  # 1496

# I2C config
I2C_RETRY = 3
I2C_DELAY = 0.005

# Register map
REG_RESET_ENC   = 0
REG_MOTOR_INDEX = 16
REG_MOTOR_BRAKE = 22
REG_REVERSE     = 23
REG_SERVO1      = 24
REG_SERVO2      = 26
REG_SERVO3      = 28
REG_SERVO4      = 30
REG_SERVOS      = [REG_SERVO1, REG_SERVO2, REG_SERVO3, REG_SERVO4]
REG_FW_VERSION  = 40
REG_WHO_AM_I    = 42
REG_BATTERY     = 43
REG_ENCODER1    = 44
REG_ENCODER2    = 48
REG_SPEED_E1    = 52
REG_SPEED_E2    = 54


def check_orc_hub(bus=1, address=MDV2_DEFAULT_ADDRESS):
    """
    Lightweight I2C probe — checks if the ORC Hub is connected
    without initializing the full driver or issuing any motor commands.

    Returns:
        (True, firmware_str)  if device found
        (False, error_msg)    if not
    """
    try:
        b = SMBus(bus)
        try:
            b.write_byte(address, REG_WHO_AM_I)
            who = b.read_byte(address)
            if who != address:
                return (False, f"Unexpected device 0x{who:02X} at 0x{address:02X}")
            # Read firmware version
            b.write_byte(address, REG_FW_VERSION)
            minor = b.read_byte(address)
            time.sleep(I2C_DELAY)
            b.write_byte(address, REG_FW_VERSION + 1)
            major = b.read_byte(address)
            return (True, f"{major}.{minor}")
        finally:
            b.close()
    except FileNotFoundError:
        return (False, "I2C bus not available")
    except PermissionError:
        return (False, "Permission denied — run with sudo or add user to i2c group")
    except (OSError, IOError) as e:
        return (False, str(e))


class MotorDriverV2:
    def __init__(self, bus=1, address=MDV2_DEFAULT_ADDRESS,
                 ppr=DEFAULT_PPR, gear_ratio=DEFAULT_GEAR_RATIO):
        """
        Connect to Motor Driver V2.

        Args:
            bus: I2C bus number (default 1)
            address: I2C address (default 0x54)
            ppr: encoder pulses per revolution (default 11)
            gear_ratio: motor gear ratio (default 34)
        """
        self._bus_num = bus
        self._addr = address
        self._bus = SMBus(bus)
        self._ticks_per_rev = ppr * 4 * gear_ratio

        who = self._read_8(REG_WHO_AM_I)
        if who != self._addr:
            self._bus.close()
            raise RuntimeError(
                f"Motor driver not found. Expected: 0x{address:02X}, got: 0x{who:02X}"
            )

        print(f"Motor Driver V2 OK | Bus: {bus} | Address: 0x{address:02X}")
        print(f"Firmware: {self.fw_version()} | Battery: {self.battery()}V")
        self.stop()

    def close(self):
        try:
            self.stop()
        except Exception:
            pass
        self._bus.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    # ==================== INFO ====================

    def fw_version(self):
        """Read firmware version. Returns string like '1.0'."""
        minor = self._read_8(REG_FW_VERSION)
        major = self._read_8(REG_FW_VERSION + 1)
        return f"{major}.{minor}"

    def battery(self):
        """Read battery voltage. Returns float like 11.8."""
        raw = self._read_8(REG_BATTERY)
        return round(raw / 10, 1)

    # ==================== DC MOTOR ====================

    def set_motors(self, motors, speed):
        """
        Run motor at given speed.

        Args:
            motors: M1, M2, M3, M4, E1, E2, or combine with |
            speed: -100 to 100 (negative = backward)

        Example:
            md.set_motors(M1, 50)       # M1 forward 50%
            md.set_motors(E1, -50)      # E1 backward 50%
            md.set_motors(M1 | M2, 80)  # M1 and M2 forward 80%
        """
        speed = max(min(100, int(speed)), -100)
        self._write_16_array(REG_MOTOR_INDEX, [motors, speed * 10])

    def stop(self, motors=ALL):
        """Stop motor (coast - slows down naturally)."""
        self.set_motors(motors, 0)

    def brake(self, motors=ALL):
        """Brake motor (lock - stops immediately)."""
        self._write_8(REG_MOTOR_BRAKE, motors)

    # ==================== SERVO ====================

    def set_servo(self, index, angle, max_angle=180):
        """
        Set servo angle.

        Args:
            index: S1=0, S2=1, S3=2, S4=3
            angle: 0 to max_angle

        Example:
            md.set_servo(S1, 90)    # S1 to 90 degrees
            md.set_servo(S2, 0)     # S2 to 0 degrees
        """
        if index < 0 or index > 3:
            raise ValueError("Servo index must be 0-3 (S1-S4)")
        angle = max(0, min(max_angle, angle))
        mapped = int(angle * 180 / max_angle)
        self._write_16(REG_SERVOS[index], mapped)

    # ==================== ENCODER SPEED ====================

    def get_speed(self, motor=ALL):
        """
        Read encoder speed (raw ticks).

        Args:
            motor: E1, E2, or ALL

        Returns:
            Raw speed value or list [speed_e1, speed_e2]
        """
        speeds = [0, 0]
        self._read_16_array(REG_SPEED_E1, speeds)

        if motor == ALL:
            return speeds
        elif motor == E1:
            return speeds[0]
        elif motor == E2:
            return speeds[1]
        return 0

    def get_speed_rpm(self, motor=ALL):
        """
        Read encoder speed in RPM.

        Args:
            motor: E1, E2, or ALL

        Returns:
            Speed in RPM (float) or list [rpm_e1, rpm_e2]

        Example:
            rpm = md.get_speed_rpm(E1)
            print(f"E1: {rpm} RPM")
        """
        raw = self.get_speed(motor)

        if isinstance(raw, list):
            return [round(r * 60 / self._ticks_per_rev, 1) for r in raw]
        else:
            return round(raw * 60 / self._ticks_per_rev, 1)

    # ==================== I2C LOW-LEVEL (with retry) ====================

    def _retry(self, func, *args):
        for attempt in range(I2C_RETRY):
            try:
                result = func(*args)
                time.sleep(I2C_DELAY)
                return result
            except OSError as e:
                if attempt < I2C_RETRY - 1:
                    time.sleep(0.01)
                else:
                    raise OSError(f"I2C error after {I2C_RETRY} retries: {e}")

    def _write_8(self, register, data):
        self._retry(self._bus.write_byte_data, self._addr, register, data & 0xFF)

    def _write_16(self, register, data):
        low = data & 0xFF
        high = (data >> 8) & 0xFF
        self._retry(self._bus.write_i2c_block_data, self._addr, register, [low, high])

    def _write_16_array(self, register, data):
        buffer = []
        for val in data:
            if val < 0:
                val = val + 65536
            buffer.append(val & 0xFF)
            buffer.append((val >> 8) & 0xFF)
        self._retry(self._bus.write_i2c_block_data, self._addr, register, buffer)

    def _read_8(self, register):
        def _do():
            self._bus.write_byte(self._addr, register)
            return self._bus.read_byte(self._addr)
        return self._retry(_do)

    def _read_16_array(self, register, result_array):
        length = len(result_array)
        def _do():
            return self._bus.read_i2c_block_data(self._addr, register, 2 * length)
        data = self._retry(_do)
        for i in range(length):
            raw = (data[2*i+1] << 8) | data[2*i]
            if raw & (1 << 15):
                result_array[i] = raw - (1 << 16)
            else:
                result_array[i] = raw


# ==================== QUICK TEST ====================

if __name__ == "__main__":
    import sys

    bus = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    try:
        md = MotorDriverV2(bus=1, gear_ratio=34)

        print("\n--- Test E1 speed at different power levels ---")
        input("Plug encoder motor into E1, press Enter...")

        for power in [30, 50, 70, 100]:
            print(f"\n  E1 at {power}%:")
            md.set_motors(E1, power)
            time.sleep(2)
            raw = md.get_speed(E1)
            rpm = md.get_speed_rpm(E1)
            print(f"    Raw ticks: {raw}")
            print(f"    RPM: {rpm}")
        md.stop(E1)
        time.sleep(1)

        print(f"\n  E1 at -50% (backward):")
        md.set_motors(E1, -50)
        time.sleep(2)
        raw = md.get_speed(E1)
        rpm = md.get_speed_rpm(E1)
        print(f"    Raw ticks: {raw}")
        print(f"    RPM: {rpm}")
        md.stop(E1)

        print("\n--- All tests done! ---")
        md.close()

    except RuntimeError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nStopped!")
        md.stop()
        md.close()