import datetime as dt
import logging  # logging functionality
from io import TextIOWrapper  # type hints in function definitions
from pathlib import Path  # file handling
from typing import Collection, Union  # type hints in function and class definitions

from processes.date_logic import str_to_date_dict, datetime_to_str
from processes.validation import validate_int, validate_length, validate_lookup, \
    validate_date, validate_regex

# simplistic and naive regular expression for validating emails
EMAIL_MAX_LEN = 50  # should match 5,??? above
EMAIL_RE_PATTERN = r'^(?=.{5,%(len)s}$)[^@]+@[^@.]+.[^@.]+$' % {'len': EMAIL_MAX_LEN}
# length of internal user_id, student_id, etc. Allows for 10^INTERNAL_ID_LEN unique items
INTERNAL_ID_LEN = 5


class Row:
    """
    Base class for row classes/data objects to be stored within tables.
    Must have a key_field which needs to be unique for each row/record/object in a table
    """

    key_field = ''

    def __repr__(self) -> str:
        """
        Returns a string representation of object in form:
        f'<ClassName object key_field="{self.key_field}" field_2="{self.field_2}" ...>'
        Not all fields need be included - since only for debugging and clarity
        and not for saving/duplicating/etc.
        """
        return '<Instance of Row class. Has a tabulate method.>'

    def tabulate(self, padding_values: dict = None, special_str_funcs: dict = None) -> str:
        """
        Returns a one line string of the object's data tabulated for text storage
        :param padding_values: dictionary of field_name (str): padding_value (int) pairs
        :param special_str_funcs: dictionary of fields with a custom func for a str representation.
            Each function should take one argument, the field's value and return a string.
            e.g. needed for date formatting
        """
        if padding_values is None:
            padding_values = {}
        if special_str_funcs is None:
            special_str_funcs = {}

        return_string = ''
        for attr_name, attr_val in self.__dict__.items():
            str_func = str
            if attr_name in special_str_funcs:
                str_func = special_str_funcs[attr_name]
            return_string += str_func(attr_val).ljust(padding_values[attr_name]) + r'\%s'
        return return_string + '\n'


class Table:
    """
    Base class for table classes which are then stored within a Database object.
    """

    row_class = Row  # indicates what Row objs will be stored within this table

    # a Collection is just a sized iterable
    def __init__(self, start_table: Collection[row_class] = None):
        """
        :param start_table: an iterable of row objects (children of Row class)
            to populate self with
        """

        # objects are stored in dictionary using key_field of self.row_class as key
        self.rows = dict()
        if start_table:  # if a collection of objects has been provided
            for row_obj in start_table:
                self.add_row(row_obj)

            logging.info(f'{type(self).__name__} object successfully populated from iterable '
                         f'argument - {len(start_table)} {self.row_class.__name__} object(s) added')

    def __repr__(self) -> str:
        """
        Returns a string representation of object.
        """
        return f'<{type(self).__name__} object with {len(self.rows)} row(s) ' \
               f'of {self.row_class} objects>'

    def add_row(self, *args):
        """
        Add a new row/object to table.
        If an object is provided first, that is added directly - all other arguments are ignored.
        Otherwise, a new object is initialised (using all args) and then added.
        Raises KeyError if attempting to add an object with a non-unique key field.
        """
        if isinstance(args[0], self.row_class):  # if first argument is a row object
            new_row_obj = args[0]
        else:
            # if no object passed to function then
            # object initialisation arguments have been passed instead
            # so row_class __init__() method is called

            # noinspection PyArgumentList
            new_row_obj = self.row_class(*args)

        key_field = self.row_class.key_field
        primary_key = new_row_obj.__getattribute__(key_field)
        if primary_key not in self.rows.keys():
            self.rows[primary_key] = new_row_obj
        else:
            error_str = f'Tried to add an object to {type(self).__name__} with a ' \
                        f'non-unique primary key - value of "{primary_key}" for field "{key_field}"'
            logging.error(error_str)
            raise KeyError(error_str)

    def load_from_file(self, txt_file: TextIOWrapper):
        """
        Given the output from an open() method, populates self with data from lines of text file
        """
        txt_lines = txt_file.readlines()
        for row in txt_lines:
            obj_info = list()

            padded_fields = row.split(r'\%s')  # split line/row by separator
            for field in padded_fields:
                if field != '\n':
                    obj_info.append(field.strip())  # remove padding whitespace

            self.add_row(*obj_info)  # add new row/obj to table

        logging.info(f'{type(self).__name__} object successfully populated from file - '
                     f'added {len(txt_lines)} {self.row_class.__name__} objects')

    def save_to_file(self, txt_file: TextIOWrapper):
        """
        Given the file output from an open('w') method, writes to the file the data within self
        """
        for row_object in self.rows.values():
            txt_file.write(row_object.tabulate())

        logging.debug(f'{type(self).__name__} object successfully saved to file')


class StudentLogin(Row):
    key_field = 'username'

    def __init__(self, username: str, password_hash: str, user_id: Union[int, str]):
        self.username = validate_length(username, 2, 30, 'username')
        self.password_hash = password_hash

        # user_id should be int but when parsed from txt file will be str so needs conversion
        self.user_id = validate_int(user_id, 'user_id')

        logging.debug(f'New StudentLogin object successfully created - username={self.username}')

    def __repr__(self):
        # only first 10 chars of hash shown
        return f'<StudentLogin object username="{self.username}" ' \
               f'password_hash="{self.password_hash[:10] + "..."}" user_id="{self.user_id}">'

    def tabulate(self, padding_values=None, special_str_funcs=None):
        padding_values = {
            'username': 30,
            'password_hash': 128,
            'user_id': INTERNAL_ID_LEN,
        }
        return super().tabulate(padding_values, special_str_funcs)


class StudentLoginTable(Table):
    row_class = StudentLogin


class Student(Row):
    key_field = 'student_id'

    def __init__(self, student_id: Union[int, str], fullname: str, centre_id: Union[int, str],
                 year_group: Union[int, str], award_level: str, gender: str,
                 date_of_birth: str, address: str, phone_primary: str,
                 email_primary: str, phone_emergency: str, primary_lang: str,
                 enrolment_date: str, skill_info_id: Union[int, str],
                 phys_info_id: Union[int, str], vol_info_id: Union[int, str]):

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

        self.enrolment_date = dt.datetime(**str_to_date_dict(enrolment_date))

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

        logging.debug(f'New Student object successfully created - student_id={self.student_id}')

    def __repr__(self):
        return f'<Student object student_id={self.student_id} ' \
               f'fullname={self.fullname} year_group={self.year_group}> ' \
               f'award_level={self.award_level} date_of_birth={self.date_of_birth!s}'

    def tabulate(self, padding_values=None, special_str_funcs=None):
        padding_values = {
            'student_id': INTERNAL_ID_LEN,
            'fullname': 30,
            'centre_id': 10,
            'year_group': 2,
            'award_level': 6,
            'gender': 6,
            'date_of_birth': 10,
            'address': 100,
            'phone_primary': 11,
            'email_primary': EMAIL_MAX_LEN,
            'phone_emergency': 11,
            'primary_lang': 7,
            'enrolment_date': 10,
            'skill_info_id': INTERNAL_ID_LEN,
            'phys_info_id': INTERNAL_ID_LEN,
            'vol_info_id': INTERNAL_ID_LEN,
        }
        special_str_funcs = {
            'date_of_birth': datetime_to_str,
            'enrolment_date': datetime_to_str,
        }
        return super().tabulate(padding_values, special_str_funcs)


class StudentTable(Table):
    row_class = Student


class Section(Row):
    key_field = 'section_id'

    def __init__(self, section_id: Union[int, str], section_type: str,
                 activity_start_date: str, activity_length: Union[int, str],
                 activity_type: str, activity_details: str, activity_goals: str,
                 assessor_fullname: str, assessor_phone: str, assessor_email: str):
        self.section_id = validate_int(section_id, 'section_id')

        self.section_type = validate_lookup(section_type, {'phys', 'skill', 'vol'}, 'section_type')

        # A valid start date can be up to 1 year in the future
        self.activity_start_date = validate_date(activity_start_date, 0, 365.25,
                                                 'activity_start_date')

        activity_length = str(validate_int(activity_length, 'activity_length'))
        self.activity_length = validate_lookup(activity_length, {'90', '180', '360'},
                                               'activity_length')

        self.activity_type = validate_length(activity_type, 3, 20, 'activity_type')

        self.activity_details = validate_length(activity_details, 10, 200, 'activity_details')

        self.activity_goals = validate_length(activity_goals, 10, 100, 'activity_goals')

        self.assessor_fullname = validate_length(assessor_fullname, 2, 30, 'assessor_fullname')

        self.assessor_phone = validate_length(assessor_phone, 9, 11, 'assessor_phone')

        self.assessor_email = validate_regex(assessor_email, EMAIL_RE_PATTERN, 'assessor_email')

        # This is a private attribute and as such is only updated when it is accessed.
        # This can not be set manually
        self._activity_status = ''

        logging.debug(f'New Section object successfully created - section_id={self.section_id}')

    def __repr__(self):
        return f'<Section object section_id="{self.section_id}" ' \
               f'section_type="{self.section_type}" ' \
               f'activity_start_date="{self.activity_start_date!s}" ' \
               f'activity_length="{self.activity_length}" activity_type="{self.activity_type}" ' \
               f'assessor_fullname="{self.assessor_fullname}'

    def tabulate(self, padding_values=None, special_str_funcs=None):
        padding_values = {
            'section_id': INTERNAL_ID_LEN,
            'section_type': 5,
            'activity_start_date': 10,
            'activity_length': 3,
            'activity_type': 20,
            'activity_details': 200,
            'activity_goals': 100,
            'assessor_fullname': 30,
            'assessor_phone': 11,
            'assessor_email': EMAIL_MAX_LEN,
        }
        special_str_funcs = {
            'activity_start_date': datetime_to_str,
        }
        return super().tabulate(padding_values, special_str_funcs)

    @property
    def activity_status(self):
        return self._activity_status

    @activity_status.getter
    def activity_status(self):
        # TODO: GENERATE SECTION STATUS method
        return 'Not Implemented'


class SectionTable(Table):
    row_class = Section


class Database:
    def __init__(self):
        """
        When initialised, automatically initialises one instance of each 'Table' in this .py file
        These are all added to self.database for access. (Therefore functions like an SQL database)
        """
        table_list = Table.__subclasses__()
        self.database = dict()
        for table_cls in table_list:
            # creates instance of table and adds to database with key of table name
            self.database[table_cls.__name__] = table_cls()

        logging.debug(f'Database initialisation created {len(table_list)} '
                      f'table(s) automatically: {", ".join(self.database)}')

    def __repr__(self):
        return f'<Database object with {len(self.database)} table(s): ' \
               f'{", ".join(self.database.keys())}>'

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
        Loads the entire database state from txt files into memory
        after clearing current state.
        Handled using each Table object's load_from_file method.
        If even one table is missing, no tables are loaded (due to links between tables)
        and a FileNotFoundError is raised.
        """
        load_path_list = list()
        for table_name in self.database.keys():
            load_path_list.append(self.get_txt_database_dir() / f'{table_name}.txt')
            if not load_path_list[-1].exists():  # a table is missing
                error_str = f'The file {load_path_list[-1]} does not exist but should. ' \
                            f'Table load aborted and no tables loaded into memory.'
                logging.error(error_str)
                raise FileNotFoundError(error_str)

        for load_path, table_obj in zip(load_path_list, self.database.values()):
            previous_row_count = len(table_obj.rows)
            table_obj.rows = dict()  # clears table
            logging.debug(f'Cleared {previous_row_count} rows/{table_obj.row_class.__name__} '
                          f'object(s) from {type(table_obj).__name__} table successfully')
            with load_path.open(mode='r') as fobj:  # type: TextIOWrapper
                table_obj.load_from_file(fobj)

        logging.info(
            f'{len(load_path_list)} populated table(s) successfully loaded into Database object')

    def save_state_to_file(self):
        """
        Saves the entire database state to txt files from memory.
        Handled using each Table object's save_to_file method.
        """
        for table_name, table_obj in self.database.items():
            save_path = self.get_txt_database_dir() / f'{table_name}.txt'

            with save_path.open(mode='w+') as fobj:  # type: TextIOWrapper
                table_obj.save_to_file(fobj)

        logging.info(
            f'All {len(self.database.items())} table(s) in Database object '
            f'successfully saved to txt files')
