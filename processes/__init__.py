def make_readable_name(var_name: str):
    """
    Returns a more user-friendly/readable version of var_name.

    e.g. user_id -> User id; year_group -> Year group
    """
    return ' '.join(var_name.split('_')).capitalize()


def shorten_string(s: str, max_length: int):
    """
    If longer than max_length, truncates string s and appends '...'
    """
    if len(s) > max_length:
        return s[:max_length - 3] + '...'
    else:
        return s
