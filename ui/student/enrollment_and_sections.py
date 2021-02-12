import logging
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.ttk as ttk

import processes
import ui
from data_tables import data_handling
from processes import date_logic, validation


class Enrollment(ui.GenericPage):
    page_name = 'Student Award Enrollment'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        self.back_button = ttk.Button(self, text='Back', command=self.back)
        self.back_button.grid(row=0, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.sign_up_label = ttk.Label(self, text='Complete Enrollment',
                                       font=ui.HEADER_FONT)
        self.sign_up_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        self.existing_info_frame = ttk.Frame(self)
        self.existing_info_frame.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        # === existing_info_frame contents ===
        for label_name in ('student_id', 'centre_id', 'award_level', 'year_group'):
            var_name = f'{label_name}_var'
            self.__setattr__(var_name, tk.StringVar())  # e.g. self.student_id_var

            label_obj = ttk.Label(self.existing_info_frame,
                                  textvariable=self.__getattribute__(var_name))
            self.__setattr__(label_name, label_obj)  # e.g. self.student_id
            self.__getattribute__(label_name).pack(padx=self.padx, pady=self.pady)
        # === end of frame ===

        # === info_submission_frame contents ===
        self.info_submission_frame = ttk.Frame(self)
        self.info_submission_frame.grid(row=2, column=1, padx=self.padx, pady=self.pady)

        # -full name entry
        self.full_name_label = ttk.Label(self.info_submission_frame,
                                         text='Full Name:', justify='right')
        self.full_name_label.grid(row=0, column=0, pady=self.pady, sticky='e')

        self.full_name_var = tk.StringVar()
        self.full_name_entry = ttk.Entry(self.info_submission_frame,
                                         textvariable=self.full_name_var)
        self.full_name_entry.grid(row=0, column=1, pady=self.pady, sticky='we')

        # -gender selection
        self.gender_selection_label = ttk.Label(self.info_submission_frame,
                                                text='Gender:', justify='right')
        self.gender_selection_label.grid(row=1, column=0, pady=self.pady, sticky='e')

        self.gender_selection_var = tk.StringVar()
        self.gender_selection = ttk.Combobox(self.info_submission_frame,
                                             state='readonly',
                                             values=('Male', 'Female', 'Other', 'PNTS'),
                                             textvariable=self.gender_selection_var)
        self.gender_selection.grid(row=1, column=1, pady=self.pady, sticky='we')
        ui.create_tooltip(self.gender_selection, 'PNTS = Prefer not to say')

        # -date of birth entry
        self.date_of_birth_label = ttk.Label(self.info_submission_frame, text='Date of Birth:')
        self.date_of_birth_label.grid(row=2, column=0, pady=self.pady, sticky='e')

        self.date_of_birth_var = tk.StringVar()
        self.date_of_birth = ttk.Entry(self.info_submission_frame,
                                       textvariable=self.date_of_birth_var)
        self.date_of_birth.grid(row=2, column=1, pady=self.pady, sticky='we')
        ui.create_tooltip(self.date_of_birth, 'Enter in format YYYY/MM/DD')

        # -address
        self.address_label = ttk.Label(self.info_submission_frame, text='Address:')
        self.address_label.grid(row=3, column=0, pady=self.pady, sticky='e')

        self.address_var = tk.StringVar()
        self.address = ttk.Entry(self.info_submission_frame,
                                 textvariable=self.address_var)
        self.address.grid(row=3, column=1, pady=self.pady, sticky='we')

        # -phone (new column)
        self.phone_primary_label = ttk.Label(self.info_submission_frame, text='Phone number:')
        self.phone_primary_label.grid(row=0, column=2, pady=self.pady, sticky='e')

        self.phone_primary_var = tk.StringVar()
        self.phone_primary = ttk.Entry(self.info_submission_frame,
                                       textvariable=self.phone_primary_var)
        self.phone_primary.grid(row=0, column=3, pady=self.pady, sticky='we')
        ui.create_tooltip(self.phone_primary, "Do not include '+'s or spaces")

        # -email
        self.email_label = ttk.Label(self.info_submission_frame, text='Email address:')
        self.email_label.grid(row=1, column=2, pady=self.pady, sticky='e')

        self.email_var = tk.StringVar()
        self.email = ttk.Entry(self.info_submission_frame,
                               textvariable=self.email_var)
        self.email.grid(row=1, column=3, pady=self.pady, sticky='we')

        # -emergency phone contact
        self.phone_emergency_label = ttk.Label(self.info_submission_frame,
                                               text='Emergency phone number:')
        self.phone_emergency_label.grid(row=2, column=2, pady=self.pady, sticky='e')

        self.phone_emergency_var = tk.StringVar()
        self.phone_emergency = ttk.Entry(self.info_submission_frame,
                                         textvariable=self.phone_emergency_var)
        self.phone_emergency.grid(row=2, column=3, pady=self.pady, sticky='we')
        ui.create_tooltip(self.phone_emergency, "Do not include '+'s or spaces")

        # -primary language
        self.language_selection_label = ttk.Label(self.info_submission_frame,
                                                  text='Primary Language:')
        self.language_selection_label.grid(row=3, column=2, pady=self.pady, sticky='e')

        self.language_selection_var = tk.StringVar()
        self.language_selection = ttk.Combobox(self.info_submission_frame,
                                               state='readonly',
                                               values=('English', 'Welsh'),
                                               textvariable=self.language_selection_var)
        self.language_selection.grid(row=3, column=3, pady=self.pady, sticky='we')
        # === end of frame ===

        self.current_date = ttk.Label(self, text=f'Current Date: {date_logic.datetime_to_str()}',
                                      font=ui.CAPTION_FONT)
        self.current_date.grid(row=3, column=0, padx=self.padx, pady=self.pady)

        self.complete_button = ttk.Button(self, text='Complete Enrollment',
                                          command=self.complete_enrollment)
        self.complete_button.grid(row=3, column=1, padx=self.padx, pady=self.pady)

        self.student = None
        self.student_username = ''

    def update_attributes(self, student: data_handling.Student, username: str) -> None:
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username

        for attr_name in ('student_id', 'centre_id', 'award_level', 'year_group'):
            # self.student.student_id, self.student.centre_id,
            # self.student.award_level, self.student.year_group
            current_val = self.student.__getattribute__(attr_name)

            # self.student_id_var, self.centre_id_var,
            # self.award_level_var, self.year_group_var
            tk_label_var = self.__getattribute__(f'{attr_name}_var')

            tk_label_var.set(f'{processes.make_readable_name(attr_name)}: '
                             f'{str(current_val).capitalize()}')

        # sets default values for fields
        self.date_of_birth_var.set('YYYY/MM/DD')
        self.gender_selection_var.set('Female')
        self.language_selection_var.set('English')

    def back(self):
        """
        Returns the student to the dashboard page
        """
        self.pager_frame.change_to_page(
            destination_page=ui.student.StudentAwardDashboard,
            student=self.student,
            username=self.student_username,
        )

    def complete_enrollment(self):
        try:
            self.student.complete_enrolment(
                fullname=self.full_name_var.get(),
                gender=self.gender_selection_var.get().lower(),
                date_of_birth=self.date_of_birth_var.get(),
                address=self.address_var.get(),
                phone_primary=self.phone_primary_var.get().replace(' ', ''),  # remove spaces
                email_primary=self.email_var.get(),
                phone_emergency=self.phone_emergency_var.get().replace(' ', ''),
                primary_lang=self.language_selection_var.get().lower(),
            )
        except validation.ValidationError as e:
            msg.showerror('Error with field data', str(e))
        else:
            msg.showinfo('Enrollment successful', 'Information submitted to staff for approval.')
            self.back()


class SectionInfo(ui.GenericPage):
    page_name = 'Student Section Details'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        # todo: Section submission/editing and evidence upload pages
        self.back_button = ttk.Button(self, text='Back', command=self.back)
        self.back_button.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        self.header_var = tk.StringVar()
        self.header = ttk.Label(self, textvariable=self.header_var, font=ui.HEADER_FONT)
        self.header.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        self.student = None
        self.student_username = ''
        self.section_type_short = ''

    def update_attributes(self, student: data_handling.Student, username: str,
                          section_type_short: str):
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username
        self.section_type_short = section_type_short

        self.page_name = f'{self.student_username} Section Details'

        self.header_var.set(f'{ui.SECTION_NAME_MAPPING[self.section_type_short]}')

    def back(self):
        """
        Returns the student to the dashboard page
        """
        self.pager_frame.change_to_page(
            destination_page=ui.student.StudentAwardDashboard,
            student=self.student,
            username=self.student_username,
        )

    def attempt_section_table_update(self):
        try:
            new_section_entry = None  # data_handling.Section()  # todo: get section input arguments
        except validation.ValidationError as e:
            msg.showerror('Error with field data', str(e))
        else:
            self.pager_frame.master_root.db.get_table_by_name('SectionTable') \
                .add_row(new_section_entry)
            msg.showinfo('Section information submission successful',
                         'Section information successfully submitted. '
                         'You can now start work on this section!')
            self.back()
