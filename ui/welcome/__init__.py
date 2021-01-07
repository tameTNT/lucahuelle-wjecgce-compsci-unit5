import tkinter.ttk as ttk


class WelcomeWindow:
    def __init__(self, master, padx=10, pady=5):
        self.master = master
        self.master.title("DofE Scheme Management")

        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack()

        self.welcome_message = ttk.Label(self.main_frame,
                                         text="Welcome to the DofE Scheme Management Application",
                                         justify="center")
        self.welcome_message.grid(row=0, column=0, columnspan=2, padx=padx, pady=pady)

        self.student_login = ttk.Button(self.main_frame,
                                        text='Student Login')
        self.student_login.grid(row=1, column=0, padx=padx, pady=pady)

        self.staff_login = ttk.Button(self.main_frame,
                                      text='Staff Login')
        self.staff_login.grid(row=1, column=1, padx=padx, pady=pady)
