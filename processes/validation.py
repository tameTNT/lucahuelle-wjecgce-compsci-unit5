import datetime as dt
import logging
import re
from typing import Union, Set

from processes.date_logic import str_to_date_dict


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
        logging.error(error_str)  # todo: log errors on error catching not within func
        raise ValidationError(error_str)


def validate_length(value: str, min_len: int, max_len: int, attribute_name: str) -> str:
    """
    Verifies that string is between min and max characters (inclusive) in length.
    If this is not the case, a ValidationError is raised with a descriptive error message.
    """
    if min_len <= len(value) <= max_len:
        return value
    else:
        error_str = f'{attribute_name} provided ("{value}") ' \
                    f'is not between {min_len} and {max_len} characters long.'
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
                    f'is not in the list of possible options: {", ".join(lookup_set)}'
        logging.error(error_str)
        raise ValidationError(error_str)


def validate_date(date_str: str, earliest_offset: Union[float, int],
                  latest_offset: Union[float, int], attribute_name: str) -> dt.datetime:
    """
    Validates a date - is it a valid date and does it fall within the given range?
    If this fails, a ValidationError is raised with a descriptive error message.

    :param date_str: A date str in the form 'YYYY-MM-DD'
    :param earliest_offset: Number of days into the future (-ve for past) from which to accept date
    :param latest_offset: Number of days into the future (-ve for past) up to which to accept date.
        Note that, therefore, earliest_offset should ALWAYS be less than latest_offset
    :param attribute_name: Name of attribute which is being validated - for error message output
    """
    date_dict = str_to_date_dict(date_str)
    try:
        valid_date = dt.datetime(**date_dict)
    except ValueError:
        error_str = f'Date information provided for {attribute_name} is ' \
                    f'logically invalid; i.e. the date specified ' \
                    f'({date_dict["year"]}-{date_dict["month"]}-{date_dict["day"]}) ' \
                    f'does not exist'
        logging.error(error_str)
        raise ValidationError(error_str)

    now = dt.datetime.now()
    earliest_offset = dt.timedelta(days=earliest_offset)
    earliest_date = now + earliest_offset
    latest_offset = dt.timedelta(days=latest_offset)
    latest_date = now + latest_offset
    if earliest_date < valid_date < latest_date:
        return valid_date
    else:
        error_str = f'Date information provided for {attribute_name} ' \
                    f'({date_dict["year"]}-{date_dict["month"]}-{date_dict["day"]}) is ' \
                    f'not within accepted range from ' \
                    f'{earliest_date:%Y-%m-%d} to {latest_date:%Y-%m-%d}'
        logging.error(error_str)
        raise ValidationError(error_str)


def validate_regex(value: str, pattern: str, attribute_name: str) -> str:
    """
    Validates whether value FULLY matches the regex pattern provided.
    If this fails, a ValidationError is raised with a descriptive error message.
    """
    if re.fullmatch(pattern, value):
        return value
    else:
        error_str = f'Value entered for {attribute_name} ("{value}"), does not match ' \
                    f'expected (regex) pattern: {pattern}'
        logging.error(error_str)
        raise ValidationError(error_str)
