import binascii
import hashlib
import logging
import os
import string
from typing import Dict


class PasswordError(Exception):
    def __init__(self, error_type: str):
        """
        Exception raised for when a password string doesn't meet requirements.

        :param error_type: one of the following options:
            'length', 'one_lower', 'one_upper', 'one_digit'
        """
        self.message = ''

        if error_type == 'length':
            self.message = 'Password must be between 6 and 100 characters long'

        elif error_type == 'one_lower':
            self.message = 'Password must contain at least one lowercase letter'

        elif error_type == 'one_upper':
            self.message = 'Password must contain at least one uppercase letter'

        elif error_type == 'one_digit':
            self.message = 'Password must contain at least one number'

        logging.error(str(self))
        super().__init__(self.message)


# Functions for hashing and verifying password adapted from code at
# https://www.vitoshacademy.com/hashing-passwords-in-python/
def hash_pwd_str(provided_password: str) -> str:
    """
    Returns a 128 char hashed str of the provided_password string to be stored.
    """
    if len(provided_password) > 100:
        raise PasswordError('length')

    random_bytes = os.urandom(60)
    salt = hashlib.sha256(random_bytes).hexdigest().encode('ascii')

    provided_password = provided_password.encode('utf-8')
    # 100000 iterations of sha256 recommended at
    # https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password, salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_pwd_str(provided_password: str, stored_hash: str) -> bool:
    """
    Returns a boolean of whether provided_password matches the stored password/hash
    """
    salt = stored_hash[:64].encode('ascii')
    stored_password = stored_hash[64:]
    provided_password = provided_password.encode('utf-8')
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password, salt, 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def enforce_strength(provided_password: str, quiet: bool = False) -> (bool, Dict[str, bool]):
    """
    Returns a tuple containing:
        - boolean of whether provided_password meets the program's strength requirements
        - dictionary of bool specifying which tests passed: 'length', 'one_lower', 'one_upper', 'one_digit'
    :param provided_password: password string to test
    :param quiet: If True, no PasswordErrors are raised on test failure
    """
    tests_passed = {
        'length': True,
        'one_lower': True,
        'one_upper': True,
        'one_digit': True,
    }

    if not (6 <= len(provided_password) <= 100):
        tests_passed['length'] = False

        if not quiet:
            raise PasswordError('length')

    string_tests = {
        'one_lower': set(string.ascii_lowercase),
        'one_upper': set(string.ascii_uppercase),
        'one_digit': set(string.digits),
    }
    for test_name, req_char_set in string_tests.items():
        if not set(provided_password).intersection(req_char_set):
            # no overlap/intersection between sets
            # i.e. there are no chars from req_char_set in provided_password
            tests_passed[test_name] = False

            if not quiet:
                raise PasswordError(test_name)

    all_passed = all(tests_passed.values())  # all() is only True if all tests passed

    return all_passed, tests_passed
