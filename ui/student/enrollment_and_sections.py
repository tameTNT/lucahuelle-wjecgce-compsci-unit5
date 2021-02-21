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
                                       font=ui.HEADING_FONT)
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
        ui.create_tooltip(self.phone_primary, 'Do not include plus signs or spaces')

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
        ui.create_tooltip(self.phone_emergency, 'Do not include plus signs or spaces')

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

        self.current_date = ttk.Label(self, text=f'Current Date: {date_logic.datetime_to_str()}')
        self.current_date.grid(row=3, column=0, padx=self.padx, pady=self.pady)

        self.complete_button = ttk.Button(self, text='Complete Enrollment',
                                          command=self.attempt_enrollment)
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

    def attempt_enrollment(self):
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
        # todo: consistency of buttons to quick navigate between pages

        self.header_var = tk.StringVar()
        self.header = ttk.Label(self, textvariable=self.header_var, font=ui.HEADING_FONT)
        self.header.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        # === detail frame ===  todo: version when section 'in progress'
        self.detail_frame = ttk.Frame(self)
        self.detail_frame.grid(row=0, rowspan=3, column=1, padx=self.padx, pady=self.pady)

        self.timescale_label = ttk.Label(self.detail_frame,
                                         text='Timescale (months):', justify='right')
        self.timescale_label.grid(row=0, column=0, pady=self.pady, sticky='e')

        # == radio buttons for timescale selection ==
        self.radio_button_frame = ttk.Frame(self.detail_frame)
        self.radio_button_frame.grid(row=0, column=1, columnspan=2, pady=self.pady, sticky='we')

        # Spreads out radio buttons evenly within frame
        self.radio_button_frame.grid_columnconfigure(0, weight=1)
        self.radio_button_frame.grid_columnconfigure(1, weight=1)
        self.radio_button_frame.grid_columnconfigure(2, weight=1)

        self.timescale_var = tk.StringVar()
        self.timescale_select_3 = ttk.Radiobutton(self.radio_button_frame, text='3',
                                                  variable=self.timescale_var, value='90',
                                                  command=self.date_update_validate)
        self.timescale_select_3.grid(row=0, column=0, pady=self.pady)

        self.timescale_select_6 = ttk.Radiobutton(self.radio_button_frame, text='6',
                                                  variable=self.timescale_var, value='180',
                                                  command=self.date_update_validate)
        self.timescale_select_6.grid(row=0, column=1, pady=self.pady)

        self.timescale_select_12 = ttk.Radiobutton(self.radio_button_frame, text='12',
                                                   variable=self.timescale_var, value='360',
                                                   command=self.date_update_validate)
        self.timescale_select_12.grid(row=0, column=2, pady=self.pady)
        # == end of radio button frame ==
        self.start_date_label = ttk.Label(self.detail_frame,
                                          text='Start date:', justify='right')
        self.start_date_label.grid(row=1, column=0, pady=self.pady, sticky='e')

        self.start_date_var = tk.StringVar()
        on_update_wrapper = self.pager_frame.master_root.tk_root.register(self.date_update_validate)
        self.start_date = ttk.Entry(self.detail_frame, width=10,
                                    textvariable=self.start_date_var,
                                    validate='all',  # calls validatecommand on any action with the widget
                                    validatecommand=on_update_wrapper)  # updates self.end_date_var based on entry
        self.start_date.grid(row=1, column=1, pady=self.pady, sticky='we')
        ui.create_tooltip(self.start_date, 'Enter in format YYYY/MM/DD')

        self.end_date_var = tk.StringVar()
        self.end_date = ttk.Label(self.detail_frame, textvariable=self.end_date_var)
        self.end_date.grid(row=1, column=2, pady=self.pady, sticky='we')

        # == activity info frame ==
        self.activity_info_frame = ttk.Labelframe(self.detail_frame, text='Activity Information')
        self.activity_info_frame.grid(row=2, column=0, columnspan=2, ipadx=self.padx, padx=self.padx, pady=self.pady)

        self.activity_type_label = ttk.Label(self.activity_info_frame, text='Type:', justify='right')
        self.activity_type_label.grid(row=0, column=0, pady=self.pady, sticky='e')

        self.activity_type_var = tk.StringVar()
        self.activity_type = ttk.Entry(self.activity_info_frame, textvariable=self.activity_type_var)
        self.activity_type.grid(row=0, column=1, pady=self.pady, sticky='we')

        self.activity_details_label = ttk.Label(self.activity_info_frame, text='Details:', justify='right')
        self.activity_details_label.grid(row=1, column=0, pady=self.pady, sticky='e')

        self.activity_details_scrollable_text = ttk.Frame(self.activity_info_frame)
        self.activity_details_scrollable_text.grid(row=1, column=1, pady=self.pady, sticky='we')
        self.activity_details_text = tk.Text(self.activity_details_scrollable_text, width=25, height=4,
                                             wrap='word', font=ui.TEXT_ENTRY_FONT)
        self.activity_details_text.grid(row=0, column=0, sticky='nesw')
        self.details_y_scroll = ttk.Scrollbar(self.activity_details_scrollable_text, orient='vertical',
                                              command=self.activity_details_text.yview)
        self.activity_details_text['yscrollcommand'] = self.details_y_scroll.set
        self.details_y_scroll.grid(row=0, column=1, sticky='ns')

        self.activity_goals_label = ttk.Label(self.activity_info_frame, text='Goals:', justify='right')
        self.activity_goals_label.grid(row=2, column=0, pady=self.pady, sticky='e')

        self.activity_goals_scrollable_text = ttk.Frame(self.activity_info_frame)
        self.activity_goals_scrollable_text.grid(row=2, column=1, pady=self.pady, sticky='we')
        self.activity_goals_text = tk.Text(self.activity_goals_scrollable_text, width=25, height=2,
                                           wrap='word', font=ui.TEXT_ENTRY_FONT)
        self.activity_goals_text.grid(row=0, column=0, sticky='nesw')
        self.goals_y_scroll = ttk.Scrollbar(self.activity_goals_scrollable_text, orient='vertical',
                                            command=self.activity_goals_text.yview)
        self.activity_goals_text['yscrollcommand'] = self.goals_y_scroll.set
        self.goals_y_scroll.grid(row=0, column=1, sticky='ns')
        # == end of self.activity_info_frame ==

        # == assessor info frame ==
        self.assessor_info_frame = ttk.Labelframe(self.detail_frame, text='Your Assessor')
        self.assessor_info_frame.grid(row=2, column=2, ipadx=self.padx, padx=self.padx, pady=self.pady)

        self.assessor_fullname_label = ttk.Label(self.assessor_info_frame, text='Full Name:', justify='right')
        self.assessor_fullname_label.grid(row=0, column=0, pady=self.pady, sticky='e')

        self.assessor_fullname_var = tk.StringVar()
        self.assessor_fullname = ttk.Entry(self.assessor_info_frame, textvariable=self.assessor_fullname_var)
        self.assessor_fullname.grid(row=0, column=1, pady=self.pady, sticky='we')

        self.assessor_phone_label = ttk.Label(self.assessor_info_frame, text='Phone number:', justify='right')
        self.assessor_phone_label.grid(row=1, column=0, pady=self.pady, sticky='e')

        self.assessor_phone_var = tk.StringVar()
        self.assessor_phone = ttk.Entry(self.assessor_info_frame, textvariable=self.assessor_phone_var)
        self.assessor_phone.grid(row=1, column=1, pady=self.pady, sticky='we')

        self.assessor_email_label = ttk.Label(self.assessor_info_frame, text='Email:', justify='right')
        self.assessor_email_label.grid(row=2, column=0, pady=self.pady, sticky='e')

        self.assessor_email_var = tk.StringVar()
        self.assessor_email = ttk.Entry(self.assessor_info_frame, textvariable=self.assessor_email_var)
        self.assessor_email.grid(row=2, column=1, pady=self.pady, sticky='we')
        # == end of self.assessor_info_frame ==

        # === end of self.detail_frame ===
        self.add_evidence_button = ttk.Button(self, text='Add Evidence',
                                              state='disabled')
        # todo: evidence functionality and tooltip to say why disabled
        self.add_evidence_button.grid(row=2, column=0, padx=self.padx, pady=self.pady)
        self.exit_button = ttk.Button(self, text='Submit section info',
                                      command=self.attempt_section_table_update)
        self.exit_button.grid(row=3, column=0, columnspan=3, padx=self.padx, pady=self.pady)

        self.student = None
        self.student_username = ''
        self.section_type_short = ''

    def update_attributes(self, student: data_handling.Student, username: str,
                          section_type_short: str):
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username
        self.section_type_short = section_type_short
        long_section_name = ui.SECTION_NAME_MAPPING[self.section_type_short]

        self.page_name = f'{self.student_username} {long_section_name} Details'

        self.header_var.set(f'{long_section_name} Details')

        # todo: disable radio buttons depending on level and timescale choices
        ui.create_tooltip(self.timescale_label, 'NB: Some options are disabled based on your award level\n'
                                                'and/or timescale choices in your other sections.')

        self.date_update_validate()  # clears end date label

    def back(self):
        """
        Returns the student to the dashboard page
        """
        self.pager_frame.change_to_page(
            destination_page=ui.student.StudentAwardDashboard,
            student=self.student,
            username=self.student_username,
        )

    def date_update_validate(self):
        """
        A 'validation' function so that the following code is executed
        on every update of the entry widget.
        Must return True for this validation aspect.
        """
        try:
            start_date = validation.validate_date(self.start_date_var.get(), 'Start date', '/')
            end_date = date_logic.calculate_end_date(int(self.timescale_var.get()), start_date)
            end_date = date_logic.datetime_to_str(end_date, '/')
        except (validation.ValidationError, ValueError):
            end_date = '----/--/--'

        self.end_date_var.set(f'➡ Expected end date: {end_date}')
        return True

    def attempt_section_table_update(self):
        # noinspection PyTypeChecker
        section_table: data_handling.SectionTable = self.pager_frame.master_root.db.get_table_by_name('SectionTable')
        try:
            new_id = section_table.get_new_key_id()
            if self.timescale_var.get():
                new_section_entry = data_handling.Section(
                    section_id=new_id,
                    section_type=self.section_type_short,
                    activity_start_date=self.start_date_var.get(),
                    activity_timescale=self.timescale_var.get(),
                    activity_type=self.activity_type_var.get(),
                    activity_details=self.activity_details_text.get('1.0', 'end').strip(),
                    activity_goals=self.activity_goals_text.get('1.0', 'end').strip(),
                    assessor_fullname=self.assessor_fullname_var.get(),
                    assessor_phone=self.assessor_phone_var.get().replace(' ', ''),
                    assessor_email=self.assessor_email_var.get(),
                    from_file=False,
                )
            else:
                raise validation.ValidationError('No timescale selected for section.')
        except validation.ValidationError as e:
            msg.showerror('Error with field data', str(e))
        else:
            section_table.add_row(new_section_entry)
            # Links student to section table
            self.student.__setattr__(f'{new_section_entry.section_type}_info_id',
                                     new_section_entry.section_id)

            msg.showinfo('Section information submission successful',
                         'Section information successfully submitted. '
                         'You can now start working on this section!')
            self.back()
