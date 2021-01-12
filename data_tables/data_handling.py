import logging  # logging functionality
from io import TextIOWrapper  # type hints in function definitions
from pathlib import Path  # file handling
from typing import Iterable, Optional  # type hints in function definitions

from processes import password_logic


class RowClass:
    """
    Base class for row classes/data objects to be stored within tables.
    """

    def __repr__(self) -> str:
        """
        Returns a string representation of object in form:
        '<ClassName object key_field={self.key_field!r}> field_2={self.field_2!r} ...'
        """
        pass

    def tabulate(self) -> str:
        """
        Returns a one line string of the object's data tabulated for text storage
        """
        pass


class TableClass:
    """
    Base class for table classes which are then stored within a Database object.
    """

    def __init__(self):
        self.rows = dict()  # objects are stored in dictionary using primary key/field as key

    def __repr__(self) -> str:
        """
        Returns a string representation of object in form:
        '<ClassName object with {len(self.rows)} row(s) of ClassRow objects>'
        """
        pass

    def add_row(self, new_obj=None, *args):
        """
        Add a new row/object to table.
        If an object is provided, that is added directly.
        Otherwise, a new object is initialised (using args) and then added.
        Raises KeyError if attempting to add an object with a non-unique key field.
        """
        pass

    def load_from_file(self, txt_file: TextIOWrapper):
        """
        Given the output from an open() method, populates self with data from lines of text file
        """
        pass

    def save_to_file(self, txt_file: TextIOWrapper):
        """
        Given the file output from an open('w') method, writes to the file the data within self
        """
        pass


# TODO: write tests for classes and methods (including int validation)
class StudentLogin(RowClass):
    def __init__(self, username: str, plain_password: str, user_id: int):
        self.username = username
        self.password = password_logic.hash_pwd_str(plain_password)  # pwd not stored in plaintext
        logging.debug('Password hashed successfully')

        # user_id should be int but when parsed from txt file will be str so needs conversion
        self.user_id = int(user_id)
        logging.info('New StudentLogin object successfully created')

    def __repr__(self):
        # only first 10 chars of hash shown
        return f'<StudentLogin object username={self.username!r} ' \
               f'password={self.password[:10] + "..."!r} user_id={self.user_id!r}>'

    def tabulate(self):
        return_string = ''
        return_string += self.username.ljust(30) + r'\%s'
        return_string += self.password.ljust(128) + r'\%s'
        return_string += str(self.user_id).ljust(4)
        return return_string + '\n'


class StudentLoginTable(TableClass):
    def __init__(self, start_table: Optional[Iterable[StudentLogin]] = tuple()):
        """
        :param start_table: (optional) an iterable of StudentLogin objects to populate self with
        """
        super().__init__()
        if start_table:  # if an iterable of objects has been provided
            for student_obj in start_table:
                self.add_row(student_obj)

            logging.info('StudentLoginTable object successfully populated from iterable argument')

    def __repr__(self):
        return f'<StudentLoginTable object with {len(self.rows)} row(s) of StudentLogin objects>'

    def add_row(self, new_student_obj: StudentLogin = None, *args):
        # if no object passed to function then initialisation arguments have been passed instead
        if not object:
            new_student_obj = StudentLogin(*args)

        primary_key = new_student_obj.username
        if primary_key not in self.rows.keys():
            self.rows[primary_key] = new_student_obj
        else:
            raise KeyError('You tried to add an object to the table with a non-unique primary key')

    def load_from_file(self, txt_file: TextIOWrapper):
        for row in txt_file.readlines():
            obj_info = list()

            padded_fields = row.split(r'\%s')  # split line/row by separator
            for field in padded_fields:
                obj_info.append(field.strip())  # remove padding whitespace and newlines

            self.add_row(*obj_info)  # add new row/StudentLogin object to table

        logging.info('StudentLoginTable object successfully populated from file')

    def save_to_file(self, txt_file: TextIOWrapper):
        for student_login_obj in self.rows.values():
            txt_file.write(student_login_obj.tabulate())

        logging.info('StudentLoginTable object successfully saved to file')


# class Section(RowClass):
#     def __init__(self, activity_status):
#         self._activity_status = activity_status
#
#     @property
#     def activity_status(self):
#         return self._activity_status
#
#     @activity_status.setter
#     def activity_status(self, new_value):
#         return
#
#     @activity_status.getter
#     def activity_status(self):
#         return 'blah'
#
#
# class SectionTable(TableClass):
#     pass


    @activity_status.getter
    def activity_status(self):
        return 'blah'


class SectionTable:
    def __init__(self):
        pass

    def load_from_file(self):
        pass
