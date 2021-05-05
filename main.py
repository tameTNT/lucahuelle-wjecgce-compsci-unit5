import argparse
import logging
import tkinter as tk
from getpass import getpass
from tkinter import font
from tkinter import messagebox

import ui.landing
import ui.staff
import ui.student
from data_tables import data_handling, populate_tables
from processes import validation, password_logic
from ui import RootWindow

logging.basicConfig(filename='main_program.log',
                    filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)6s: %(message)s')


def close_window_call(db_obj: data_handling.Database, tk_root: tk.Tk, file_save_suffix: str) -> None:
    """
    This function is activated by the WM_DELETE_WINDOW protocol (i.e. when the user presses X).
    It makes the user confirm they want to close the program and saves the program data to file.

    :param db_obj: the main Database object to which the current database state should be saved from
    :param tk_root: tkinter Tk() object which is main base window that user wanted to close
    :param file_save_suffix: if given, appends this to each table's filename when saving (use for backups).
    """
    logging.debug('User pressed quit button')
    if messagebox.askokcancel("Quit",
                              "Are you sure you want to quit?\n"
                              "This will save all currently stored data."):
        logging.info('User chose to destroy window and exit program')
        # saves current database state from memory to file before closing
        db_obj.save_state_to_file(suffix=file_save_suffix)
        tk_root.destroy()  # closes tkinter window
    else:
        logging.debug('User chose not to exit')


def create_gui(file_save_suffix):
    root = tk.Tk()

    # some font constants set here as Tk needs to be initialised to use nametofont()
    font_obj = font.nametofont('TkCaptionFont')
    font_obj['size'], font_obj['slant'] = 10, 'italic'
    # can't just assign font_obj as options edited below again
    ui.ITALIC_CAPTION_FONT = font.Font(**font_obj.actual())
    font_obj['weight'], font_obj['slant'] = 'bold', 'roman'
    ui.BOLD_CAPTION_FONT = font.Font(**font_obj.actual())

    main_window = RootWindow(tk_root=root, db=MAIN_DATABASE_OBJ)  # initialises tkinter root/base

    page_obj_list = list()
    for cls in ui.GenericPage.__subclasses__():
        subcls_list = cls.__subclasses__()
        if subcls_list:  # subclasses of subclasses exist (e.g. Student/StaffLogin pages)
            for subcls in subcls_list:
                page_obj_list.append(subcls)
        else:
            page_obj_list.append(cls)

    # initialises actual tkinter window on Welcome page
    main_window.initialise_window(page_obj_list=page_obj_list, start_page=ui.landing.Welcome)
    # binds above function to action of closing window - i.e. tkinter triggers func on close
    root.resizable(width=False, height=False)
    root.protocol("WM_DELETE_WINDOW", lambda: close_window_call(MAIN_DATABASE_OBJ, root, file_save_suffix))
    root.mainloop()


def create_staff_account(file_save_suffix):
    print('Abort entry process with break command (Ctrl+Z).'
          '\nCreating a new staff account...'
          '\nPlease enter the following details:')

    # noinspection PyTypeChecker
    staff_table: data_handling.StaffTable = MAIN_DATABASE_OBJ.get_table_by_name('StaffTable')

    while True:  # ensure all data is valid
        fullname = input(' Fullname: ')
        username = input(' Username: ')

        print('Passwords should be between 6 and 100 characters long and contain one each of:\n'
              'lowercase letter, uppercase letter, number.')
        print('NB: No characters will be shown when entering passwords.')
        while True:  # ensure passwords match
            while True:  # enforce password strength on first entry
                password_a = getpass(prompt=' Password: ')
                try:
                    password_logic.enforce_strength(password_a)
                except password_logic.PasswordError as pe:
                    print(str(pe))
                else:
                    break

            password_b = getpass(prompt=' Confirm password: ')
            if password_a == password_b:
                password_hash = password_logic.hash_pwd_str(password_a)
                break
            else:
                print('Passwords entered do not match. Please try again.')

        try:
            new_staff_user = data_handling.Staff(username, password_hash, fullname)
        except validation.ValidationError as ve:
            print(f'Error in entered data as follows:\n {str(ve)}\nPlease try again.')
        else:
            try:
                staff_table.add_row(new_staff_user)
            except KeyError as ke:
                print(f'Error in entered data as follows:\n {str(ke)}\nPlease try again.')
            else:
                print(f'New staff user added successfully:\n {str(new_staff_user)}')
                break

    MAIN_DATABASE_OBJ.save_state_to_file(suffix=file_save_suffix)
    print('Tables successfully saved to txt files.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.format_help()
    parser.add_argument('-f', '--file-save-suffix',
                        type=str, metavar='SUFFIX',
                        help='optional suffix to add when loading files (use to load specific tables)',
                        default='')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', '--show-gui',
                       help='show GUI to log in to system as staff or student',
                       action='store_true')
    group.add_argument('-s', '--create-staff-account',
                       help='launch interactive command line to create a staff/admin account',
                       action='store_true')
    group.add_argument('-p', '--populate-tables',
                       help='launch interactive command line to create random test student data',
                       action='store_true')
    args = parser.parse_args()

    MAIN_DATABASE_OBJ = data_handling.Database()
    try:
        # loads last database state from file into memory
        MAIN_DATABASE_OBJ.load_state_from_file(suffix=args.file_save_suffix)
    except FileNotFoundError as fe:
        if args.file_save_suffix:
            raise fe
        else:
            # fixme: set up example databases to be loaded using readme instructions
            print('No existing complete database. New files will be created on program termination.')

    if args.show_gui:
        logging.debug('show-gui argument provided: creating tkinter instance')
        create_gui(args.file_save_suffix)
    elif args.create_staff_account:
        logging.debug('create-staff-account argument provided: launching command line function to create account')
        create_staff_account(args.file_save_suffix)
    elif args.populate_tables:
        logging.debug('populate-tables argument provided: launching command line function to generate test students')
        populate_tables.populate(args.file_save_suffix)
