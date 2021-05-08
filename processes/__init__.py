import logging


def make_readable_name(var_name: str):
    """
    Returns a more user-friendly/readable version of var_name.

    e.g. user_id -> User id; year_group -> Year group
    """
    return ' '.join(var_name.split('_')).capitalize()


def shorten_string(s: str, max_length: int, no_multiline: bool = True):
    """
    If longer than max_length, truncates string s and appends '...'.
    Final string length will always be <= max_length.
    If no_multiline=True, returned string can only be maximum of one line
    """
    line_split = False
    if '\n' in s and no_multiline:
        s = s.split('\n', maxsplit=1)[0]  # reduces s to just one line
        line_split = True

    if len(s) > max_length:
        return s[:max_length - 3] + '...'

    # if s was more than one line long but shorter than max_length
    elif line_split:
        return s + '...'

    else:
        return s


def make_multiline_string(s: str, max_line_length: int):
    """
    Converts string s into a string with \n separators that ensure
    that each line of text is no longer than line_length characters long.
    Line breaks only occur on spaces, not within words.
    If a word is longer than the max_line_length, the word is abbreviated with
    a '...'
    """
    words = s.split(' ')
    final_string = ''
    current_line_length = 0
    for w in words:
        word_length = len(w)

        if current_line_length + word_length > max_line_length:
            if current_line_length == 0:  # no words on this line yet
                logging.debug(f'First word in string longer than permitted line length ({max_line_length}). '
                              f'Trimming word.')
                w = shorten_string(w, max_line_length)
            else:
                final_string = final_string[:-1] + '\n'  # [:-1] removes trailing space
                current_line_length = 0

        current_line_length += word_length
        final_string += w + ' '

    return final_string[:-1]  # removes trailing space
