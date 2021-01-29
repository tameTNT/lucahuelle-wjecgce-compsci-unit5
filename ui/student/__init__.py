from __future__ import annotations

import logging
import tkinter as tk
import tkinter.ttk as ttk

import ui
import ui.landing
from data_tables import data_handling


class StudentAwardDashboard(ui.GenericPage):
    page_name = 'Student Award Dashboard'

    def __init__(self, pager_frame: ui.PagedMainFrame, student: data_handling.Student = None):
        super().__init__(pager_frame=pager_frame)

        # starts with a null value before being updated with student info below
        self.student_name_welcome = tk.StringVar(value='Hi Null!')
        self.welcome_text = ttk.Label(self, textvariable=self.student_name_welcome,
                                      justify='center')
        self.welcome_text.grid(row=0, column=0, columnspan=3, padx=self.padx, pady=self.pady)

        self.logout_button = ttk.Button(self, text='Logout', command=self.logout)
        self.logout_button.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        self.student = student  # stores all student information for the window
        self.student_username = ''

    def update_attributes(self, student: data_handling.Student, username: str) -> None:
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username

        # updates tkinter StringVars with new information received
        self.student_name_welcome.set(f'Hi {self.student.fullname}!')

    def logout(self):
        """
        Logs the student out of the page - returns them to Welcome page
        """
        logging.info(f'Username "{self.student_username}" '
                     f'successfully logged out of student application')

        self.pager_frame.change_to_page(ui.landing.Welcome)
