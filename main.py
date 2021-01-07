import tkinter as tk
from tkinter import messagebox

from ui.welcome import WelcomeWindow


def close_window_call():
    if messagebox.askokcancel("Quit",
                              "Are you sure you want to quit?\n"
                              "This will save all stored data."):
        root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    main_window = WelcomeWindow(master=root, padx=10, pady=2)
    root.protocol("WM_DELETE_WINDOW", close_window_call)
    root.mainloop()
