import binascii
import hashlib
import os


class PasswordLengthError(Exception):
    def __init__(self, password_len, message='provided_password string argument too long'):
        """
        Exception raised for when provided_password string is too long.
        :param password_len: length of provided_password string
        :param message: error message explanation to be raised
        """
        self.password_len = password_len
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.password_len} > 100 : {self.message}'


# By CC attribution, the functions for hashing and verifying password are based on code at
# https://www.vitoshacademy.com/hashing-passwords-in-python/
def hash_pwd_str(provided_password: str) -> str:
    """
    Returns a secure hash of the provided_password string to be stored.
    """
    if len(provided_password) > 100:
        raise PasswordLengthError(len(provided_password))

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


def enforce_strength(provided_password: str) -> bool:
    """
    Returns a boolean of whether provided_password matches the program's strength requirements
    """
    # TODO: write enforce pwd strength function
    return bool(provided_password)
