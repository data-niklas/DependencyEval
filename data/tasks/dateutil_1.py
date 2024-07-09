from datetime import datetime
import dateutil

def current_datetime_in_local_timezone() -> datetime:
    """Return the current date and time in the local time zone.

    Returns:
        datetime: Current local date and time
    """
    return datetime.now(dateutil.tz.tzlocal())