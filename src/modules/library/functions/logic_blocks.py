"""Logic utility blocks for the AI Coding Lab Function Library."""

import time


def Wait_Seconds(seconds=1.0):
    """Pause execution for the specified number of seconds."""
    time.sleep(float(seconds))


def Print_Message(message="Hello!"):
    """Print a message to the console output."""
    print(message)
