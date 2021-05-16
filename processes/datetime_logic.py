import datetime as dt
import logging
import re
from typing import TypedDict, Set, Union

from data_tables import SECTION_NAME_MAPPING

DATE_SEPARATOR = '/'


class DateInfoDict(TypedDict):
    year: int
    month: int
    day: int


def str_to_date_dict(date_str, sep: str = DATE_SEPARATOR, do_logging: bool = True) -> DateInfoDict:
    """
    Converts date_str in format 'YYYY(sep)MM(sep)DD' (sep should be a 1-char str)
    to dictionary in format {'year': ???, 'month': ???, 'day': ???}
    If date_str is not in the required format, a ValidationError is raised.
    If do_logging is True, errors are logged to .log file also, otherwise they are not (silent)
    """
    match_str = '{year}{sep}{month}{sep}{day}'.format(year=r'\d{4}', month=r'\d{2}', day=r'\d{2}', sep=sep)
    if re.fullmatch(match_str, date_str):
        value_list = list(map(int, date_str.split(sep)))
        return DateInfoDict(year=value_list[0], month=value_list[1], day=value_list[2])
    else:
        error_str = f'Date provided ("{date_str}") is not in the form YYYY{sep}MM{sep}DD.'
        if do_logging:
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


def datetime_to_str(datetime_obj: Union[dt.datetime, dt.date] = dt.datetime.now(), sep: str = DATE_SEPARATOR) -> str:
    """
    Converts datetime_obj into string of format 'YYYY(sep)MM(sep)DD'
    (always 10 chars long - sep should be a 1-char str).
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


def date_in_past(date: dt.datetime) -> bool:
    """
    Returns True is date is in the past, False otherwise
    """
    return date < dt.datetime.now()


def get_possible_timeframes(level: str, section_type: str,
                            student_obj, section_table) -> Set[int]:
    """
    Returns a set of the potential timeframes still available for the student for the section specified.
    Based on the DofE structure shown here: https://images.app.goo.gl/xCqbRvrhF3h6YLGy8

    :param level: the DofE level of the student (one of 'bronze', 'silver' or 'gold').
        Determines what timeframe choices are initially available
    :param section_type: one of 'vol', 'skill' or 'phys' - determines which timeframe set is returned.
    :param student_obj: a student obj (data_tables.data_handling.Student)
        to read any associated/already started section info from
    :param section_table: the section table (data_tables.data_handling.SectionTable)
        to read from (see student_obj)
    :return: A set of timescale strings (3 and/or 6 and/or 12) still available to the student
    """
    set_choices = dict()
    for st in SECTION_NAME_MAPPING.keys():
        section_id = student_obj.__getattribute__(f'{st}_info_id')
        if section_id:  # section has been started
            set_choices[st] = int(section_table.row_dict[section_id].activity_timescale) // 30
        else:
            set_choices[st] = None

    if level == 'bronze':
        if 6 in set_choices.values():  # one section already on 6 months
            return {3}  # only choice left is 3 months
        else:
            return {3, 6}

    elif level == 'silver':
        if section_type == 'vol':
            return {6}
        elif section_type == 'skill':
            if set_choices['phys'] == 3:
                return {6}
            elif set_choices['phys'] == 6:
                return {3}
            else:
                return {3, 6}
        elif section_type == 'phys':
            if set_choices['skill'] == 3:
                return {6}
            elif set_choices['skill'] == 6:
                return {3}
            else:
                return {3, 6}

    elif level == 'gold':
        if section_type == 'vol':
            return {12}
        elif section_type == 'skill':
            if set_choices['phys'] == 6:
                return {12}
            elif set_choices['phys'] == 12:
                return {6}
            else:
                return {6, 12}
        elif section_type == 'phys':
            if set_choices['skill'] == 6:
                return {12}
            elif set_choices['skill'] == 12:
                return {6}
            else:
                return {6, 12}

# todo: write GET WEEKDAY ABBREVIATION AND DATE PARTS function
# todo: write GET UPCOMING EVENTS WITHIN TIMEFRAME function
