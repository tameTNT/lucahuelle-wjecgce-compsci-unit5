import logging
import tkinter as tk
from tkinter import messagebox

from data_tables import data_handling

logging.basicConfig(filename='main_program.log',
                    filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)8s: %(message)s')


def close_window_call(db_obj: data_handling.Database):
    """
    TODO: docs and typing of close_window_call()
    :param db_obj:
    :return:
    """
    logging.debug('User pressed quit button')
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?\n"
                                      "This will save all stored data."):
        logging.debug('User chose to destroy window and exit program')
        # saves current database state from memory to file before closing
        db_obj.save_state_to_file()  # TODO: trial saving to file
        root.destroy()
    else:
        logging.debug('User chose not to exit')


if __name__ == '__main__':
    root = tk.Tk()
    main_database_obj = data_handling.Database()
    main_database_obj.load_state_from_file()  # loads last database state from file into memory
    logging.debug('WelcomeLoginWindow initialised')
    # TODO: trial loading from file using main_database_obj.load_state_from_file()
    # main_window = WelcomeLoginWindow(master=root, padx=10, pady=2)
    # root.protocol("WM_DELETE_WINDOW", lambda: close_window_call(main_database_obj))
    # root.mainloop()
