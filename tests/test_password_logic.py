from unittest import TestCase

from processes import password_logic


class PasswordTest(TestCase):
    test_pwd_list = ('generic password', 'uniɕode password', '', '12.345')

    def test_hash_pwd_str(self):
        for pwd_str in self.test_pwd_list:
            hash_str = password_logic.hash_pwd_str(pwd_str)
            self.assertIsInstance(hash_str, str, 'Hash not a string')
            self.assertEqual(len(hash_str), 128, 'Hash incorrect length')

        with self.assertRaises(password_logic.PasswordLengthError):
            password_logic.hash_pwd_str('a' * 101)  # 101 is longer than the 100 pwd len limit
        password_logic.hash_pwd_str('a' * 100)  # on boundary of accepted pwd len range

    def test_verify_pwd_str(self):
        pwd_hash_list = map(password_logic.hash_pwd_str, self.test_pwd_list)
        for pwd_str, pwd_hash in zip(self.test_pwd_list, pwd_hash_list):
            self.assertTrue(password_logic.verify_pwd_str(pwd_str, pwd_hash),
                            'Password verification failed on correct match')

        # noinspection PyRedundantParentheses
        for pwd_str, pwd_hash in zip(('test') * len(self.test_pwd_list), pwd_hash_list):
            self.assertFalse(password_logic.verify_pwd_str(pwd_str, pwd_hash),
                             "Password verification should have failed but didn't")
