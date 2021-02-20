import logging
import tkinter as tk
from tkinter import font
from tkinter import messagebox

import ui.landing
import ui.student
from data_tables import data_handling
from ui import RootWindow

# todo: args parser to create admin accounts
#  -gui argument for default operation, update README

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
        logging.debug('User chose to destroy window and exit program')
        # saves current database state from memory to file before closing
        db_obj.save_state_to_file()
        tk_root.destroy()  # closes tkinter window
    else:
        logging.debug('User chose not to exit')


if __name__ == '__main__':
    root = tk.Tk()
    main_database_obj = data_handling.Database()
    main_database_obj.load_state_from_file()  # loads last database state from file into memory

    # some font constants set here as Tk needs to be initialised to use nametofont()
    font_obj = font.nametofont('TkCaptionFont')
    font_obj['size'], font_obj['slant'] = 10, 'italic'
    # can't just assign font_obj as options edited below again
    ui.ITALIC_CAPTION_FONT = font.Font(**font_obj.actual())
    font_obj['weight'], font_obj['slant'] = 'bold', 'roman'
    ui.BOLD_CAPTION_FONT = font.Font(**font_obj.actual())

    main_window = RootWindow(tk_root=root, db=main_database_obj)  # initialises tkinter root/base

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
    root.protocol("WM_DELETE_WINDOW", lambda: close_window_call(main_database_obj, root))
    root.mainloop()
