from src.modules.library.functions.robotics import DC_Stop
from src.modules.library.functions.robotics import DC_Run
while True:
	DC_Run(pin = 'M1', speed = 100, time_ms = 2000)