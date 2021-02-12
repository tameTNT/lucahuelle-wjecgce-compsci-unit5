import datetime as dt
import logging
import re
from typing import TypedDict


class DateInfoDict(TypedDict):
    year: int
    month: int
    day: int


def str_to_date_dict(date_str) -> DateInfoDict:
    """
    Converts date_str in format 'YYYY-MM-DD'
    to dictionary in format {'year': ???, 'month': ???, 'day': ???}
    If date_str is not in the required format,  a ValidationError is raised
    """
    if re.fullmatch('\d{4}-\d{2}-\d{2}', date_str):
        value_list = list(map(int, date_str.split('-')))
        return DateInfoDict(year=value_list[0], month=value_list[1], day=value_list[2])
    else:
        error_str = f'Date provided ("{date_str}") is not in the form YYYY-MM-DD.'
        logging.error(error_str)

        from processes.validation import ValidationError
        raise ValidationError(error_str)


def datetime_to_str(datetime_obj: dt.datetime = dt.datetime.now()) -> str:
    """
    Converts datetime_obj into string of format 'YYYY-MM-DD' (10 chars long)
    But only if datetime_obj is a datetime obj. Otherwise, returns an empty string.
    If no argument is provided, the current date is returned as a string.
    """
    if datetime_obj:
        return f'{datetime_obj:%Y-%m-%d}'
    else:
        return ''

# TODO: write CALCULATE END DATE function
# TODO: write GET WEEKDAY ABBREVIATION AND DATE PARTS function
# TODO: write GET UPCOMING EVENTS WITHIN TIMEFRAME function
