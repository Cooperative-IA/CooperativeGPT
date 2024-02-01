from datetime import datetime

def str_to_timestamp(date: str, date_format: str) -> int:
    """Converts a string date to a timestamp.

    Args:
        date (str): Date in string format.
        dateformat (str): Date format.

    Returns:
        int: Timestamp.
    """
    if date is None:
        return 0
    return int(datetime.strptime(date, date_format).timestamp())