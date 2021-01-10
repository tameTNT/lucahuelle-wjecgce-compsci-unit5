import logging
from io import TextIOWrapper
from typing import Iterable


class StudentLogin:
    def __init__(self, username: str, password: str, user_id: int):
        self.username = username
        self.password = password
        self.user_id = user_id
        logging.info('New StudentLogin object successfully created')

    def __repr__(self):
        return f'<StudentLogin object username={self.username!r} ' \
               f'password={self.password!r} user_id={self.user_id!r}>'

    def tabulate(self) -> str:
        """
        Returns a one line string of the object's data tabulated for text storage
        """
        # TODO: write tests
        return_string = ''
        return_string += self.username.ljust(30) + r'\%s'
        return_string += self.password.ljust(192) + r'\%s'
        return_string += str(self.user_id).ljust(4)
        return return_string


class StudentLoginTable:
    def __init__(self, start_table: Iterable[StudentLogin] = tuple()):
        """
        :param start_table: (optional) an iterable of StudentLogin objects to populate self with
        """
        self.rows = list()
        if start_table:  # if an iterable of objects has been provided
            for obj in start_table:
                self.rows.append(obj)

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
                obj_info.append(field.strip())  # remove padding whitespace

            self.rows.append(StudentLogin(*obj_info))

        logging.info('StudentLoginTable object successfully populated from file')

    def save_to_file(self, txt_file: TextIOWrapper):
        """
        Given the output from an open() method, writes to that text file the data within self
        """
        # TODO: write data to text file
        return


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
