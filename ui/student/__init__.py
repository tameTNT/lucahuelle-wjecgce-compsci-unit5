import logging
import tkinter as tk
import tkinter.ttk as ttk

import ui
import ui.landing
import ui.student.enrollment
import ui.student.section_info
from data_tables import data_handling, SECTION_NAME_MAPPING


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
                                      font=ui.HEADING_FONT)
        self.welcome_text.pack(padx=self.padx, pady=self.pady)

        self.current_level_var = tk.StringVar()
        self.current_level = ttk.Label(self, textvariable=self.current_level_var,
                                       justify='center', font=ui.BOLD_CAPTION_FONT)
        self.current_level.pack(padx=self.padx, pady=self.pady)

        # button only shown if student has not yet registered/fully enrolled
        # this button and following frame are not packed until the frame is shown to the user
        self.complete_enrollment_button = ttk.Button(self, text='Complete Enrollment',
                                                     command=self.enrol_fully)

        # frame packed into window later depending on registration status
        self.fully_enrolled_info_frame = ttk.Frame(self)
        # === frame contents below only shown if student not yet registered ===

        # == frame containing info on each section of award ==
        self.section_info_frame = ttk.Labelframe(self.fully_enrolled_info_frame, text='Section progress')
        self.section_info_frame.pack(padx=self.padx, pady=self.pady)

        # Builds up GUI by section/column
        for col, section_type in enumerate(SECTION_NAME_MAPPING.keys()):
            # = Section title row =
            title_var_name = f'{section_type}_title_var'
            self.__setattr__(title_var_name, tk.StringVar())  # e.g. self.vol_title_var

            title_label_name = f'{section_type}_title_label'
            label_obj = ttk.Label(self.section_info_frame,
                                  textvariable=self.__getattribute__(title_var_name),
                                  justify='center')

            self.__setattr__(title_label_name, label_obj)  # e.g. self.vol_title_label
            self.__getattribute__(title_label_name).grid(row=0, column=col,
                                                         padx=self.padx, pady=self.pady)

            # = Section status row =
            status_var_name = f'{section_type}_status_var'
            self.__setattr__(status_var_name, tk.StringVar())  # e.g. self.vol_status_var

            status_label_name = f'{section_type}_status_label'
            label_obj = ttk.Label(self.section_info_frame,
                                  textvariable=self.__getattribute__(status_var_name),
                                  justify='center', font=ui.ITALIC_CAPTION_FONT)
            self.__setattr__(status_label_name, label_obj)  # e.g. self.vol_status_label
            self.__getattribute__(status_label_name).grid(row=2, column=col,
                                                          padx=self.padx, pady=self.pady)

            # = Section edit row =
            button_var_name = f'{section_type}_edit_button'
            # For explanation of why 'lambda x=section_type:...' is used
            # instead of just 'lambda:...' see:
            # https://stackoverflow.com/questions/10452770/python-lambdas-binding-to-local-values
            button_obj = ttk.Button(self.section_info_frame, text='Edit',
                                    command=lambda x=section_type: self.edit_section(x))

            self.__setattr__(button_var_name, button_obj)  # e.g. self.vol_edit_button
            self.__getattribute__(button_var_name).grid(row=3, column=col,
                                                        padx=self.padx, pady=self.pady)

        self.title_separator = ttk.Separator(self.section_info_frame, orient='horizontal')
        self.title_separator.grid(row=1, columnspan=3, sticky='we', padx=self.padx, pady=self.pady)
        # == end of self.section_info_frame ==

        # == expedition info frame contents ==
        self.expedition_frame = ttk.Labelframe(self.fully_enrolled_info_frame, text='Expedition')
        self.expedition_frame.pack(padx=self.padx, pady=self.pady)

        # todo: expedition info frame in Student overview page
        self.temp_expedition_label = ttk.Label(self.expedition_frame, text='Temp expedition text')
        self.temp_expedition_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        # == end of self.expedition_frame contents ==

        # == calendar frame contents ==
        self.calendar_frame = ttk.Labelframe(self.fully_enrolled_info_frame, text='Calendar')
        self.calendar_frame.pack(padx=self.padx, pady=self.pady)

        # todo: calendar info frame in Student overview page
        self.temp_expedition_label = ttk.Label(self.calendar_frame, text='Temp calendar text')
        self.temp_expedition_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        # == end of self.calendar_frame contents ==

        # === end of self.fully_enrolled_info_frame contents ===

        self.student = None  # stores all student information for the window - updated below
        self.student_username = ''

        db = self.pager_frame.master_root.db
        # noinspection PyTypeChecker
        self.student_table: data_handling.StudentTable = db.get_table_by_name('StudentTable')
        # noinspection PyTypeChecker
        self.section_table: data_handling.SectionTable = db.get_table_by_name('SectionTable')

    def update_attributes(self, student: data_handling.Student, username: str) -> None:
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username
        self.page_name = f'{self.student_username} - Award Dashboard'

        # === updates tkinter StringVar with new information received ===
        if self.student.fullname:  # registration complete
            if self.student.is_approved:  # teacher has approved enrolment
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

        # Goes through each section one by one and updates the GUI's labels
        for section_type, long_name in SECTION_NAME_MAPPING.items():
            # fetches the tk.StringVar attributes to update with new info
            title_var = self.__getattribute__(f'{section_type}_title_var')
            status_var = self.__getattribute__(f'{section_type}_status_var')

            # self.student.vol_info_id, self.student.skill_info_id, self.student.phys_info_id
            section_obj = self.student_table.get_student_section_obj(
                self.student.student_id, section_type, self.section_table
            )

            if section_obj:
                # if get_student_section_obj() isn't None then the table exists and the section has been started
                section_length = int(section_obj.activity_timescale) // 30
                title_var.set(f'{long_name}\n({section_length} months)')
                status_var.set(section_obj.activity_status)
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
            destination_page=ui.student.enrollment.Enrollment,
            student=self.student,
            username=self.student_username,
        )

    def edit_section(self, section_type_short):
        self.pager_frame.change_to_page(
            destination_page=ui.student.section_info.SectionInfo,
            student=self.student,
            username=self.student_username,
            section_type_short=section_type_short,
        )
