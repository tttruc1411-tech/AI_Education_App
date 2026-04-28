"""Logic utility blocks for the AI Coding Lab Function Library."""

import time


def Wait_Seconds(seconds=1.0):
    """Pause execution for the specified number of seconds."""
    time.sleep(float(seconds))


def Print_Message(message="Hello!"):
    """Print a message to the console output."""
    print(message)

from datetime import datetime


def Get_Timestamp():
    """
    Return the current date and time as a formatted string.

    Returns
    -------
    str
        Current timestamp in 'YYYY-MM-DD HH:MM:SS' format, or '' on failure.
    """
    try:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"[Logic] Error in Get_Timestamp: {e}")
        return ""


def Compare_Values(value1, value2):
    """
    Compare two values for equality.

    Parameters
    ----------
    value1 : any
        First value.
    value2 : any
        Second value.

    Returns
    -------
    bool
        True if the values are equal, False otherwise.
    """
    try:
        return bool(value1 == value2)
    except Exception as e:
        print(f"[Logic] Error in Compare_Values: {e}")
        return False
