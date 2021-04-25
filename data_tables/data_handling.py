from __future__ import annotations

import datetime as dt
import logging  # logging functionality
import shutil
from pathlib import Path  # file handling
from typing import Collection, Union, Dict, List, Optional  # type hints in function and class definitions
from typing.io import TextIO

from data_tables import SECTION_NAME_MAPPING
from processes import shorten_string
from processes.datetime_logic import str_to_date_dict, datetime_to_str, date_in_past, calculate_end_date
from processes.validation import validate_int, validate_length, validate_lookup, \
    validate_date, validate_regex

# simplistic and naive regular expression for validating emails
EMAIL_MAX_LEN = 50  # should match 5,??? above
# matches abc@def.ghi
EMAIL_RE_PATTERN = r'^(?=.{5,%s}$)[^@]+@[^@.]+\.[^@.]+$' % EMAIL_MAX_LEN
# length of internal student_id, etc. Allows for 10^INTERNAL_ID_LEN unique items
INTERNAL_ID_LEN = 5

# fixme: what happens if the user enters this or quotes into strings? clean input in save function?
FIELD_SEP_STR = r'\%s'


class Row:
    """
    Base class for row classes/data objects to be stored within tables.
    Must have a key_field which needs to be unique for each row/record/object in a table
    """

    key_field = ''

    def __repr__(self) -> str:
        """
        Returns a string representation of object in form:
        f'<ClassName object key_field={self.key_field!r} field_2={self.field_2!r} ...>'
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
            if attr_name[0] != '_':  # ignores protected attributes
                str_func = str  # defaults to just using the str() func on the attribute
                if attr_name in special_str_funcs:
                    str_func = special_str_funcs[attr_name]
                return_string += str_func(attr_val).ljust(padding_values[attr_name]) + FIELD_SEP_STR
        return return_string + '\n'


class Table:
    """
    Base class for table classes which are then stored within a Database object.
    """

    row_class = Row  # indicates what Row objs will be stored within this table
    # objects are stored in dictionary using key_field of self.row_class as key
    row_dict: Dict[str, Row]

    # a Collection is just a sized iterable
    def __init__(self, start_table: Collection[row_class] = None):
        """
        Populates self.row_dict from the iterable of row objects, start_table
        """

        self.row_dict = dict()
        if start_table:  # if a collection of objects has been provided
            for row_obj in start_table:
                self.add_row(row_obj)

            logging.info(f'{type(self).__name__} object successfully populated from iterable '
                         f'argument - {len(start_table)} {self.row_class.__name__} object(s) added')

    def __repr__(self) -> str:
        """
        Returns a string representation of object.
        """
        return f'<{type(self).__name__} object with {len(self.row_dict)} row(s) ' \
               f'of {self.row_class} objects>'

    def get_new_key_id(self) -> int:
        """
        Looks at current row_dict and returns the next
        available id that can be used as a unique key.
        Should only be used with tables that use an integer-only id key_field.
        """
        taken_ids = {int(str_id) for str_id in self.row_dict.keys()}
        if taken_ids:
            # range(1, max(taken_ids) + 2): a range of all possible ids between 1 and the max taken id+1
            # set.difference finds any unused ids in this range and min() finds the smallest such id
            return min(set(range(1, max(taken_ids) + 2)).difference(taken_ids))
        else:
            return 1  # ids should start at 1

    def add_row(self, *args, **kwargs) -> None:
        """
        Add a new row/object to table.
        If an object is provided first, that is added directly - all other arguments are ignored.
        Otherwise, a new object is initialised (using all args OR kwargs (kwargs priority)) and then added.
        Raises KeyError if attempting to add an object with a non-unique key field.
        """
        if kwargs:
            # noinspection PyArgumentList
            new_row_obj = self.row_class(**kwargs)
        else:
            if isinstance(args[0], self.row_class):  # if first argument is a row object
                new_row_obj = args[0]
            else:
                # if no object passed to function then
                # object initialisation arguments have been passed instead
                # so row_class __init__() method is called

                # noinspection PyArgumentList
                new_row_obj = self.row_class(*args, **kwargs)

        key_field = self.row_class.key_field
        primary_key = new_row_obj.__getattribute__(key_field)
        if primary_key not in self.row_dict.keys():
            self.row_dict[primary_key] = new_row_obj
        else:
            error_str = f'Tried to add an object to {type(self).__name__} with a ' \
                        f'non-unique primary key - value of "{primary_key}" for field "{key_field}"'
            logging.error(error_str)
            raise KeyError(error_str)

    def delete_row(self, primary_key):
        """
        Attempts to delete row with primary key 'primary_key' from table.
        Raises a KeyError if this key is invalid.
        """
        try:
            del self.row_dict[primary_key]
        except KeyError:
            error_str = f'{primary_key} is not a row within {type(self).__name__}'
            logging.error(error_str)
            raise KeyError(error_str)

    def load_from_file(self, txt_file: TextIO):
        """
        Given the output from an open() method, populates self with data from lines of text file
        """
        txt_lines = txt_file.readlines()
        for row in txt_lines:
            obj_info = list()

            padded_fields = row.split(FIELD_SEP_STR)  # split line/row by separator
            for field in padded_fields:
                if field != '\n':
                    obj_info.append(field.strip())  # remove padding whitespace

            self.add_row(*obj_info)  # add new row/obj to table

        txt_file.close()
        logging.info(f'{type(self).__name__} object successfully populated from file - '
                     f'added {len(txt_lines)} {self.row_class.__name__} objects')

    def save_to_file(self, txt_file: TextIO):
        """
        Given the file output from an open('w') method, writes to the file the data within self
        """
        for row_object in self.row_dict.values():
            txt_file.write(row_object.tabulate())

        txt_file.close()
        logging.debug(f'{type(self).__name__} object successfully saved to file')


class StudentLogin(Row):
    key_field = 'username'

    def __init__(self, username: str, password_hash: str, student_id: Union[int, str]):
        self.username = validate_length(username, 2, 30, 'Username')
        self.password_hash = password_hash

        # student_id should be int but when parsed from txt file will be str so needs conversion
        self.student_id = validate_int(student_id, 'Student ID')

        logging.debug(f'New StudentLogin object successfully created - username={self.username!r}')

    def __repr__(self):
        # only first 10 chars of hash shown
        return f'<StudentLogin object username={self.username!r} ' \
               f"password_hash='{shorten_string(self.password_hash, 13)}' student_id={self.student_id}>"

    def tabulate(self, padding_values=None, special_str_funcs=None):
        padding_values = {
            'username': 30,
            'password_hash': 128,
            'student_id': INTERNAL_ID_LEN,
        }
        return super().tabulate(padding_values, special_str_funcs)


class StudentLoginTable(Table):
    row_class = StudentLogin
    row_dict: Dict[str, StudentLogin]


class Student(Row):
    key_field = 'student_id'

    def __init__(self, student_id: Union[int, str], centre_id: Union[int, str], award_level: str,
                 year_group: Union[int, str], is_approved: Union[int, str] = 0,
                 fullname: str = '', gender: str = '',
                 date_of_birth: str = '', address: str = '', phone_primary: str = '',
                 email_primary: str = '', phone_emergency: str = '', primary_lang: str = '',
                 submission_date: str = '', vol_info_id: Union[int, str] = '',
                 skill_info_id: Union[int, str] = '', phys_info_id: Union[int, str] = '',
                 from_file: bool = True):
        # Only the first 4 parameters are provided by staff. (is_approved defaults to 0)
        # The rest are filled in by the student at a later date
        # and hence default to '' on initial creation.

        # todo: creation of students by staff
        # student_id should be int but when parsed from txt file will be str so needs conversion
        self.student_id = validate_int(student_id, 'Student ID')

        self.centre_id = validate_int(centre_id, 'Centre ID')

        self.award_level = validate_lookup(award_level, {'bronze', 'silver', 'gold'}, 'Award Level')

        year_group = str(validate_int(year_group, 'Year Group'))
        self.year_group = validate_lookup(year_group, set(map(str, range(7, 14))), 'Year Group')

        # 1 = True/is approved, 0 = False/is not approved
        self.is_approved = int(is_approved)

        # All following attributes are null ('') if a fullname is not provided -
        # indicating initial creation and not student completing enrolment/loading

        self.fullname = validate_length(fullname, 2, 30, 'Fullname') if fullname else ''

        # pnts = prefer not to say
        self.gender = validate_lookup(gender, {'male', 'female', 'other', 'pnts'},
                                      'Gender') if fullname else ''

        if from_file:  # date range validation skipped if loading from file to allow for dates in the past
            self.date_of_birth = validate_date(date_of_birth, 'Date of birth') if fullname else ''
        else:
            # -365.25*25 = -25 years (-ve=in the past); -365.25*10 = -10 years (-ve=in the past)
            self.date_of_birth = validate_date(date_of_birth, 'Date of birth',
                                               offset_range=(-365.25 * 25, -365.25 * 10))

        self.address = validate_length(address, 5, 100,
                                       'Address') if fullname else ''

        self.phone_primary = validate_length(phone_primary, 9, 11,
                                             'Primary Phone') if fullname else ''

        self.email_primary = validate_regex(email_primary, EMAIL_RE_PATTERN, 'Primary Email',
                                            'abc@def.ghi') if fullname else ''

        self.phone_emergency = validate_length(phone_emergency, 9, 11,
                                               'Emergency Phone') if fullname else ''

        self.primary_lang = validate_lookup(primary_lang, {'english', 'welsh'},
                                            'Primary Language') if fullname else ''

        self.submission_date = dt.datetime(**str_to_date_dict(submission_date)) if fullname else ''

        self.vol_info_id = validate_int(vol_info_id, 'vol_info_id') if vol_info_id else ''

        self.skill_info_id = validate_int(skill_info_id, 'skill_info_id') if skill_info_id else ''

        self.phys_info_id = validate_int(phys_info_id, 'phys_info_id') if phys_info_id else ''

        logging.debug(f'New Student object {"fully" if fullname else "partially"} created '
                      f'- student_id={self.student_id}')

    def complete_enrolment(self, fullname: str, gender: str,
                           date_of_birth: str, address: str, phone_primary: str,
                           email_primary: str, phone_emergency: str, primary_lang: str):
        fullname = validate_length(fullname, 2, 30, 'Fullname')

        # pnts = prefer not to say
        gender = validate_lookup(gender, {'male', 'female', 'other', 'pnts'},
                                 'Gender')

        # -365.25*25 = -25 years (-ve=in the past); -365.25*10 = -10 years (-ve=in the past)
        date_of_birth = validate_date(date_of_birth, 'Date of birth',
                                      offset_range=(-365.25 * 25, -365.25 * 10))

        address = validate_length(address, 5, 100,
                                  'Address')

        phone_primary = validate_length(phone_primary, 9, 11,
                                        'Primary Phone')

        email_primary = validate_regex(email_primary, EMAIL_RE_PATTERN, 'Primary Email',
                                       'abc@def.ghi')

        phone_emergency = validate_length(phone_emergency, 9, 11,
                                          'Emergency Phone')

        primary_lang = validate_lookup(primary_lang, {'english', 'welsh'},
                                       'Primary Language')

        logging.debug('All validation checks passed on input data for student enrollment.')

        self.fullname = fullname
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.address = address
        self.phone_primary = phone_primary
        self.email_primary = email_primary
        self.phone_emergency = phone_emergency
        self.primary_lang = primary_lang
        self.submission_date = dt.datetime.now()

        logging.debug(f'New Student object fully created '
                      f'- student_id={self.student_id} fullname={self.fullname!r}')

    def __repr__(self):
        return f'<Student object student_id={self.student_id} ' \
               f'fullname={self.fullname!r} year_group={self.year_group!r} ' \
               f"award_level={self.award_level!r} date_of_birth='{self.date_of_birth!s}' " \
               f'is_approved={self.is_approved}>'

    def tabulate(self, padding_values=None, special_str_funcs=None):
        padding_values = {
            'student_id': INTERNAL_ID_LEN,
            'centre_id': 10,
            'award_level': 6,
            'year_group': 2,
            'fullname': 30,
            'gender': 6,
            'date_of_birth': 10,
            'address': 100,
            'phone_primary': 11,
            'email_primary': EMAIL_MAX_LEN,
            'phone_emergency': 11,
            'primary_lang': 7,
            'submission_date': 10,
            'vol_info_id': INTERNAL_ID_LEN,
            'skill_info_id': INTERNAL_ID_LEN,
            'phys_info_id': INTERNAL_ID_LEN,
            'is_approved': 1,
        }
        special_str_funcs = {
            'date_of_birth': datetime_to_str,
            'submission_date': datetime_to_str,
        }
        return super().tabulate(padding_values, special_str_funcs)

    def get_section_obj(self, section_type_short: str, section_table: SectionTable) -> Optional[Section]:
        """
        Returns the requested section object (if it exists) for self

        :param section_type_short: specific section to retrieve. One of 'vol', 'skill' or 'phys'
        :param section_table: SectionTable to return section_obj from if it exists
        :return: Section object to interface with if it exists, otherwise None
        """
        # student.vol_info_id, student.skill_info_id, student.phys_info_id
        section_id = self.__getattribute__(f'{section_type_short}_info_id')
        if section_id:
            return section_table.row_dict[section_id]
        else:
            return None

    def get_progress_summary(self, section_table: SectionTable) -> str:
        # todo: docstring
        if self.is_approved:
            section_started_count = 0
            section_finished_count = 0
            for section_type_short in SECTION_NAME_MAPPING.keys():
                # student.vol_info_id, student.skill_info_id, student.phys_info_id
                section_id = self.__getattribute__(f'{section_type_short}_info_id')
                if section_id:
                    section_started_count += 1
                    section_obj = section_table.row_dict[section_id]
                    if section_obj.activity_status == '':  # fixme: finish status method to compare option here
                        section_finished_count += 1

            if section_finished_count == 3:  # todo: doesn't include expeditions
                return 'Fully complete'
            elif section_started_count == 3:
                return 'All in progress'
            elif 1 <= section_started_count < 3:
                return 'In progress'
            else:
                return 'None started'

        elif not self.fullname:  # student has not yet entered all details
            return 'Pending enrolment'

        elif not self.is_approved:
            return 'Needs approval'

    def get_login_username(self, login_table: StudentLoginTable) -> Optional[str]:
        """
        Returns the username of self using the login_table provided.
        If the student does not have a login for whatever reason, returns None
        """
        for username, login in login_table.row_dict.items():
            if login.student_id == self.student_id:
                return username

        return None


class StudentTable(Table):
    row_class = Student
    row_dict: Dict[int, Student]


class Section(Row):
    key_field = 'section_id'

    def __init__(self, section_id: Union[int, str], section_type: str,
                 activity_start_date: str, activity_timescale: str,
                 activity_type: str, activity_details: str, activity_goals: str,
                 assessor_fullname: str, assessor_phone: str, assessor_email: str,
                 from_file: bool = True):
        self.section_id = validate_int(section_id, 'Section ID')

        self.section_type = validate_lookup(section_type, set(SECTION_NAME_MAPPING.keys()), 'Section Type')

        if from_file:
            temp_start_date = validate_date(activity_start_date, 'Activity Start Date')
        else:
            # A valid start date can be up to 1 year in the future
            temp_start_date = validate_date(activity_start_date, 'Activity Start Date', offset_range=(0, 365.25))
        self.activity_start_date = temp_start_date

        self.activity_timescale = validate_lookup(activity_timescale, {'90', '180', '360'},
                                                  'Activity Timescale')

        self.activity_type = validate_length(activity_type, 3, 20, 'Activity Type')

        self.activity_details = validate_length(activity_details, 10, 200, 'Activity Details')

        self.activity_goals = validate_length(activity_goals, 10, 100, 'Activity Goals')

        self.assessor_fullname = validate_length(assessor_fullname, 2, 30, 'Assessor Fullname')

        self.assessor_phone = validate_length(assessor_phone, 9, 11, 'Assessor Phone')

        self.assessor_email = validate_regex(assessor_email, EMAIL_RE_PATTERN, 'Assessor Email',
                                             'abc@def.ghi')

        # This is a private attribute and as such is only updated when it is accessed.
        # This can not be set manually
        self._activity_status = ''

        logging.debug(f'New Section object successfully created - section_id={self.section_id}')

    def __repr__(self):
        return f'<Section object section_id={self.section_id} ' \
               f'section_type={self.section_type!r} ' \
               f"activity_start_date='{self.activity_start_date!s}' " \
               f'activity_timescale={self.activity_timescale!r} ' \
               f'activity_type={self.activity_type!r} ' \
               f'assessor_fullname={self.assessor_fullname!r}'

    def tabulate(self, padding_values=None, special_str_funcs=None):
        padding_values = {
            'section_id': INTERNAL_ID_LEN,
            'section_type': 5,
            'activity_start_date': 10,
            'activity_timescale': 3,
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
        # this method is called every time this variable is accessed
        proposed_end_date = calculate_end_date(int(self.activity_timescale), self.activity_start_date)

        if date_in_past(proposed_end_date):
            # todo: GENERATE SECTION STATUS method
            self._activity_status = 'Not Implemented'
        else:
            self._activity_status = 'In Progress'

        return self._activity_status


class SectionTable(Table):
    row_class = Section
    row_dict: Dict[int, Section]


class Resource(Row):
    key_field = 'resource_id'

    def __init__(self, resource_id: Union[int, str], file_path: Union[Path, str],
                 is_section_report: Union[int, str], resource_type: str,
                 parent_link_id: Union[int, str], date_uploaded: Union[str] = ''):

        self.resource_id = validate_int(resource_id, 'Resource ID')

        if isinstance(file_path, str):
            # validates string paths (loaded from file)
            # leading slashes optional. Must start with 'uploads\' followed by at least 1 char
            file_path = validate_regex(file_path, r'[\\]?uploads\\.+', 'file_path', '(\\)uploads\\...')
            # wouldbenice: check file path actually exists when loading from file (from_file: bool = True)

        self.file_path = Path(file_path)
        # wouldbenice: path strings are gonna cause issues when loading for viewing

        self.is_section_report = int(is_section_report) if is_section_report else 0
        self.resource_type = validate_lookup(resource_type, {'event', 'section_evidence'}, 'Resource Type')
        self.parent_link_id = validate_int(parent_link_id, 'Parent Link ID')

        if not date_uploaded:  # if this argument is not provided, generated from current datetime
            date_uploaded = datetime_to_str()  # gets current datetime as string
        self.date_uploaded = validate_date(date_uploaded, 'Date Uploaded')

        logging.debug(f'New Resource object successfully created - resource_id={self.resource_id}')

    def __repr__(self):
        return f'<Resource object resource_id={self.resource_id} ' \
               f"file_path={self.file_path!r} date_uploaded='{self.date_uploaded!s}'" \
               f'is_section_report={self.is_section_report} ' \
               f'resource_type={self.resource_type!r} parent_link_id={self.parent_link_id}>'

    def tabulate(self, padding_values=None, special_str_funcs=None):
        padding_values = {
            'resource_id': INTERNAL_ID_LEN,
            'file_path': 256,  # Windows default file path limit - highly unlikely that path is longer
            'is_section_report': 1,
            'resource_type': 16,
            'parent_link_id': INTERNAL_ID_LEN,
            'date_uploaded': 10,
        }
        special_str_funcs = {
            'date_uploaded': datetime_to_str,
        }
        return super().tabulate(padding_values, special_str_funcs)


class ResourceTable(Table):
    row_class = Resource
    row_dict: Dict[int, Resource]

    def add_student_resources(self, selected_file_list: List[TextIO], student_id: int,
                              section_id: int) -> int:
        """
        Adds the files in selected_file_list to the ResourceTable each as its own Resource object.

        :param selected_file_list: a list of TextIO objects such as that produced by tk.filedialog.askopenfiles()
        :param student_id: the id of the student to which the resources should be linked
        :param section_id: the id of the section to which the resources should be linked
        :return: the length of selected_file_list
        """
        if selected_file_list:  # if any files were selected (i.e. operation not cancelled)
            internal_upload_dir = Path('uploads') / 'student' / f'id-{student_id}'

            upload_dir = Path.cwd() / internal_upload_dir
            upload_dir.mkdir(parents=True, exist_ok=True)

            for fobj in selected_file_list:
                orig_file_path = Path(fobj.name)  # .name is the filepath

                upload_path = upload_dir / orig_file_path.name
                i = 0
                while upload_path.exists():  # adds ' (i)' to end of filename (before suffix) until unique
                    i += 1  # keeps increasing i until unique
                    new_name = f'{upload_path.stem} ({i}){upload_path.suffix}'
                    upload_path = upload_path.with_name(new_name)

                shutil.copy(orig_file_path, upload_path)  # 'uploads'/copies file to upload_path

                self.add_row(
                    resource_id=self.get_new_key_id(),
                    file_path=internal_upload_dir / upload_path.name,
                    is_section_report=0,
                    resource_type='section_evidence',
                    parent_link_id=section_id
                )

        logging.info(f'{len(selected_file_list)} resource(s) were added to {type(self).__name__}')
        return len(selected_file_list)

    # todo: add_event_resources - possible to combine with above

    def has_section_report(self, section_id: int) -> bool:
        """
        Returns True if the section with id parent_link_id already has a
        resource associated with it marked as a section report. Returns False
        if this is not the case.

        :param section_id: id of section to check
        :return: boolean of whether there is a report associated with section already
        """
        for resource in self.row_dict.values():
            if resource.resource_type == 'section_evidence' and resource.parent_link_id == section_id:
                if resource.is_section_report:
                    return True
        return False

    def delete_row(self, primary_key):
        file_path = self.row_dict[primary_key].file_path
        file_path.unlink(missing_ok=True)  # actually deletes file - doesn't care if it doesn't exist
        logging.debug(f'{file_path} was deleted.')
        super().delete_row(primary_key)


# todo: event table for calendar and expeditions etc.


class Staff(Row):
    key_field = 'username'

    def __init__(self, username: str, password_hash: str, fullname: str):
        # wouldbenice: staff detail table (similar to student table)
        self.username = validate_length(username, 2, 30, 'Username')
        self.password_hash = password_hash

        self.fullname = validate_length(fullname, 2, 30, 'Fullname')

        logging.debug(f'New Staff object successfully created - username={self.username!r}')

    def __repr__(self):
        # only first 10 chars of hash shown
        return f'<Staff object username={self.username!r} ' \
               f"password_hash='{shorten_string(self.password_hash, 13)}' fullname={self.fullname!r}>"

    def tabulate(self, padding_values=None, special_str_funcs=None):
        padding_values = {
            'username': 30,
            'password_hash': 128,
            'fullname': 30,
        }
        return super().tabulate(padding_values, special_str_funcs)


class StaffTable(Table):
    row_class = Staff
    row_dict: Dict[str, Staff]


class Database:
    def __init__(self):
        """
        When initialised, automatically initialises one instance of each 'Table' in this .py file.
        These are all added to the self.database dict for access.
        """
        table_list = Table.__subclasses__()
        self.database: Dict[str, Table] = dict()
        for table_cls in table_list:
            # creates instance of table and adds to database with key of table name
            self.database[table_cls.__name__] = table_cls()

        logging.debug(f'Database initialisation created {len(table_list)} '
                      f'table(s) automatically: {", ".join(self.database)}')

    def __repr__(self):
        return f'<Database object with {len(self.database)} table(s): ' \
               f'{", ".join(self.database.keys())}>'

    @staticmethod  # since it doesn't use any class attributes
    def get_txt_database_dir():
        """
        Returns the absolute path to the directory in which to store the database txt files.
        Creates this path if it does not yet exist.
        """
        txt_db_path = Path.cwd()
        if 'data_tables' not in str(txt_db_path):
            txt_db_path /= 'data_tables'  # wouldbenice: not guaranteed to cover every case I think?

        txt_db_path /= 'txt_tbls'
        txt_db_path.mkdir(exist_ok=True)  # makes the path if it does not yet exist

        return txt_db_path

    def load_state_from_file(self, suffix=''):
        """
        Loads the entire database state from txt files into memory
        after clearing current state.
        Handled using each Table object's load_from_file method.
        If even one table is missing, no tables are loaded (due to links between tables)
        and a FileNotFoundError is raised.
        If suffix is given, appends this to each table's filename when saving (use for backups).
        """
        load_path_list = list()
        for table_name in self.database.keys():
            new_load_path = self.get_txt_database_dir() / f'{table_name}{suffix}.txt'
            load_path_list.append(new_load_path)
            if not new_load_path.exists():  # a table is missing
                error_str = f'The file {new_load_path} does not exist but should. ' \
                            f'Table load aborted and no tables loaded into memory.'
                logging.error(error_str)
                raise FileNotFoundError(error_str)

        for load_path, table_obj in zip(load_path_list, self.database.values()):
            previous_row_count = len(table_obj.row_dict)
            table_obj.row_dict = dict()  # clears table
            logging.debug(f'Cleared {previous_row_count} rows/{table_obj.row_class.__name__} '
                          f'object(s) from {type(table_obj).__name__} table successfully')

            with load_path.open(mode='r') as fobj:
                table_obj.load_from_file(fobj)

        logging.info(
            f'{len(load_path_list)} populated table(s) successfully loaded into Database object. '
            f'(from "{self.get_txt_database_dir()!s}" using {suffix!r} as table filename suffix)')

    def save_state_to_file(self, suffix=''):
        """
        Saves the entire database state to txt files from memory.
        Handled using each Table object's save_to_file method.
        If suffix is given, appends this to each table's filename when saving (use for backups).
        """
        for table_name, table_obj in self.database.items():
            save_path = self.get_txt_database_dir() / f'{table_name}{suffix}.txt'

            with save_path.open(mode='w+') as fobj:
                table_obj.save_to_file(fobj)

        logging.info(
            f'All {len(self.database.items())} table(s) in Database object '
            f'successfully saved to txt files. '
            f'(in "{self.get_txt_database_dir()!s}" using {suffix!r} as table filename suffix)')

    def get_table_by_name(self, table_name) -> Table:
        """
        Returns the table_name Table object from the database
        for queries and editing etc.
        If the table_name is not a valid table name then a KeyError is raised.
        """
        if table_name in self.database.keys():
            return self.database[table_name]
        else:
            error_str = f'{table_name} is not a valid table name. ' \
                        f'Valid options: {", ".join(self.database.keys())}'
            logging.error(error_str)
            raise KeyError(error_str)
