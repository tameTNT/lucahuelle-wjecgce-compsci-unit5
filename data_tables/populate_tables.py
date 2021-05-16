import random
import string
from typing import Tuple

from data_tables.data_handling import Database, Student, StudentLogin
from processes import password_logic


def new_student_objs(username, id_num, centre_id, award_level, year_group) -> Tuple[StudentLogin, Student]:
    """
    Creates and returns a StudentLogin and a Student object

    :param username: username of new student to be created (for login)
    :param id_num: id number to use for object creation
    :param centre_id: centre number to use for object creation
    :param award_level: award level to use for object creation
    :param year_group: year group to use for object creation
    :return: login_obj, student_obj
    """
    login_obj = StudentLogin(
        username, password_logic.hash_pwd_str('password'), id_num
    )
    student_obj = Student(id_num, centre_id, award_level, year_group)
    return login_obj, student_obj


def get_random_username(length: int, taken_list: set) -> str:
    """
    Generates a random username of length 'length' that is not present in taken_list.
    (This is only checked if length is at least 3)
    """

    def gen_username(i: int):
        # chooses from all lowercase letters
        return ''.join([random.choice(string.ascii_lowercase) for _ in range(i)])

    result_str = gen_username(length)
    while result_str in taken_list and length >= 3:
        result_str = gen_username(length)  # regenerates username until not already taken

    return result_str


def populate_db(db_obj: Database, num_students) -> set:
    """
    Populates db_obj with num_students randomly generated Student and StudentLogin objects.
    Returns a set of all the usernames created
    """
    login_table = db_obj.get_table_by_name('StudentLoginTable')
    student_table = db_obj.get_table_by_name('StudentTable')

    usernames_created = set()
    for i in range(num_students):
        print(f'Generating student num {i + 1:>{len(str(num_students))}}/{num_students}...', end='\r')
        random_username = get_random_username(5, usernames_created)
        usernames_created.add(random_username)

        # creates a student with random username, sequential id, random award level and random year group (valid only)
        login_obj, student_obj = new_student_objs(
            username=random_username,
            id_num=i,
            centre_id=68362,
            award_level=random.choice(['bronze', 'silver', 'gold']),
            year_group=random.choice(range(7, 14))
        )
        login_table.add_row(login_obj)
        student_table.add_row(student_obj)

    return usernames_created


def populate(base_table_suffix):
    db = Database()
    db.load_state_from_file(suffix=base_table_suffix)

    print('Purging existing tables (except StaffTable)...')
    for name, table in db.database.items():
        if name != 'StaffTable':
            table.row_dict = {}  # clears row_dict

    print('Populating Student and StudentLogin tables with new student data...')
    username_set = populate_db(db, int(input('Num of random students to generate: ')))
    print('Done generating!')

    print(f'Usernames added:\n  {"; ".join(username_set)}\nAll students use password "password".')

    print('Saving new tables with suffix " (test students)"...')
    db.save_state_to_file(' (test students)')

    print('Done saving!')
