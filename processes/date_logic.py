from typing import TypedDict


class DateInfoDict(TypedDict):
    year: int
    month: int
    day: int


def convert_str_to_dict(date_str) -> DateInfoDict:
    """
    Converts date_str in format 'YEAR-MONTH-DAY'
    to dictionary in format {'year': ???, 'month': ???, 'day': ???}
    """
    # TODO: when saving dates to file insert dashes
    value_list = list(map(int, date_str.split('-')))
    return {'year': value_list[0], 'month': value_list[1], 'day': value_list[2]}

# TODO: write CALCULATE END DATE function
# TODO: write GET WEEKDAY ABBREVIATION AND DATE PARTS function
# TODO: write GET UPCOMING EVENTS WITHIN TIMEFRAME function
