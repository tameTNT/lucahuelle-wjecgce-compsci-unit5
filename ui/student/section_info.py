import logging
import os
import shutil
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as msg
import tkinter.ttk as ttk
from pathlib import Path

import ui
from data_tables import data_handling
from processes import datetime_logic, validation


class SectionInfo(ui.GenericPage):
    page_name = 'Student Section Details'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        self.back_button = ttk.Button(self, text='Back', command=self.back)
        self.back_button.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        # wouldbenice: consistency of buttons to quick navigate between pages

        self.header_var = tk.StringVar()
        self.header = ttk.Label(self, textvariable=self.header_var, font=ui.HEADING_FONT)
        self.header.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        # === detail frame ===
        self.detail_frame = ttk.Frame(self)
        self.detail_frame.grid(row=0, rowspan=3, column=1, padx=self.padx, pady=self.pady)

        self.timescale_label = ttk.Label(self.detail_frame,
                                         text='Timescale (months):', justify='right')
        self.timescale_label.grid(row=0, column=0, pady=self.pady, sticky='e')

        # == radio buttons for timescale selection ==
        self.radiobutton_frame = ttk.Frame(self.detail_frame)
        self.radiobutton_frame.grid(row=0, column=1, columnspan=2, pady=self.pady, sticky='we')
        ui.create_tooltip(self.radiobutton_frame, 'NB: Some options may be disabled based on your award level\n'
                                                  'and/or timescale choices in your other sections.')

        # Spreads out radio buttons evenly within frame
        self.radiobutton_frame.grid_columnconfigure(0, weight=1)
        self.radiobutton_frame.grid_columnconfigure(1, weight=1)
        self.radiobutton_frame.grid_columnconfigure(2, weight=1)

        self.timescale_var = tk.StringVar()
        self.timescale_select_3 = ttk.Radiobutton(self.radiobutton_frame, text='3',
                                                  variable=self.timescale_var, value='90',
                                                  command=self.date_update_validate)
        self.timescale_select_3.grid(row=0, column=0, pady=self.pady)

        self.timescale_select_6 = ttk.Radiobutton(self.radiobutton_frame, text='6',
                                                  variable=self.timescale_var, value='180',
                                                  command=self.date_update_validate)
        self.timescale_select_6.grid(row=0, column=1, pady=self.pady)

        self.timescale_select_12 = ttk.Radiobutton(self.radiobutton_frame, text='12',
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
                                    # calls validatecommand on any action with the widget (e.g. edit, focus change)
                                    validate='all',
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
        # todo: list resources already added (from table)
        self.add_evidence_button = ttk.Button(self, text='Add Evidence', command=self.add_evidence)
        self.add_evidence_button.grid(row=2, column=0, padx=self.padx, pady=self.pady)

        self.submit_button = ttk.Button(self, text='Submit section info',
                                        command=self.attempt_section_table_update)
        self.submit_button.grid(row=3, column=0, columnspan=3, padx=self.padx, pady=self.pady)

        self.student = None
        self.section_obj = None
        self.student_username = ''
        self.section_type_short = ''

        # noinspection PyTypeChecker
        self.section_table: data_handling.SectionTable = \
            self.pager_frame.master_root.db.get_table_by_name('SectionTable')

    def update_attributes(self, student: data_handling.Student, username: str,
                          section_type_short: str):
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username
        self.section_type_short = section_type_short
        long_section_name = ui.SECTION_NAME_MAPPING[self.section_type_short]

        self.page_name = f'{self.student_username} {long_section_name} Details'

        self.header_var.set(f'{long_section_name} Details')

        state_dict = {False: 'disabled', True: 'normal'}
        if self.student.__getattribute__(f'{section_type_short}_info_id'):
            # if the section's details have already been filled out, fields are disabled with data filled in
            fields_enabled = False

            section_id = self.student.__getattribute__(f'{section_type_short}_info_id')
            section_table_dict = self.section_table.row_dict
            self.section_obj: data_handling.Section = section_table_dict[section_id]

            self.timescale_var.set(self.section_obj.activity_timescale)
            self.start_date_var.set(datetime_logic.datetime_to_str(self.section_obj.activity_start_date))
            self.activity_type_var.set(self.section_obj.activity_type)
            self.activity_details_text.insert('1.0', self.section_obj.activity_details)
            self.activity_goals_text.insert('1.0', self.section_obj.activity_goals)
            self.assessor_fullname_var.set(self.section_obj.assessor_fullname)
            self.assessor_phone_var.set(self.section_obj.assessor_phone)
            self.assessor_email_var.set(self.section_obj.assessor_email)

            self.timescale_select_3['state'] = 'disabled'
            self.timescale_select_6['state'] = 'disabled'
            self.timescale_select_12['state'] = 'disabled'
        else:
            # otherwise, the fields are enabled to allow data entry
            fields_enabled = True

            available_timescale_options = datetime_logic.get_possible_timeframes(
                student.award_level,
                self.section_type_short,
                self.student,
                self.section_table
            )

            self.timescale_select_3['state'] = state_dict[3 in available_timescale_options]
            self.timescale_select_6['state'] = state_dict[6 in available_timescale_options]
            self.timescale_select_12['state'] = state_dict[12 in available_timescale_options]

        self.start_date['state'] = state_dict[fields_enabled]
        self.activity_type['state'] = state_dict[fields_enabled]
        self.activity_details_text['state'] = state_dict[fields_enabled]
        self.activity_goals_text['state'] = state_dict[fields_enabled]
        self.assessor_fullname['state'] = state_dict[fields_enabled]
        self.assessor_phone['state'] = state_dict[fields_enabled]
        self.assessor_email['state'] = state_dict[fields_enabled]
        self.submit_button['state'] = state_dict[fields_enabled]

        # button set to inverse state of detail fields above - i.e. only enabled if section filled in
        self.add_evidence_button['state'] = state_dict[not fields_enabled]

        self.date_update_validate()  # updates/clears end date label

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
            start_date = validation.validate_date(self.start_date_var.get(), 'Start date', '/', do_logging=False)
            end_date = datetime_logic.calculate_end_date(int(self.timescale_var.get()), start_date)
            end_date = datetime_logic.datetime_to_str(end_date, '/')
        except (validation.ValidationError, ValueError):
            end_date = '----/--/--'

        self.end_date_var.set(f'➡ Expected end date: {end_date}')
        return True

    def attempt_section_table_update(self):
        try:
            new_id = self.section_table.get_new_key_id()
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
            self.section_table.add_row(new_section_entry)
            # Links student to section table
            self.student.__setattr__(f'{new_section_entry.section_type}_info_id',
                                     new_section_entry.section_id)

            msg.showinfo('Section submission successful',
                         'Section information successfully submitted. '
                         'You can now start working on this section!')
            self.back()

    def add_evidence(self):
        # if section time is complete, evidence can now be uploaded
        planned_end_date = datetime_logic.calculate_end_date(int(self.section_obj.activity_timescale),
                                                             self.section_obj.activity_start_date)
        if not datetime_logic.date_in_past(planned_end_date):
            msg.showwarning('File upload',
                            f'You cannot upload evidence until you have reached the '
                            f"section's end date ({datetime_logic.datetime_to_str(planned_end_date)}).")
        else:
            # opens a file selection dialog in the user's home directory
            # the user can select as many files as they wish
            selected_files = filedialog.askopenfiles(title='Please select file(s) to add as evidence.',
                                                     initialdir=os.path.expanduser('~'))

            if selected_files:  # if any files were selected (i.e. operation not cancelled)
                upload_dir = Path.cwd() / 'uploads' / 'student' / f'id-{self.student.student_id}'
                upload_dir.mkdir(parents=True, exist_ok=True)
                for fobj in selected_files:
                    orig_file_path = Path(fobj.name)

                    upload_path = upload_dir / orig_file_path.name
                    i = 0
                    while upload_path.exists():  # adds ' (i)' to end of filename until unique
                        i += 1  # keeps increasing i until unique
                        new_name = f'{upload_path.stem} ({i}){upload_path.suffix}'
                        upload_path = Path(upload_path.parent) / new_name

                    shutil.copy(orig_file_path, upload_path)  # 'uploads'/copies file into dir

                msg.showinfo('File upload', f'{len(selected_files)} file(s) uploaded successfully.')

                # todo: add resource table and link to section

            else:
                msg.showinfo('File upload', 'No file(s) selected to upload.')
