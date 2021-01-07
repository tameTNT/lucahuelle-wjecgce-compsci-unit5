import logging
import tkinter as tk
from tkinter import messagebox

from ui.welcome import WelcomeWindow

logging.basicConfig(filename='main_program.log',
                    filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)8s: %(message)s')


def close_window_call():
    logging.debug('User pressed quit button')
    if messagebox.askokcancel("Quit",
                              "Are you sure you want to quit?\n"
                              "This will save all stored data."):
        logging.debug('User chose to destroy window and exit program')
        root.destroy()
    else:
        logging.debug('User chose not to exit')


if __name__ == '__main__':
    root = tk.Tk()
    logging.debug('WelcomeWindow initialised')
    main_window = WelcomeWindow(master=root, padx=10, pady=2)
    root.protocol("WM_DELETE_WINDOW", close_window_call)
    root.mainloop()
