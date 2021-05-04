import datetime as dt
import logging
import re
from typing import Union, Set, Tuple

from processes.datetime_logic import str_to_date_dict, date_dict_to_str, datetime_to_str, DATE_SEPARATOR


class ValidationError(Exception):
    pass


def validate_int(value: Union[int, str], attribute_name: str):
    """
    Attempts to return int(value).
    If this fails, a ValidationError is raised with a descriptive error message.
    """
    try:
        return int(value)
    except ValueError:
        error_str = f'{attribute_name} provided ("{value}") is not an integer.'
        logging.error(error_str)
        # wouldbenice: log errors on error catching not within func (i.e. prevent logging if handled in except block).
        #  Revert do_logging function changes
        raise ValidationError(error_str)


def validate_length(value: str, min_len: int, max_len: int, attribute_name: str) -> str:
    """
    Verifies that string is between min and max characters (inclusive) in length.
    If this is not the case, a ValidationError is raised with a descriptive error message.
    """
    if min_len <= len(value) <= max_len:
        return value
    else:
        # :.20 shortens value to 20 chars
        error_str = f'{attribute_name} provided ("{value:.20}{"..." if len(value) > 20 else ""}")' \
                    f' is not between {min_len} and {max_len} characters long.'
        logging.error(error_str)
        raise ValidationError(error_str)


def validate_lookup(value: str, lookup_set: Set[str], attribute_name: str) -> str:
    """
    Validates whether value is in lookup_set.
    If this fails, a ValidationError is raised with a descriptive error message.
    """
    if value in lookup_set:
        return value
    else:
        error_str = f'{attribute_name} provided ("{value}") ' \
                    f'is not in the list of possible options: {", ".join(sorted(lookup_set))}'
        logging.error(error_str)
        raise ValidationError(error_str)


def validate_date(date_str: str, attribute_name: str, date_str_sep: str = DATE_SEPARATOR,
                  offset_range: Tuple[Union[float, int], ...] = (0, 0),
                  do_logging: bool = True) -> dt.datetime:
    """
    Validates a date - is it a valid date and does it fall within the given range?
    If this fails, a ValidationError is raised with a descriptive error message.

    :param date_str: a date str in the form 'YYYY(date_str_sep)MM(date_str_sep)DD'
    :param attribute_name: name of attribute which is being validated - for error message output
    :param date_str_sep: the separator to use when validating the date string (see above).
        Defaults to processes.datetime_logic.DATE_SEPARATOR
    :param offset_range: tuple of number of days into the future (-ve for past) *from which* to accept date
        and number of days into the future (-ve for past) *up to which* to accept date.
        Note that, therefore, the first number should ALWAYS be less than second.
        If omitted, then no range check is performed on the date.
    :param do_logging: if True, errors are logged to .log file, otherwise they are not (silent)
    """
    date_dict = str_to_date_dict(date_str, date_str_sep, do_logging=do_logging)

    try:
        valid_date = dt.datetime(**date_dict)
    except ValueError:
        error_str = f'Date information provided for {attribute_name} is ' \
                    f'logically invalid; i.e. the date specified ' \
                    f'({date_dict_to_str(date_dict, date_str_sep)}) ' \
                    f'does not exist'
        if do_logging:
            logging.error(error_str)
        raise ValidationError(error_str)

    if offset_range != (0, 0):
        now = dt.datetime.now()
        earliest_offset = dt.timedelta(days=offset_range[0])
        earliest_date = now + earliest_offset
        latest_offset = dt.timedelta(days=offset_range[1])
        latest_date = now + latest_offset
        if earliest_date < valid_date < latest_date:
            return valid_date
        else:
            error_str = f'Date information provided for {attribute_name} ' \
                        f'({date_dict_to_str(date_dict, date_str_sep)}) is ' \
                        f'not within accepted range from ' \
                        f'{datetime_to_str(earliest_date, date_str_sep)} to ' \
                        f'{datetime_to_str(latest_date, date_str_sep)}'
            logging.error(error_str)
            raise ValidationError(error_str)
    else:
        return valid_date


def validate_regex(value: str, pattern: str, attribute_name: str, pretty_format: str) -> str:
    """
    Validates whether value FULLY matches the regex pattern provided (use a r'' string).
    If this fails, a ValidationError is raised with a descriptive error message.
    This error uses pretty format for user convenience and the regex pattern provided.
    """
    if re.fullmatch(pattern, value):
        return value
    else:
        error_str = f'Value entered for {attribute_name} ("{value}"), does not match ' \
                    f'expected format: "{pretty_format}". (DEBUG - regex format: "{pattern}")'
        logging.error(error_str)
        raise ValidationError(error_str)
