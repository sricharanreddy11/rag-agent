from datetime import datetime
from dateutil.parser import parser


def format_datetime(date_format, scheduled_at):
    if not isinstance(scheduled_at, datetime):
        scheduled_at = parser().parse(timestr=scheduled_at)
    formatted_scheduled_at = scheduled_at.strftime(date_format)
    return formatted_scheduled_at


def convert_timestamp_to_utc(timestamp, format):
    my_datetime = datetime.utcfromtimestamp(timestamp)
    formatted_datetime = my_datetime.strftime(format)
    return formatted_datetime