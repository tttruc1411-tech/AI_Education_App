"""
Motor Brain Layer - Jetson Orin Nano Super
High-level motor control with async support.
Works on top of motor_driver_v2.py (the Translator).

Setup:
    from motor_driver_v2 import MotorDriverV2, M1, M2, E1, E2
    from motor import DCMotor, STOP, BRAKE

    md = MotorDriverV2(bus=1)

    # Encoder motor on E1 port (can read speed)
    motor_left = DCMotor(md, E1)
    motor_left.set_encoder()

    # Normal motor on M1 port (no speed reading)
    motor_extra = DCMotor(md, M1)

Functions:
    motor.run(50)                                   # run forward 50%
    motor.run(-50)                                  # run backward 50%
    motor.stop()                                    # stop (coast)
    motor.brake()                                   # brake (lock)
    motor.speed()                                   # read speed in RPM (encoder only)
    await motor.run_time(50, 2000)                  # run 50% for 2 seconds
    await motor.run_time(50, 2000, then=BRAKE)      # run then brake
    await motor.run_until_stalled(50)               # run until blocked

Run 2 motors at same time:
    async def main():
        await asyncio.gather(
            motor_left.run_time(50, 2000),
            motor_right.run_time(50, 2000),
        )

    asyncio.run(main())
"""

import asyncio
import time

# Action after run completes
STOP = 0
BRAKE = 1
HOLD = 2

# Default encoder config (change to match your motor)
DEFAULT_PPR = 11         # pulses per revolution
DEFAULT_GEAR_RATIO = 34  # gear ratio
DEFAULT_RPM = 250        # max RPM


class DCMotor:
    def __init__(self, driver, port, reversed=False):
        """
        Create a motor object.

        Args:
            driver: MotorDriverV2 object
            port: M1, M2, M3, M4, E1, or E2
            reversed: True to reverse direction

        Example:
            motor_left = DCMotor(md, E1)              # encoder motor
            motor_right = DCMotor(md, E2, reversed=True)
            motor_extra = DCMotor(md, M1)             # normal motor
        """
        self.driver = driver
        self.port = port

        if reversed:
            self._reversed = -1
        else:
            self._reversed = 1

        # Encoder config
        self._encoder_enabled = False
        self._rpm = 0
        self._ppr = 0
        self._gear_ratio = 0
        self._ticks_per_rev = 0
        self._max_pps = 0

        # Stall detection config
        self._stalled_speed = 0.05   # less than 5% of max speed = stalled
        self._stalled_time = 1000    # must be stalled for 1 second (ms)

    def set_encoder(self, rpm=DEFAULT_RPM, ppr=DEFAULT_PPR, gear_ratio=DEFAULT_GEAR_RATIO):
        """
        Set encoder specs for speed reading.
        Only needed for E1/E2 ports.

        Args:
            rpm: max RPM of motor (default 250)
            ppr: pulses per revolution (default 11)
            gear_ratio: gear ratio (default 34)

        Example:
            motor_left.set_encoder()                          # use defaults
            motor_left.set_encoder(rpm=300, ppr=11, gear_ratio=48)  # custom
        """
        if rpm <= 0 or ppr <= 0 or gear_ratio <= 0:
            raise ValueError("rpm, ppr, gear_ratio must be > 0")

        self._encoder_enabled = True
        self._rpm = rpm
        self._ppr = ppr
        self._gear_ratio = gear_ratio
        self._ticks_per_rev = ppr * 4 * gear_ratio
        self._max_pps = rpm * ppr * 4 * gear_ratio / 60

    def set_stall_config(self, speed_threshold=0.05, time_ms=1000):
        """
        Set stall detection sensitivity.

        Args:
            speed_threshold: fraction of max speed (default 0.05 = 5%)
            time_ms: how long before stall is confirmed (default 1000ms)
        """
        self._stalled_speed = speed_threshold
        self._stalled_time = time_ms

    def reverse(self):
        """Reverse motor direction."""
        self._reversed *= -1

    # ==================== BASIC CONTROL ====================

    def run(self, speed):
        """
        Run motor continuously. Runs until you call stop() or brake().

        Args:
            speed: -100 to 100 (negative = backward)

        Example:
            motor.run(50)    # forward 50%
            motor.run(-50)   # backward 50%
        """
        speed = max(min(100, int(speed)), -100)
        self.driver.set_motors(self.port, speed * self._reversed)

    def stop(self):
        """Stop motor (coast - slows down naturally)."""
        self.driver.stop(self.port)

    def brake(self):
        """Brake motor (lock - stops immediately)."""
        self.driver.brake(self.port)

    # ==================== ASYNC CONTROL ====================

    async def run_time(self, speed, time_ms, then=STOP):
        """
        Run motor for a specific time.

        Args:
            speed: -100 to 100
            time_ms: time in milliseconds
            then: STOP, BRAKE, or HOLD

        Example:
            await motor.run_time(50, 2000)              # 2 seconds then stop
            await motor.run_time(50, 2000, then=BRAKE)  # 2 seconds then brake
        """
        if time_ms <= 0:
            return

        self.run(speed)
        start = time.time()

        while True:
            elapsed = (time.time() - start) * 1000
            if elapsed >= time_ms:
                break
            await asyncio.sleep(0.01)

        if then == STOP:
            self.stop()
        elif then == BRAKE:
            self.brake()

    async def run_until_stalled(self, speed, then=STOP):
        """
        Run motor until it is blocked/stalled.
        Requires encoder (E1/E2). Call set_encoder() first.

        Args:
            speed: -100 to 100
            then: STOP or BRAKE

        Example:
            motor.set_encoder()
            await motor.run_until_stalled(70)
        """
        if not self._encoder_enabled:
            print("Warning: encoder not set. Call set_encoder() first.")
            return

        threshold = int(self._max_pps * self._stalled_speed * 60 / self._ticks_per_rev)
        stalled_start = 0
        stalled = False

        self.run(speed)

        while True:
            current_speed = abs(self.speed())

            if current_speed <= threshold:
                if not stalled:
                    stalled = True
                    stalled_start = time.time()
            else:
                stalled = False

            if stalled and (time.time() - stalled_start) * 1000 > self._stalled_time:
                break

            await asyncio.sleep(0.2)

        if then == STOP:
            self.stop()
        elif then == BRAKE:
            self.brake()

    # ==================== SPEED READING ====================

    def speed(self):
        """
        Read motor speed in RPM.
        Requires encoder (E1/E2). Call set_encoder() first.

        Returns:
            Speed in RPM (float)

        Example:
            motor.set_encoder()
            motor.run(50)
            time.sleep(1)
            print(motor.speed())  # e.g. 120.5 RPM
        """
        if not self._encoder_enabled:
            print("Warning: encoder not set. Call set_encoder() first.")
            return 0

        raw = self.driver.get_speed(self.port)
        rpm = round(raw * 60 / self._ticks_per_rev, 1)
        return rpm


# ==================== QUICK TEST ====================

if __name__ == "__main__":
    import sys
    from motor_driver_v2 import MotorDriverV2, M1, M2, E1, E2, S1

    bus = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    async def main():
        md = MotorDriverV2(bus=bus)

        # Create motor on E1 port (encoder motor)
        m_e1 = DCMotor(md, E1)
        m_e1.set_encoder()

        # Create motor on M1 port (normal motor)
        m_m1 = DCMotor(md, M1)

        try:
            # Test 1: E1 run_time
            print("\n--- Test: E1 forward 40% for 2 seconds ---")
            await m_e1.run_time(40, 2000)
            await asyncio.sleep(1)

            # Test 2: E1 read speed
            print("\n--- Test: E1 read speed ---")
            m_e1.run(50)
            await asyncio.sleep(1)
            print(f"  E1 speed: {m_e1.speed()} RPM")
            m_e1.stop()
            await asyncio.sleep(1)

            # Test 3: M1 run_time
            print("\n--- Test: M1 forward 40% for 2 seconds ---")
            await m_m1.run_time(40, 2000)
            await asyncio.sleep(1)

            # Test 4: E1 run_until_stalled
            print("\n--- Test: E1 run until stalled ---")
            print("  (hold the motor shaft to trigger stall)")
            await m_e1.run_until_stalled(50)
            print("  Stall detected!")

            print("\nAll tests done!")
            md.close()

        except KeyboardInterrupt:
            print("\nStopped!")
            m_e1.stop()
            m_m1.stop()
            md.close()

    asyncio.run(main())