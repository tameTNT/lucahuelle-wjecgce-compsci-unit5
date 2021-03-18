import argparse
import logging
import tkinter as tk
from getpass import getpass
from tkinter import font
from tkinter import messagebox

import ui.landing
import ui.student
from data_tables import data_handling
from processes import validation, password_logic
from ui import RootWindow

logging.basicConfig(filename='main_program.log',
                    filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)8s: %(message)s')


def close_window_call(db_obj: data_handling.Database, tk_root: tk.Tk) -> None:
    """
    This function is activated by the WM_DELETE_WINDOW protocol (i.e. when the user presses X).
    It makes the user confirm they want to close the program and saves the program data to file.

    :param db_obj: the main Database object to which the current database state should be saved from
    :param tk_root: tkinter Tk() object which is main base window that user wanted to close
    """
    logging.debug('User pressed quit button')
    if messagebox.askokcancel("Quit",
                              "Are you sure you want to quit?\n"
                              "This will save all currently stored data."):
        logging.info('User chose to destroy window and exit program')
        # saves current database state from memory to file before closing
        db_obj.save_state_to_file()
        tk_root.destroy()  # closes tkinter window
    else:
        logging.debug('User chose not to exit')


def create_gui():
    root = tk.Tk()

    # some font constants set here as Tk needs to be initialised to use nametofont()
    font_obj = font.nametofont('TkCaptionFont')
    font_obj['size'], font_obj['slant'] = 10, 'italic'
    # can't just assign font_obj as options edited below again
    ui.ITALIC_CAPTION_FONT = font.Font(**font_obj.actual())
    font_obj['weight'], font_obj['slant'] = 'bold', 'roman'
    ui.BOLD_CAPTION_FONT = font.Font(**font_obj.actual())

    main_window = RootWindow(tk_root=root, db=MAIN_DATABASE_OBJ)  # initialises tkinter root/base

    PAGE_OBJ_LIST = list()
    for cls in ui.GenericPage.__subclasses__():
        subcls_list = cls.__subclasses__()
        if subcls_list:  # subclasses of subclasses exist (e.g. Student/StaffLogin pages)
            for subcls in subcls_list:
                PAGE_OBJ_LIST.append(subcls)
        else:
            PAGE_OBJ_LIST.append(cls)

    # initialises actual tkinter window on Welcome page
    # todo: change start_page back to ui.landing.Welcome
    main_window.initialise_window(page_obj_list=PAGE_OBJ_LIST, start_page=ui.landing.StudentLogin)
    # binds above function to action of closing window - i.e. tkinter triggers func on close
    root.protocol("WM_DELETE_WINDOW", lambda: close_window_call(MAIN_DATABASE_OBJ, root))
    root.mainloop()


def create_staff_account():
    print('Abort entry process with break command (Ctrl+Z).'
          '\nCreating a new staff account...'
          '\nPlease enter the following details:')

    # noinspection PyTypeChecker
    staff_table: data_handling.StaffTable = MAIN_DATABASE_OBJ.get_table_by_name('StaffTable')

    while True:
        fullname = input('Fullname: ')
        username = input('Username: ')

        print('NB: No characters will be shown when entering passwords.')
        while True:
            password_a = getpass(prompt='Password: ')
            # TODO: password strength enforcement
            password_b = getpass(prompt='Confirm password: ')
            if password_a == password_b:
                password_hash = password_logic.hash_pwd_str(password_a)
                break
            else:
                print('Passwords entered do not match. Please try again.')

        try:
            new_staff_user = data_handling.Staff(username, password_hash, fullname)
        except validation.ValidationError as e:
            print(f'Error in entered data as follows:\n{str(e)}\nPlease try again.')
        else:
            staff_table.add_row(new_staff_user)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.format_help()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--show-gui',
                       help='show GUI to log in to system as staff or student',
                       action='store_true')
    group.add_argument('--create-staff-account',
                       help='launch interactive command line to create staff/admin accounts',
                       action='store_true')
    args = parser.parse_args()

    if args.show_gui or args.create_staff_account:
        MAIN_DATABASE_OBJ = data_handling.Database()
        try:
            MAIN_DATABASE_OBJ.load_state_from_file()  # loads last database state from file into memory
            print('Tables successfully loaded from txt files.')
        except FileNotFoundError:
            # todo: test 'clean' startup with no txt files/database
            print('No existing complete database. New files will be created on program termination.')

        if args.show_gui:
            logging.debug('show-gui argument provided: creating tkinter instance')
            create_gui()
        elif args.create_staff_account:
            logging.debug('create-staff-account argument provided: launching command line function')
            create_staff_account()
    else:
        logging.debug('No arguments provided at command line. Showing help instead')
        parser.print_help()
