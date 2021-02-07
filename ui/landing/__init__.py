import logging
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.ttk as ttk

import ui
import ui.student
from processes import password_logic


class Welcome(ui.GenericPage):
    # The first page the user sees
    # The welcome landing page where they can select their login type (student/staff)

    page_name = 'Welcome'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        self.message = ttk.Label(self,
                                 text='Welcome to the\n'
                                      'DofE Scheme Management Application.\n\n'
                                      'Please select your login method:',
                                 justify='center')
        self.message.grid(row=0, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        # button calls the change_to_page method of the pager_frame to change view to StudentLogin
        self.student_login = ttk.Button(self,
                                        text='Student Login',
                                        command=lambda:
                                        self.pager_frame.change_to_page(StudentLogin))
        self.student_login.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        # button calls the change_to_page method of the pager_frame to change view to StaffLogin
        self.staff_login = ttk.Button(self,
                                      text='Staff Login',
                                      command=lambda:
                                      self.pager_frame.change_to_page(StaffLogin))
        self.staff_login.grid(row=1, column=1, padx=self.padx, pady=self.pady)


class Login(ui.GenericPage):
    # Set by child classes.
    # Determines where the user is directed to on a successful login.
    is_student: bool

    def __init__(self, pager_frame: ui.PagedMainFrame):
        """
        The base class for the login page objects of StudentLogin and StaffLogin.
        Allows the user to return back to the landing screen
        or enter their username and password in order to access each respective system.
        """
        super().__init__(pager_frame=pager_frame)

        self.back_button = ttk.Button(self, text='Back',
                                      command=self.back)
        self.back_button.grid(row=0, column=0, padx=self.padx, pady=self.pady, sticky='w')

        self.user_type_label = ttk.Label(self,
                                         text=f'{"Student" if self.is_student else "Staff"} Login',
                                         font='TkHeadingFont 15')
        self.user_type_label.grid(row=1, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        if self.is_student:
            login_message = 'These will be given to you by your teacher.'
        else:
            login_message = 'Contact the system admin to create an account.'

        self.message = ttk.Label(
            self,
            text=f'Please enter your username and password.\n\n{login_message}',
            justify='center', font='TkCaptionFont 10'
        )
        self.message.grid(row=2, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.user_detail_frame = ttk.Frame(self)
        self.user_detail_frame.grid(row=3, column=0, columnspan=2, pady=self.pady)
        # === username/password entry and show/hide button frame contents ===
        self.username_label = ttk.Label(self.user_detail_frame, text='Username:', justify='right')
        self.username_label.grid(row=0, column=0, pady=self.pady, sticky='e')

        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.user_detail_frame, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1, columnspan=2, pady=self.pady, sticky='we')

        self.password_label = ttk.Label(self.user_detail_frame, text='Password:', justify='right')
        self.password_label.grid(row=1, column=0, pady=self.pady, sticky='e')

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.user_detail_frame,  # \u2022 is a unicode bullet pt/dot
                                        textvariable=self.password_var, show='\u2022')
        self.password_entry.grid(row=1, column=1, sticky='we')

        self.show_pwd_button = ttk.Button(self.user_detail_frame, text='👁',
                                          width=2, command=self.toggle_show_password)
        self.show_pwd_button.grid(row=1, column=2, sticky='w')
        ui.create_tooltip(self.show_pwd_button, 'Show/Hide password')
        # === end of frame ===

        self.login_button = ttk.Button(self, text='Login', command=self.login)
        self.login_button.grid(row=4, column=1, padx=self.padx, pady=self.pady, sticky='e')

    def toggle_show_password(self):
        """
        Show/hide password with unicode dot characters by changing Entry widget's show option
        """
        if self.password_entry['show'] == '\u2022':  # password currently hid
            self.password_entry.config(show='')  # reveal password
        else:  # password currently revealed
            self.password_entry.config(show='\u2022')

    def login(self):
        """
        Gets user's input and verifies their login details.
        Automatically advances application to appropriate page
        (for student or for staff member)
        """
        input_username = self.username_var.get()
        input_password = self.password_var.get()

        db = self.pager_frame.master_root.db  # gets database obj from main root of application
        if self.is_student:
            logging.debug(f'A student attempted to log in with username "{input_username}"')

            login_username_dict = db.get_table_by_name('StudentLoginTable').row_dict
            if input_username in login_username_dict.keys():  # if username is valid, verifies pwd
                if password_logic.verify_pwd_str(input_password,
                                                 login_username_dict[input_username].password_hash):
                    logging.info(f'Username "{input_username}" '
                                 f'successfully logged into student application')

                    user_id = login_username_dict[input_username].student_id
                    student_dict = db.get_table_by_name('StudentTable').row_dict
                    # gets Student obj specified by logged in username
                    logged_in_student = student_dict[user_id]

                    # changes page appropriately, providing StudentAwardDashboard
                    # frame with the Student obj information to update text
                    self.pager_frame.change_to_page(
                        destination_page=ui.student.StudentAwardDashboard,
                        student=logged_in_student,
                        username=input_username,
                    )
                    return  # ends function so error below is not displayed

            msg.showerror('Login Failed', 'Username and/or password incorrect')
        else:
            # TODO: password verification for staff - way to merge with above code?
            logging.debug(f'A staff member attempted to log in with username "{input_username}"')
            return

    def back(self):
        """
        Returns the user back to the Welcome page after resetting the pwd visibility
        """
        self.password_entry.config(show='\u2022')
        self.pager_frame.change_to_page(Welcome)


class StudentLogin(Login):
    """
    The login page modified for students
    """
    page_name = 'Student Login'
    is_student = True


class StaffLogin(Login):
    """
    The login page modified for staff
    """
    page_name = 'Staff Login'
    is_student = False
