import binascii
import hashlib
import os


# By CC attribution, the functions for hashing and verifying password are based on code at
# https://www.vitoshacademy.com/hashing-passwords-in-python/
def hash_pwd_str(provided_password: str) -> str:
    """
    Returns a secure hash of the provided_password string to be stored.
    """
    random_bytes = os.urandom(60)
    salt = hashlib.sha256(random_bytes).hexdigest().encode('ascii')

    provided_password = provided_password.encode('utf-8')
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password, salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_pwd_str(provided_password: str, stored_hash: str) -> bool:
    """
    Returns a boolean of whether provided_password matches the stored password/hash
    """
    salt = stored_hash[:64].encode('ascii')
    stored_password = stored_hash[64:]
    provided_password = provided_password.encode('utf-8')
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password, salt, 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def enforce_strength(provided_password: str) -> bool:
    """
    Returns a boolean of whether provided_password matches the program's strength requirements
    """
    # TODO: write function
    return bool(provided_password)
