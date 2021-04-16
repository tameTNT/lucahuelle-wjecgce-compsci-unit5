import logging
import os
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as msg
import tkinter.ttk as ttk

import ui
from data_tables import data_handling, SECTION_NAME_MAPPING
from processes import datetime_logic, validation, shorten_string


class SectionInfo(ui.GenericPage):
    page_name = 'Student Section Details'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        self.back_button = ttk.Button(self, text='Back', command=self.page_back)
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
                                                  command=self.update_date_validation)
        self.timescale_select_3.grid(row=0, column=0, pady=self.pady)

        self.timescale_select_6 = ttk.Radiobutton(self.radiobutton_frame, text='6',
                                                  variable=self.timescale_var, value='180',
                                                  command=self.update_date_validation)
        self.timescale_select_6.grid(row=0, column=1, pady=self.pady)

        self.timescale_select_12 = ttk.Radiobutton(self.radiobutton_frame, text='12',
                                                   variable=self.timescale_var, value='360',
                                                   command=self.update_date_validation)
        self.timescale_select_12.grid(row=0, column=2, pady=self.pady)
        # == end of radio button frame ==
        self.start_date_label = ttk.Label(self.detail_frame,
                                          text='Start date:', justify='right')
        self.start_date_label.grid(row=1, column=0, pady=self.pady, sticky='e')

        self.start_date_var = tk.StringVar()
        # on_update_wrapper = ...tk_root.register(self.update_date_validation) - wrapper not needed
        self.start_date = ttk.Entry(self.detail_frame, width=10,
                                    textvariable=self.start_date_var,
                                    # calls validatecommand on any action with the widget (e.g. edit, focus change)
                                    validate='all',
                                    # updates self.end_date_var based on entry
                                    validatecommand=self.update_date_validation)
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

        self.activity_details_scrollable_frame = ttk.Frame(self.activity_info_frame)
        self.activity_details_scrollable_frame.grid(row=1, column=1, pady=self.pady, sticky='we')
        self.activity_details_text = tk.Text(self.activity_details_scrollable_frame, width=25, height=4,
                                             wrap='word', font=ui.TEXT_ENTRY_FONT)
        self.activity_details_text.pack(side='left')
        self.details_y_scroll = ttk.Scrollbar(self.activity_details_scrollable_frame, orient='vertical',
                                              command=self.activity_details_text.yview)
        self.activity_details_text['yscrollcommand'] = self.details_y_scroll.set
        self.details_y_scroll.pack(side='right', fill='y')

        self.activity_goals_label = ttk.Label(self.activity_info_frame, text='Goals:', justify='right')
        self.activity_goals_label.grid(row=2, column=0, pady=self.pady, sticky='e')

        self.activity_goals_scrollable_frame = ttk.Frame(self.activity_info_frame)
        self.activity_goals_scrollable_frame.grid(row=2, column=1, pady=self.pady, sticky='we')
        self.activity_goals_text = tk.Text(self.activity_goals_scrollable_frame, width=25, height=3,
                                           wrap='word', font=ui.TEXT_ENTRY_FONT)
        self.activity_goals_text.pack(side='left')
        self.goals_y_scroll = ttk.Scrollbar(self.activity_goals_scrollable_frame, orient='vertical',
                                            command=self.activity_goals_text.yview)
        self.activity_goals_text['yscrollcommand'] = self.goals_y_scroll.set
        self.goals_y_scroll.pack(side='right', fill='y')
        # == end of self.activity_info_frame ==

        # == assessor info frame ==
        self.assessor_info_frame = ttk.Labelframe(self.detail_frame, text='Your Assessor')
        self.assessor_info_frame.grid(row=2, column=2, ipadx=self.padx, padx=self.padx, pady=self.pady)

        self.assessor_fullname_label = ttk.Label(self.assessor_info_frame, text='Fullname:', justify='right')
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

        # === evidence frame ===
        self.evidence_frame = ttk.Labelframe(self, text='Evidence Upload')
        self.evidence_frame.grid(row=2, column=0, padx=self.padx, pady=self.pady)

        self.evidence_list = ttk.Frame(self.evidence_frame)  # populated in self.update_attributes()
        self.evidence_list.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        # wouldbenice: buttons to open folder containing resource for staff - os.startfile(path, 'open'), Windows only
        self.add_evidence_button = ttk.Button(self.evidence_frame, text='Add Evidence', command=self.add_evidence)
        self.add_evidence_button.grid(row=1, column=0, padx=self.padx, pady=self.pady)
        # === end of self.evidence_frame ===

        self.submit_button = ttk.Button(self, text='Submit section info',
                                        command=self.attempt_section_table_submit)
        self.submit_button.grid(row=3, column=0, columnspan=3, padx=self.padx, pady=self.pady)

        # noinspection PyTypeChecker
        self.student: data_handling.Student = None
        # noinspection PyTypeChecker
        self.section_obj: data_handling.Section = None
        self.student_username = ''
        self.section_type_short = ''

        db = self.pager_frame.master_root.db
        # noinspection PyTypeChecker
        self.section_table: data_handling.SectionTable = db.get_table_by_name('SectionTable')
        # noinspection PyTypeChecker
        self.resource_table: data_handling.ResourceTable = db.get_table_by_name('ResourceTable')

    def update_attributes(self, student: data_handling.Student, username: str,
                          section_type_short: str):
        # updates attributes with submitted parameters
        self.student = student
        self.student_username = username
        self.section_type_short = section_type_short
        long_section_name = SECTION_NAME_MAPPING[self.section_type_short]

        self.page_name = f'{self.student_username} {long_section_name} Details'

        self.header_var.set(f'{long_section_name} Details')

        state_dict = {False: 'disabled', True: 'normal'}

        # if the section's details have already been filled in,
        # fields are disabled with data pre-filled
        if self.student.__getattribute__(f'{section_type_short}_info_id'):
            fields_enabled = False

            section_id = self.student.__getattribute__(f'{section_type_short}_info_id')
            section_table_dict = self.section_table.row_dict
            self.section_obj: data_handling.Section = section_table_dict[section_id]

            # fill in all form fields with entered data
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

            self.update_evidence_list()  # updates/populates the evidence list

        else:  # otherwise, the fields are enabled to allow data entry
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

        # enable/disable fields/forms depending on section status
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

        self.update_date_validation()  # updates/clears end date label

    def update_evidence_list(self):
        """
        Freshly populates the GUI's evidence list from the resource table.
        """
        self.evidence_list.destroy()  # clears current evidence list
        self.evidence_list = ttk.Frame(self.evidence_frame)  # populated below
        self.evidence_list.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        for resource in self.resource_table.row_dict.values():
            is_section_evidence = resource.resource_type == 'section_evidence'
            is_id_match = resource.parent_link_id == self.section_obj.section_id
            if is_section_evidence and is_id_match:
                row_id = resource.resource_id

                evidence_row = ttk.Frame(self.evidence_list)
                evidence_row.grid(sticky='we')

                short_name = shorten_string(resource.file_path.stem, 15) + ' ' + resource.file_path.suffix
                name_label = ttk.Label(evidence_row, text=short_name, width=20, justify='right')
                name_label.grid(row=0, column=0)
                ui.create_tooltip(name_label, resource.file_path.name)  # adds full path to tooltip

                date_added = datetime_logic.datetime_to_str(resource.date_uploaded)
                date_label = ttk.Label(evidence_row,  # 📝 marks section report
                                       text=f'Uploaded {date_added}{" 📝" if resource.is_section_report else ""}',
                                       width=22)
                date_label.grid(row=0, column=1, sticky='we')

                delete_button = ttk.Button(evidence_row, text='❌', width=3,
                                           command=lambda x=row_id: self.delete_evidence(x))
                delete_button.grid(row=0, column=2)
                ui.create_tooltip(delete_button, 'Delete evidence')

                report_button = ttk.Button(evidence_row, text='📝', width=3,
                                           command=lambda x=row_id: self.mark_evidence_as_report(x))
                report_button.grid(row=0, column=3)
                ui.create_tooltip(report_button, 'Mark as section report')

    def update_date_validation(self) -> True:
        """
        A 'validation' function so that the following code is executed
        on every event of the entry widget.
        Therefore always returns True for this validation aspect to work.
        """
        try:
            start_date = validation.validate_date(self.start_date_var.get(), 'Start date', '/', do_logging=False)
            end_date = datetime_logic.calculate_end_date(int(self.timescale_var.get()), start_date)
            end_date = datetime_logic.datetime_to_str(end_date, '/')
        except (validation.ValidationError, ValueError):
            end_date = '----/--/--'

        self.end_date_var.set(f'➡ Expected end date: {end_date}')

        return True

    def page_back(self):
        """
        Returns the student to the dashboard page
        """
        self.pager_frame.change_to_page(
            destination_page=ui.student.StudentAwardDashboard,
            student=self.student,
            username=self.student_username,
        )

    def attempt_section_table_submit(self):
        """
        Attempts to submit the user input data as a new section object.
        Raises a ValidationError if this fails for any reason to do with user
        input. Otherwise, if successful, returns the student to the overview page.
        """
        try:  # attempts to create new Section object
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
        else:  # no validation errors during object creation means all clear to add to table
            self.section_table.add_row(new_section_entry)
            # Links student to section table by ..._info_id attribute in student object
            self.student.__setattr__(f'{new_section_entry.section_type}_info_id',
                                     new_section_entry.section_id)

            msg.showinfo('Section submission successful',
                         'Section information successfully submitted. '
                         'You can now start working on this section!')
            self.page_back()

    def add_evidence(self):
        """
        Allows the user to select one or more files to upload as evidence for a section.
        These files are then added to the resource table and displayed in a list
        within the section's associated page. If the upload is successful, the student
        is returned to the overview page.
        """
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

            num_files_uploaded = self.resource_table.add_student_resources(selected_files,
                                                                           self.student.student_id,
                                                                           self.section_obj.section_id)

            if num_files_uploaded > 0:
                msg.showinfo('File upload', f'{num_files_uploaded} file(s) uploaded successfully.')
                self.page_back()
            else:
                msg.showinfo('File upload', 'No file(s) selected to upload.')

    def delete_evidence(self, resource_id: int):
        """
        Attempts to delete the section_evidence resource with id resource_id
        from the ResourceTable. Also deletes the actual associated file.

        :param resource_id: id of the resource to delete
        :return:
        """
        resource_obj = self.resource_table.row_dict[resource_id]
        confirm_delete = msg.askyesno('Delete evidence',
                                      f"Are you sure you want to delete '{resource_obj.file_path.name}'?\n"
                                      'This action cannot be undone.')
        if confirm_delete:
            self.resource_table.delete_row(resource_id)
            # refresh resource list
            self.update_evidence_list()

    def mark_evidence_as_report(self, resource_id: int):
        """
        Attempts to mark the section_evidence resource with id resource_id
        in the ResourceTable as a section report
        (i.e. set is_section_report attribute to 1 (from 0)).
        Only one resource per section object can be marked in this way.

        :param resource_id: id of the resource to mark as section report
        :return:
        """
        resource_obj = self.resource_table.row_dict[resource_id]
        confirm_mark = msg.askyesno('Mark as section report',
                                    f"Are you sure you want to mark '{resource_obj.file_path.name}' "
                                    'as your ONE assessor report for this section?\n'
                                    f'This action cannot be undone.')
        if confirm_mark:
            if self.resource_table.has_section_report(self.section_obj.section_id):
                msg.showwarning('Mark as section report',
                                'This section already has a resource marked as a section report. '
                                'You may only have one section report per section.\n'
                                'Please delete that resource before trying to mark another'
                                'as your section report.')
            else:
                resource_obj.is_section_report = 1
                logging.debug(f'Resource with id {resource_obj.resource_id} was '
                              f'marked as the section report for section id {self.section_obj.section_id}')
                # refresh resource list
                self.update_evidence_list()
