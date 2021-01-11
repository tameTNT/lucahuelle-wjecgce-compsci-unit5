import logging
from io import TextIOWrapper
from typing import Iterable, Optional


# TODO: write tests for classes and methods (including int validation)
class StudentLogin:
    def __init__(self, username: str, password: str, user_id: int):
        self.username = username
        self.password = password
        # user_id should be int but when parsed from txt file will be str so needs conversion
        self.user_id = int(user_id)
        logging.info('New StudentLogin object successfully created')

    def __repr__(self):
        return f'<StudentLogin object username={self.username!r} ' \
               f'password={self.password!r} user_id={self.user_id!r}>'

    def tabulate(self) -> str:
        """
        Returns a one line string of the object's data tabulated for text storage
        """
        return_string = ''
        return_string += self.username.ljust(30) + r'\%s'
        return_string += self.password.ljust(128) + r'\%s'
        return_string += str(self.user_id).ljust(4)
        return return_string + '\n'


class StudentLoginTable:
    def __init__(self, start_table: Optional[Iterable[StudentLogin]] = tuple()):
        """
        :param start_table: (optional) an iterable of StudentLogin objects to populate self with
        """
        self.rows = dict()
        if start_table:  # if an iterable of objects has been provided
            for student_obj in start_table:
                # objects stored in dictionary using primary key/field as key
                self.rows[student_obj.username] = student_obj

            logging.info('StudentLoginTable object successfully populated from iterable argument')

    def __repr__(self):
        return f'<StudentLoginTable object with {len(self.rows)} row(s) of StudentLogin objects>'

    def load_from_file(self, txt_file: TextIOWrapper):
        """
        Given the output from an open() method, populates self with data from lines of text file
        """
        for row in txt_file.readlines():
            obj_info = list()

            padded_fields = row.split(r'\%s')  # split line/row by separator
            for field in padded_fields:
                obj_info.append(field.strip())  # remove padding whitespace and newlines

            new_student_obj = StudentLogin(*obj_info)
            self.rows[new_student_obj.username] = new_student_obj

        logging.info('StudentLoginTable object successfully populated from file')

    def save_to_file(self, txt_file: TextIOWrapper):
        """
        Given the file output from an open('w') method, writes to the file the data within self
        """
        for student_login_obj in self.rows.values():
            txt_file.write(student_login_obj.tabulate())

        logging.info('StudentLoginTable object successfully saved to file')


class Section:
    def __init__(self, activity_status):
        self._activity_status = activity_status

    @property
    def activity_status(self):  # new to me
        return self._activity_status

    @activity_status.setter
    def activity_status(self, new_value):
        return

    @activity_status.getter
    def activity_status(self):
        return 'blah'


class SectionTable:
    def __init__(self):
        pass

    def load_from_file(self):
        pass
