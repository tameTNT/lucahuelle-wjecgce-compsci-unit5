from unittest import TestCase

from processes import passwords


class PasswordTest(TestCase):
    test_pwd_list = ('generic password', 'uniɕode password', '', '12.345')

    def test_hash_password(self):
        for pwd_str in self.test_pwd_list:
            hash_str = passwords.hash_pwd_str(pwd_str)
            self.assertIsInstance(hash_str, str, 'Hash not a string')
            self.assertEqual(len(hash_str), 192, 'Hash incorrect length')

    def test_verify_password(self):
        pwd_hash_list = map(passwords.hash_pwd_str, self.test_pwd_list)
        for pwd_str, pwd_hash in zip(self.test_pwd_list, pwd_hash_list):
            self.assertTrue(passwords.verify_pwd_str(pwd_str, pwd_hash),
                            'Password verification failed on correct match')

        for pwd_str, pwd_hash in zip(('test') * len(self.test_pwd_list), pwd_hash_list):
            self.assertFalse(passwords.verify_pwd_str(pwd_str, pwd_hash),
                             "Password verification should have failed but didn't")
