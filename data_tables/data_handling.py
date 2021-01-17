import datetime as dt
import logging  # logging functionality
from io import TextIOWrapper  # type hints in function definitions
from pathlib import Path  # file handling
from typing import Iterable, Optional, Union  # type hints in function definitions

from processes.date_logic import convert_str_to_dict
from processes.validation import validate_int, validate_length, validate_lookup, \
    validate_date, validate_regex

EMAIL_RE_PATTERN = r'[^@]+@[^@.]+.[^@.]+'


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

    def add_row(self, *args):
        """
        Add a new row/object to table.
        If an object is provided first, that is added directly - all other arguments are ignored.
        Otherwise, a new object is initialised (using all args) and then added.
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


class StudentLogin(RowClass):
    def __init__(self, username: str, password_hash: str, user_id: Union[int, str]):
        self.username = validate_length(username, 2, 30, 'username')
        self.password_hash = password_hash

        # user_id should be int but when parsed from txt file will be str so needs conversion
        self.user_id = validate_int(user_id, 'user_id')

        logging.debug(f'New StudentLogin object successfully created - username={self.username!r}')

    def __repr__(self):
        # only first 10 chars of hash shown
        return f'<StudentLogin object username={self.username!r} ' \
               f'password_hash={self.password_hash[:10] + "..."!r} user_id={self.user_id!r}>'

    def tabulate(self):
        return_string = ''
        return_string += self.username.ljust(30) + r'\%s'
        return_string += self.password_hash.ljust(128) + r'\%s'
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

            # noinspection PyTypeChecker
            logging.info('StudentLoginTable object successfully populated from iterable argument - '
                         f'{len(start_table)} object(s) added.')

    def __repr__(self):
        return f'<StudentLoginTable object with {len(self.rows)} row(s) of StudentLogin objects>'

    def add_row(self, *args):
        if isinstance(args[0], StudentLogin):  # first argument is a StudentLogin object
            new_student_obj = args[0]
        # if no object passed to function then initialisation arguments have been passed instead
        else:
            new_student_obj = StudentLogin(*args)

        primary_key = new_student_obj.username
        if primary_key not in self.rows.keys():
            self.rows[primary_key] = new_student_obj
        else:
            raise KeyError(
                f'Tried to add an object to table with a non-unique primary key - {primary_key}')

    def load_from_file(self, txt_file: TextIOWrapper):
        txt_lines = txt_file.readlines()
        for row in txt_lines:
            obj_info = list()

            padded_fields = row.split(r'\%s')  # split line/row by separator
            for field in padded_fields:
                obj_info.append(field.strip())  # remove padding whitespace and newlines

            self.add_row(*obj_info)  # add new row/StudentLogin obj to table

        logging.info(f'StudentLoginTable object successfully populated from file - '
                     f'added {len(txt_lines)} StudentLogin objects')

    def save_to_file(self, txt_file: TextIOWrapper):
        for student_login_obj in self.rows.values():
            txt_file.write(student_login_obj.tabulate())

        logging.info('StudentLoginTable object successfully saved to file')


class Student(RowClass):
    def __init__(self, student_id: Union[int, str], fullname: str, centre_id: Union[int, str],
                 year_group: Union[int, str], award_level: str, gender: str,
                 date_of_birth: str, address: str, phone_primary: str,
                 email_primary: str, phone_emergency: str, primary_lang: str,
                 enrolment_date: str, skill_info_id: Union[int, str, None],
                 phys_info_id: Union[int, str, None], vol_info_id: Union[int, str, None]):

        # student_id should be int but when parsed from txt file will be str so needs conversion
        self.student_id = validate_int(student_id, 'student_id')

        self.fullname = validate_length(fullname, 2, 30, 'fullname')

        self.centre_id = validate_int(centre_id, 'centre_id')

        year_group = str(validate_int(year_group, 'year_group'))
        self.year_group = validate_lookup(year_group, set(map(str, range(7, 14))), 'year_group')

        self.award_level = validate_lookup(award_level, {'bronze', 'silver', 'gold'}, 'award_level')

        # pnts = prefer not to say
        self.gender = validate_lookup(gender, {'male', 'female', 'other', 'pnts'}, 'gender')

        # -365.25*25 = -25 years (-ve=in the past); -365.25*10 = -10 years (-ve=in the past)
        self.date_of_birth = validate_date(date_of_birth, -365.25 * 25, -365.25 * 10,
                                           'date_of_birth')

        self.address = validate_length(address, 5, 100, 'address')

        self.phone_primary = validate_length(phone_primary, 9, 11, 'phone_primary')

        self.email_primary = validate_regex(email_primary, EMAIL_RE_PATTERN, 'email_primary')

        self.phone_emergency = validate_length(phone_emergency, 9, 11, 'phone_emergency')

        self.primary_lang = validate_lookup(primary_lang, {'english', 'welsh'}, 'primary-lang')

        self.enrolment_date = dt.datetime(**convert_str_to_dict(enrolment_date))

        if skill_info_id:
            self.skill_info_id = validate_int(skill_info_id, 'skill_info_id')
        else:
            self.skill_info_id = ''  # Null value if not provided

        if phys_info_id:
            self.phys_info_id = validate_int(phys_info_id, 'phys_info_id')
        else:
            self.phys_info_id = ''

        if vol_info_id:
            self.vol_info_id = validate_int(vol_info_id, 'vol_info_id')
        else:
            self.vol_info_id = ''

        logging.debug(f'New Student object successfully created - student_id={self.student_id!r}')
        # TODO: Student method - repr
        # TODO: Student method - tabulate


# class StudentTable(TableClass):
# TODO: table of students


# class Section(RowClass):
# TODO: section/activity table
    # def __init__(self, activity_status):
    #     self._activity_status = activity_status
    #
    # @property
    # def activity_status(self):
    #     return self._activity_status
    #
    # @activity_status.getter
    # def activity_status(self):
    #     TODO: GENERATE SECTION STATUS method
    #     return 'blah'


# class SectionTable(TableClass):
# TODO: table of activities


class Database:
    def __init__(self):
        """
        When initialised, automatically initialises one instance of each 'Table' in this .py file
        These are all added to self.database for access. (Therefore functions like an SQL database)
        """
        table_list = TableClass.__subclasses__()
        self.database = dict()
        for table_cls in table_list:
            # creates instance of table and adds to database with key of table name
            self.database[table_cls.__name__] = table_cls()

        logging.debug(f'Database created {len(table_list)} table(s) automatically: '
                      f'{",".join(self.database)}')

    def __repr__(self):
        return f'<Database object with {len(self.database)} table(s): ' \
               f'{",".join(self.database.keys())}>'

    @staticmethod  # since it doesn't use any attributes
    def get_txt_database_dir():
        """
        Returns the absolute path to the directory in which to store the database txt files.
        """
        if __name__ == '__main__':  # file is being executed in console/directly
            return Path.cwd()
        else:  # normal operation from main.py
            return Path.cwd() / 'data_tables'

    def load_state_from_file(self):
        """
        Loads the entire database state from txt files into memory.
        Handled using each Table object's load_from_file method.
        If even one table is missing, no tables are loaded (due to links between tables)
        and a FileNotFoundError is raised.
        """
        load_path_list = list()
        for table_name in self.database.keys():
            load_path_list.append(self.get_txt_database_dir() / f'{table_name}.txt')
            if not load_path_list[-1].exists():  # a table is missing
                logging.debug(f'Table at path {load_path_list[-1]} not found. Table load aborted.')
                raise FileNotFoundError(f'The file {load_path_list[-1]} does not exist but should. '
                                        f'No tables loaded into memory.')

        for load_path, table_obj in zip(load_path_list, self.database.values()):
            with load_path.open(mode='r') as fobj:
                # noinspection PyTypeChecker
                table_obj.load_from_file(fobj)

        logging.info(
            f'{len(load_path_list)} table(s) successfully loaded into Database object')

    def save_state_to_file(self):
        """
        Saves the entire database state to txt files from memory.
        Handled using each Table object's save_to_file method.
        """
        for table_name, table_obj in self.database.items():
            save_path = self.get_txt_database_dir() / f'{table_name}.txt'

            with save_path.open(mode='w+') as fobj:
                # noinspection PyTypeChecker
                table_obj.save_to_file(fobj)

        logging.info(
            f'All {len(self.database.items())} tables successfully saved to txt files')
