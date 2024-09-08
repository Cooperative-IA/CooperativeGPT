from datetime import datetime

def str_to_timestamp(date: str|None) -> int:
    """Converts a string date to a timestamp.

    Args:
        date (str|None): Date in string format.

    Returns:
        int: Timestamp.
    """
    if date is None:
        return 0
    return int(date.split()[1])