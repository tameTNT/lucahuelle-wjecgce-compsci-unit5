def make_readable_name(var_name: str):
    """
    Returns a more user-friendly/readable version of var_name.

    e.g. user_id -> User id; year_group -> Year group
    """
    return ' '.join(var_name.split('_')).capitalize()
