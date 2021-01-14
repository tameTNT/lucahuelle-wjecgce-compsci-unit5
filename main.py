import logging
import tkinter as tk
from tkinter import messagebox

from data_tables import data_handling
from ui.welcome import WelcomeLoginWindow

logging.basicConfig(filename='main_program.log',
                    filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)8s: %(message)s')


def close_window_call(db_obj: data_handling.Database, tk_root: tk.Tk) -> None:
    """
    This function is activated by the WM_DELETE_WINDOW protocol (i.e. when the user presses X).
    It makes the user confirm they want to close the program and saves program data.

    :param db_obj: the main Database object to which the current database state should be saved from
    :param tk_root: tkinter Tk() object which is main base window that user wanted to close
    """
    logging.debug('User pressed quit button')
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?\n"
                                      "This will save all stored data."):
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
    logging.debug('WelcomeLoginWindow initialised')
    main_window = WelcomeLoginWindow(master=root, db=main_database_obj, padx=10, pady=2)
    root.protocol("WM_DELETE_WINDOW", lambda: close_window_call(main_database_obj, root))
    root.mainloop()
