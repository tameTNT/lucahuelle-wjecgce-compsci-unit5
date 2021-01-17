from copy import deepcopy
from pathlib import Path
from unittest import TestCase

from data_tables.data_handling import StudentLogin, StudentLoginTable
from processes.validation import ValidationError

TEST_STUDENT_SAVE_STRING = f'{"test name".ljust(30)}\\%s' \
                           f'{"test pwd hash".ljust(128)}\\%s{"1".ljust(4)}\n'


class TestStudentLogin(TestCase):
    test_student = StudentLogin('test name', 'test pwd hash', '01')

    def test_init(self):
        with self.assertRaises(ValidationError) as cm:
            StudentLogin('t', 'test pwd hash', 10)
        if 'username' not in str(cm.exception):
            self.fail('Error message text for string length validation incorrect.')

        with self.assertRaises(ValidationError) as cm:
            StudentLogin('test name', 'test pwd hash', 'test int')
        if 'user_id' not in str(cm.exception):
            self.fail('Error message text for int validation incorrect.')

        StudentLogin('test name', 'test pwd hash', 10)  # shouldn't fail

    def test_tabulate(self):
        tabulate_output = TestStudentLogin.test_student.tabulate()
        self.assertEqual(tabulate_output, TEST_STUDENT_SAVE_STRING,
                         'Tabulated output not in expected form')


class TestStudentLoginTable(TestCase):
    test_student = StudentLogin('test name', 'test pwd hash', '02')
    test_login_table = StudentLoginTable([test_student])

    def test_init(self):
        self.assertEqual(len(TestStudentLoginTable.test_login_table.rows), 1,
                         'StudentLoginTable missing a row')
        self.assertEqual(len(StudentLoginTable().rows), 0,
                         "StudentLoginTable contains data it shouldn't")

    def test_add_row(self):
        # deepcopy made so modifications don't affect other tests
        test_table = deepcopy(TestStudentLoginTable.test_login_table)
        with self.assertRaises(KeyError):
            test_table.add_row('test name', 'test pwd hash', '01')
        self.assertEqual(len(test_table.rows), 1,
                         'Row with non-unique primary key incorrectly added')

        test_table.add_row('test different name', 'test pwd hash', '01')
        self.assertEqual(len(test_table.rows), 2, 'Unique row incorrectly not added')

    def test_load_from_file(self):
        test_file_path = Path.cwd() / 'test_student_load.txt'
        with test_file_path.open('w+') as fobj:
            fobj.write(TEST_STUDENT_SAVE_STRING)

        test_table = StudentLoginTable()
        # noinspection PyTypeChecker
        test_table.load_from_file(test_file_path.open('r'))
        self.assertEqual(test_table.rows['test name'].user_id, 1,
                         'New row not correctly loaded from txt file')

    def test_save_to_file(self):
        test_file_path = Path.cwd() / 'test_student_save.txt'

        # noinspection PyTypeChecker
        TestStudentLoginTable.test_login_table.save_to_file(test_file_path.open('w+'))

        with test_file_path.open('r') as fobj:
            for line in fobj.readlines():
                self.assertEqual(line, TEST_STUDENT_SAVE_STRING.replace('1', '2'),
                                 'Held rows not correctly saved to txt file')


class TestDatabase(TestCase):
    # TODO: add Database tests
    def test_get_txt_database_dir(self):
        self.fail()

    def test_load_state_from_file(self):
        self.fail()

    def test_save_state_to_file(self):
        self.fail()
