from unittest import TestCase
from processes import passwords


class PasswordTest(TestCase):
    def test_hash_password(self):
        if passwords.hash_password():
            pass
        else:
            self.fail()

    def test_verify_password(self):
        if passwords.verify_password():
            pass
        else:
            self.fail()
