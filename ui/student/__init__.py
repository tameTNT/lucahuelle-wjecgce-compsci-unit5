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

        self.logout_button = ttk.Button(self, text='Logout', command=self.logout)
        self.logout_button.grid(row=0, column=0, columnspan=3, padx=self.padx, pady=self.pady)

        # all variable fields start with a null value before being updated
        # with student info when update_attributes is called
        self.welcome_text_var = tk.StringVar(value='Null')
        self.welcome_text = ttk.Label(self, textvariable=self.welcome_text_var, justify='center')
        self.welcome_text.grid(row=1, column=0, columnspan=3, padx=self.padx, pady=self.pady)

        self.current_level_var = tk.StringVar(value='Null')
        self.current_level = ttk.Label(self, textvariable=self.current_level_var, justify='center')
        self.current_level.grid(row=2, column=0, columnspan=3, padx=self.padx, pady=self.pady)

        self.vol_title_var = tk.StringVar()
        self.vol_title = ttk.Label(self,
                                   textvariable=self.vol_title_var,
                                   justify='center')
        self.vol_title.grid(row=3, column=0, padx=self.padx, pady=self.pady)

        self.skill_title_var = tk.StringVar()
        self.skill_title = ttk.Label(self,
                                     textvariable=self.skill_title_var,
                                     justify='center')
        self.skill_title.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.phys_title_var = tk.StringVar()
        self.phys_title = ttk.Label(self,
                                    textvariable=self.phys_title_var,
                                    justify='center')
        self.phys_title.grid(row=3, column=2, padx=self.padx, pady=self.pady)

        self.title_separator = ttk.Separator(self, orient='horizontal')
        self.title_separator.grid(row=4, columnspan=3, sticky='we', padx=self.padx, pady=self.pady)

        self.vol_status_var = tk.StringVar()
        self.volunteering_status = ttk.Label(self,
                                             textvariable=self.vol_status_var,
                                             justify='center')
        self.volunteering_status.grid(row=5, column=0, padx=self.padx, pady=self.pady)

        self.skill_status_var = tk.StringVar()
        self.skill_status = ttk.Label(self,
                                      textvariable=self.skill_status_var,
                                      justify='center')
        self.skill_status.grid(row=5, column=1, padx=self.padx, pady=self.pady)

        self.phys_status_var = tk.StringVar()
        self.phys_status = ttk.Label(self,
                                     textvariable=self.phys_status_var,
                                     justify='center')
        self.phys_status.grid(row=5, column=2, padx=self.padx, pady=self.pady)
        # TODO: section edit/submission buttons

        self.student = student  # stores all student information for the window
        self.student_username = ''

        self.section_table = self.pager_frame.master_root.db. \
            get_table_by_name('SectionTable').row_dict

    def update_attributes(self, student: data_handling.Student, username: str) -> None:
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username
        self.page_name = f'{self.student_username} Award Dashboard'

        # === updates tkinter StringVars with new information received ===
        self.welcome_text_var.set(f'Welcome, {self.student.fullname}')
        self.current_level_var.set(f'Current level: {self.student.award_level.capitalize()}')

        def str_days_to_months(str_days):
            return int(str_days) // 30

        section_name_map = {'vol': 'Volunteering', 'skill': 'Skill', 'phys': 'Physical'}
        # Goes through each section one by one and updates the GUI's labels
        for section_type, long_name in section_name_map.items():
            # fetches the tk.StringVar attributes to update with new info

            # self.student.vol_info_id, self.student.skill_info_id, self.student.phys_info_id
            section_id = self.student.__getattribute__(f'{section_type}_info_id')

            # self.vol_title_var, self.skill_title_var, self.phys_title_var
            title_var = self.__getattribute__(f'{section_type}_title_var')

            # self.vol_status_var, self.skill_status_var, self.phys_status_var
            status_var = self.__getattribute__(f'{section_type}_status_var')

            if section_id:  # if the link between tables exists then the section has been started
                section_length = str_days_to_months(self.section_table[section_id].activity_length)
                title_var.set(f'{long_name} ({section_length})')
                status_var.set(self.section_table[section_id].activity_status)
            else:
                title_var.set(long_name)
                status_var.set('Not started')

    def logout(self):
        """
        Logs the student out of the page - returns them to Welcome page
        """
        logging.info(f'Username "{self.student_username}" '
                     f'successfully logged out of student application')

        self.pager_frame.change_to_page(ui.landing.Welcome)
