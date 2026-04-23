"""
Variable constructor functions for the AI Coding Lab Function Library.

These are trivial identity functions that cast inputs to the appropriate Python type.
Their primary purpose is to provide typed return values so the hint system's
type scanner (_scan_variable_types) can register variables with correct types.
"""


def Create_Text(value="Hello"):
    """Create a text string variable. Returns: Text (str)"""
    return str(value)


def Create_Number(value=0):
    """Create an integer variable. Returns: Number"""
    return int(value)


def Create_Decimal(value=0.0):
    """Create a floating-point variable. Returns: Number (float)"""
    return float(value)


def Create_Boolean(value=True):
    """Create a boolean variable. Returns: Boolean"""
    return bool(value)


def Create_List(value=None):
    """Create a list variable. Returns: List"""
    if value is None:
        return []
    return list(value)
