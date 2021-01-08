import logging
import tkinter as tk
import tkinter.ttk as ttk


# By CC attribution, this 'page-based approach' is based on the framework provided at
# https://pythonprogramming.net/change-show-new-frame-tkinter/


class WelcomeLoginWindow:
    def __init__(self, master, padx=10, pady=5):
        """
        Initialises a WelcomeLoginWindow object: the main tkinter window which contains
        the 'pages'/frames for student and staff login operations.
        The user can navigate the different login pages using buttons.
        These buttons call the change_page method which cycles through the layered frames
        by elevating them to the top of the tkinter window.
        :param master: tk.Tk() object to act as tkinter root
        :param padx: padx value to use in .grid() calls
        :param pady: pady value to use in .grid() calls
        """
        self.master = master
        self.master.title('DofE - Login')

        container_frame = ttk.Frame(self.master)
        container_frame.pack(side='top', fill='both', expand=True)
        container_frame.grid_rowconfigure(0, weight=1)
        container_frame.grid_columnconfigure(0, weight=1)

        # a dictionary of all the page objects/frames to be contained in the tkinter window
        self.page_frames = dict()

        # goes through each page object in turn and creates their frame in the window
        for Page in (WelcomePage, StudentLoginPage, StaffLoginPage):
            page_frame = Page(container_frame, self, padx, pady)
            self.page_frames[Page] = page_frame  # adds page object to frame dictionary
            page_frame.grid(row=0, column=0, sticky='nsew')

        self.change_page(WelcomePage)  # sets the initial page to WelcomePage

    def change_page(self, destination_page):
        """Changes the page displayed in the tkinter window to destination_page"""
        logging.debug('User changed displayed page in WelcomeLoginWindow')
        next_frame = self.page_frames[destination_page]
        next_frame.tkraise()  # elevates the frame to the top of frame stack/'changes pages'


class WelcomePage(ttk.Frame):
    def __init__(self, parent_tk_obj, controller_obj, padx, pady):
        """
        The initial landing page of the application
        :param parent_tk_obj: a frame object in which to pack/grid this page/frame object
        :param controller_obj: the parent object which is in charge of managing
        which page is displayed. Has a change_page method
        :param padx: padx value to use in .grid() calls
        :param pady: pady value to use in .grid() calls
        """
        ttk.Frame.__init__(self, master=parent_tk_obj)

        self.message = ttk.Label(self,
                                 text='Welcome to the\n'
                                      'DofE Scheme Management Application.\n'
                                      'Please select your login method:',
                                 justify='center')
        self.message.grid(row=0, column=0, columnspan=2, padx=padx, pady=pady)

        # button calls the change_page method of controller_obj to change to the StudentLoginPage
        self.student_login = ttk.Button(self,
                                        text='Student Login',
                                        command=lambda:
                                        controller_obj.change_page(StudentLoginPage))
        self.student_login.grid(row=1, column=0, padx=padx, pady=pady)

        # button calls the change_page method of controller_obj to change to the StaffLoginPage
        self.staff_login = ttk.Button(self,
                                      text='Staff Login',
                                      command=lambda:
                                      controller_obj.change_page(StaffLoginPage))
        self.staff_login.grid(row=1, column=1, padx=padx, pady=pady)


class LoginPage(ttk.Frame):
    def __init__(self, parent_tk_obj, controller_obj, padx, pady, is_student):
        """
        The base class for the login page objects of StudentLoginPage and StaffLoginPage.
        Allows the user to return back to the welcome screen
        or enter their username and password in order to access the system.
        :param parent_tk_obj: a frame object in which to pack/grid this page/frame object
        :param controller_obj: the parent object which is in charge of managing
        which page is displayed. Has a change_page method
        :param padx: padx value to use in .grid() calls
        :param pady: pady value to use in .grid() calls
        :param is_student: boolean to differentiate between StudentLoginPage and StaffLoginPage
        objects' initialisation.Determines which part of the application the user is directed to
        """
        ttk.Frame.__init__(self, master=parent_tk_obj)

        self.back_button = ttk.Button(self, text='Back',
                                      command=lambda: controller_obj.change_page(WelcomePage))
        self.back_button.grid(row=0, column=0, padx=padx, pady=pady, sticky='w')

        self.message = ttk.Label(self,
                                 text='Please enter your username and password.',
                                 justify='center')
        self.message.grid(row=1, column=0, columnspan=2, padx=padx, pady=pady)

        self.username_label = ttk.Label(self, text='Username:', justify='right')
        self.username_label.grid(row=2, column=0, pady=pady, sticky='e')

        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self, textvariable=self.username_var)
        self.username_entry.grid(row=2, column=1, pady=pady, sticky='w')

        self.password_label = ttk.Label(self, text='Password:', justify='right')
        self.password_label.grid(row=3, column=0, pady=pady, sticky='e')
        # TODO: hidden password entry and password reveal/view button

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self, textvariable=self.password_var)
        self.password_entry.grid(row=3, column=1, pady=pady, sticky='w')

        self.login_button = ttk.Button(self, text='Login', command=self.login)
        self.login_button.grid(row=4, column=1, padx=padx, pady=pady, sticky='e')

        self.is_student = is_student

    def login(self):
        if self.is_student:
            logging.info('A student attempted to log in')
        else:
            logging.info('A staff member attempted to log in')


class StudentLoginPage(LoginPage):
    def __init__(self, *args, is_student=True):
        """The login page for students - is_student=True"""
        LoginPage.__init__(self, *args, is_student)


class StaffLoginPage(LoginPage):
    def __init__(self, *args, is_student=False):
        """The login page for staff - is_student=False"""
        LoginPage.__init__(self, *args, is_student)
