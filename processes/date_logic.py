import datetime as dt
from typing import TypedDict


class DateInfoDict(TypedDict):
    year: int
    month: int
    day: int


def str_to_date_dict(date_str) -> DateInfoDict:
    """
    Converts date_str in format 'YYYY-MM-DD'
    to dictionary in format {'year': ???, 'month': ???, 'day': ???}
    """
    value_list = list(map(int, date_str.split('-')))
    return {'year': value_list[0], 'month': value_list[1], 'day': value_list[2]}


def datetime_to_str(datetime_obj: dt.datetime) -> str:
    """
    Converts datetime_obj into string of format 'YYYY-MM-DD' (10 chars long)
    """
    return f'{datetime_obj:%Y-%m-%d}'

# TODO: write CALCULATE END DATE function
# TODO: write GET WEEKDAY ABBREVIATION AND DATE PARTS function
# TODO: write GET UPCOMING EVENTS WITHIN TIMEFRAME function
