import logging
import tkinter as tk
import tkinter.ttk as ttk

import ui
import ui.landing
import ui.student.enrollment_and_sections
from data_tables import data_handling


class StudentAwardDashboard(ui.GenericPage):
    page_name = 'Student Award Dashboard'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        self.logout_button = ttk.Button(self, text='Logout', command=self.logout)
        self.logout_button.pack(padx=self.padx, pady=self.pady)

        # all variable fields start with a null value before being updated
        # with student info when update_attributes is called
        self.welcome_text_var = tk.StringVar()
        self.welcome_text = ttk.Label(self, textvariable=self.welcome_text_var, justify='center',
                                      font=ui.HEADER_FONT)
        self.welcome_text.pack(padx=self.padx, pady=self.pady)

        self.current_level_var = tk.StringVar()
        self.current_level = ttk.Label(self, textvariable=self.current_level_var, justify='center')
        self.current_level.pack(padx=self.padx, pady=self.pady)

        # button only shown if student has not yet registered/fully enrolled
        # this button and following frame are not packed until the frame is shown to the user
        self.complete_enrollment_button = ttk.Button(self, text='Complete Enrollment',
                                                     command=self.enrol_fully)

        self.fully_enrolled_info_frame = ttk.Frame(self)
        # === section info frame contents - not shown if student not yet registered ===
        self.vol_title_var = tk.StringVar()
        self.vol_title = ttk.Label(self.fully_enrolled_info_frame,
                                   textvariable=self.vol_title_var,
                                   justify='center')
        self.vol_title.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        self.skill_title_var = tk.StringVar()
        self.skill_title = ttk.Label(self.fully_enrolled_info_frame,
                                     textvariable=self.skill_title_var,
                                     justify='center')
        self.skill_title.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.phys_title_var = tk.StringVar()
        self.phys_title = ttk.Label(self.fully_enrolled_info_frame,
                                    textvariable=self.phys_title_var,
                                    justify='center')
        self.phys_title.grid(row=0, column=2, padx=self.padx, pady=self.pady)

        self.title_separator = ttk.Separator(self.fully_enrolled_info_frame, orient='horizontal')
        self.title_separator.grid(row=1, columnspan=3, sticky='we', padx=self.padx, pady=self.pady)

        self.vol_status_var = tk.StringVar()
        self.volunteering_status = ttk.Label(self.fully_enrolled_info_frame,
                                             textvariable=self.vol_status_var,
                                             justify='center')
        self.volunteering_status.grid(row=2, column=0, padx=self.padx, pady=self.pady)

        self.skill_status_var = tk.StringVar()
        self.skill_status = ttk.Label(self.fully_enrolled_info_frame,
                                      textvariable=self.skill_status_var,
                                      justify='center')
        self.skill_status.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        self.phys_status_var = tk.StringVar()
        self.phys_status = ttk.Label(self.fully_enrolled_info_frame,
                                     textvariable=self.phys_status_var,
                                     justify='center')
        self.phys_status.grid(row=2, column=2, padx=self.padx, pady=self.pady)

        # TODO: section edit/submission buttons and rest of GUI for enrolled students

        # === end of frame ===

        self.student = None  # stores all student information for the window - updated below
        self.student_username = ''

        self.section_table = self.pager_frame.master_root.db. \
            get_table_by_name('SectionTable').row_dict

    def update_attributes(self, student: data_handling.Student, username: str) -> None:
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username
        self.page_name = f'{self.student_username} Award Dashboard'

        # === updates tkinter StringVar with new information received ===
        if self.student.fullname:  # registration complete
            if self.student.approved:  # teacher has approved enrolment
                self.welcome_text_var.set(f'Welcome, {self.student.fullname}!')
                self.complete_enrollment_button.pack_forget()
                self.fully_enrolled_info_frame.pack(padx=self.padx, pady=self.pady)
            else:  # pending teacher approval
                self.welcome_text_var.set(f'Welcome!\n Your teacher has not yet approved '
                                          f'your enrollment, {username}.')
                self.complete_enrollment_button.pack_forget()
                self.fully_enrolled_info_frame.pack_forget()

        else:  # if the student's details aren't complete, they have yet to register
            self.welcome_text_var.set(f'Welcome!\n'
                                      f'You have not yet completed your registration, {username}.')
            self.complete_enrollment_button.pack(padx=self.padx, pady=self.pady)
            self.fully_enrolled_info_frame.pack_forget()

        self.current_level_var.set(f'Current level: {self.student.award_level.capitalize()}')

        def str_days_to_months(str_days):
            return int(str_days) // 30

        # Goes through each section one by one and updates the GUI's labels
        for section_type, long_name in ui.SECTION_NAME_MAPPING.items():
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

        logging.info(f'Username "{self.student_username}" entered the student dashboard. '
                     f'They have {"already" if self.student.fullname else "not yet"} '
                     f'completed their enrollment.')

    def logout(self):
        """
        Logs the student out of the page - returns them to Welcome page
        """
        logging.info(f'Username "{self.student_username}" '
                     f'successfully logged out of student application')

        self.pager_frame.change_to_page(ui.landing.Welcome)

    def enrol_fully(self):
        self.pager_frame.change_to_page(
            destination_page=ui.student.enrollment_and_sections.Enrollment,
            student=self.student,
            username=self.student_username,
        )

    def edit_section(self, section_type_short):
        self.pager_frame.change_to_page(
            destination_page=ui.student.enrollment_and_sections.SectionInfo,
            student=self.student,
            username=self.student_username,
            section_type_short=section_type_short,
        )
