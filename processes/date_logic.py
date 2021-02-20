import datetime as dt
import logging
import re
from typing import TypedDict

DATE_SEPARATOR = '/'


class DateInfoDict(TypedDict):
    year: int
    month: int
    day: int


def str_to_date_dict(date_str, sep: str = DATE_SEPARATOR) -> DateInfoDict:
    """
    Converts date_str in format 'YYYY(sep)MM(sep)DD' (sep should be a 1-char str)
    to dictionary in format {'year': ???, 'month': ???, 'day': ???}
    If date_str is not in the required format,  a ValidationError is raised
    """
    match_str = '{year}{sep}{month}{sep}{day}'.format(year=r'\d{4}', month=r'\d{2}', day=r'\d{2}', sep=sep)
    if re.fullmatch(match_str, date_str):
        value_list = list(map(int, date_str.split(sep)))
        return DateInfoDict(year=value_list[0], month=value_list[1], day=value_list[2])
    else:
        error_str = f'Date provided ("{date_str}") is not in the form YYYY{sep}MM{sep}DD.'
        logging.error(error_str)

        from processes.validation import ValidationError  # only imported here to prevent circular import
        raise ValidationError(error_str)


def date_dict_to_str(date_dict: DateInfoDict, sep: str = DATE_SEPARATOR) -> str:
    """
    Converts date_dict in format {'year': ???, 'month': ???, 'day': ???}
    to string in format 'YYYY(sep)MM(sep)DD' (sep should be a 1-char str)
    """
    # :02 zero-pads int into 2 digits
    return f'{date_dict["year"]:04}{sep}{date_dict["month"]:02}{sep}{date_dict["day"]:02}'


def datetime_to_str(datetime_obj: dt.datetime = dt.datetime.now(), sep: str = DATE_SEPARATOR) -> str:
    """
    Converts datetime_obj into string of format 'YYYY(sep)MM(sep)DD'
    (always 10 chars long - sep should be a 1-char str)
    If no datetime_obj argument is provided, the current date is returned as a string instead.
    If datetime_obj is not a datetime obj, returns an empty string (used in file handling).
    """
    if datetime_obj:
        return f'{datetime_obj:%Y}{sep}{datetime_obj:%m}{sep}{datetime_obj:%d}'
    else:
        return ''


def calculate_end_date(time_offset: int, start_datetime_obj: dt.datetime = dt.datetime.now()) -> dt.datetime:
    """
    Returns start_datetime_obj (if given, otherwise, uses current datetime)
    + time_offset in days as a datetime obj
    """
    return start_datetime_obj + dt.timedelta(days=time_offset)

# TODO: write GET WEEKDAY ABBREVIATION AND DATE PARTS function
# TODO: write GET UPCOMING EVENTS WITHIN TIMEFRAME function
