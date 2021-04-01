import logging
import tkinter as tk
import tkinter.ttk as ttk

import ui
import ui.landing
from data_tables import data_handling


class StudentOverview(ui.GenericPage):
    page_name = 'Student Overview Dashboard'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        self.heading_label = ttk.Label(self, text='Student Overview', font=ui.HEADING_FONT)
        self.heading_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        self.import_export_button = ttk.Button(self, text='Import/Export data')
        self.import_export_button.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.logout_button = ttk.Button(self, text='Logout', command=self.logout)
        self.logout_button.grid(row=0, column=2, columnspan=2, padx=self.padx, pady=self.pady)

        self.select_level_label = ttk.Label(self, text='Select level:')
        self.select_level_label.grid(row=1, column=0, sticky='e', padx=(self.padx, 0), pady=self.pady)

        self.level_selection_var = tk.StringVar()
        self.select_level = ttk.Combobox(self,
                                         state='readonly',
                                         values=('Bronze', 'Silver', 'Gold'),
                                         textvariable=self.level_selection_var,
                                         width=15)
        self.select_level.grid(row=1, column=1, sticky='w', padx=(0, self.padx), pady=self.pady)
        self.select_level.bind("<<ComboboxSelected>>", self.repopulate_treeview_table)
        self.columnconfigure(1, weight=1)

        self.search_query_var = tk.StringVar()
        self.search_entry = ttk.Entry(self,
                                      textvariable=self.search_query_var,
                                      width=30,
                                      validate='focus',
                                      validatecommand=self.initial_search_clear)
        self.search_entry.grid(row=1, column=2, sticky='e', pady=self.pady)

        self.search_button = ttk.Button(self, text='🔎', width=2, command=self.search)
        self.search_button.grid(row=1, column=3, sticky='w', pady=self.pady)

        self.table_note = ttk.Label(self,
                                    text='Double click a student to view their associated '
                                         'data and approve submissions',
                                    justify='center', font=ui.ITALIC_CAPTION_FONT, width=65)
        self.table_note.grid(row=2, column=0, columnspan=5, padx=self.padx, pady=(self.pady, 0))
        self.rowconfigure(2, weight=1)
        # == configuring student table ==
        self.student_info_treeview = ttk.Treeview(self,
                                                  columns=(
                                                      'approval_status', 'volunteering',
                                                      'skill', 'physical', 'expedition'
                                                  ))

        self.student_info_treeview.heading('#0', text='Fullname/Username', anchor='w')
        self.student_info_treeview.column('#0', anchor='w')
        self.student_info_treeview.heading('approval_status', text='Approval status')
        self.student_info_treeview.column('approval_status', anchor='center')
        self.student_info_treeview.heading('volunteering', text='Volunteering')
        self.student_info_treeview.column('volunteering', anchor='center')
        self.student_info_treeview.heading('skill', text='Skill')
        self.student_info_treeview.column('skill', anchor='center')
        self.student_info_treeview.heading('physical', text='Physical')
        self.student_info_treeview.column('physical', anchor='center')
        self.student_info_treeview.heading('expedition', text='Expedition')
        self.student_info_treeview.column('expedition', anchor='center')

        # wouldbenice: ability to sort columns when the headings are clicked

        self.student_info_treeview.grid(row=3, column=0, columnspan=5, sticky='we', padx=self.padx,
                                        pady=(0, self.pady))
        self.student_info_treeview.bind('<Double-1>', self.on_double_click)
        # == end table config ==

        self.staff = None
        self.staff_fullname = ''

        db = self.pager_frame.master_root.db
        # noinspection PyTypeChecker
        self.student_login_table: data_handling.StudentLoginTable = db.get_table_by_name('StudentLoginTable')
        # noinspection PyTypeChecker
        self.student_table: data_handling.StudentTable = db.get_table_by_name('StudentTable')
        # noinspection PyTypeChecker
        self.section_table: data_handling.SectionTable = db.get_table_by_name('SectionTable')

    def update_attributes(self, staff: data_handling.Staff) -> None:
        # updates attributes with submitted parameters
        self.staff = staff
        self.staff_fullname = self.staff.fullname
        self.page_name = f'{self.staff.username} - Student Overview Dashboard'

        self.level_selection_var.set('Bronze')
        self.search_query_var.set('Search...')

        self.repopulate_treeview_table()

    def logout(self):
        """
        Logs the staff member out of the page - returns them to Welcome page
        """
        logging.info(f'Username "{self.staff.username}" '
                     f'successfully logged out of staff application')

        self.pager_frame.change_to_page(ui.landing.Welcome)

    # def import_export(self):  # todo: import/export data GUI - add command to button above
    #     self.pager_frame.change_to_page(
    #         destination_page=ui.student.enrollment.Enrollment,
    #         student=self.student,
    #         username=self.student_username,
    #     )

    def initial_search_clear(self) -> True:  # 'validation' function must return True
        if self.search_query_var.get() == 'Search...':
            self.search_query_var.set('')
        elif self.search_query_var.get() == '':
            self.search_query_var.set('Search...')
        return True

    def search(self):
        query = self.search_query_var.get()
        # todo: search primary keys and repopulate Treeview
        # todo: add 'reset' link when searching to clear box and reset results
        # wouldbenice: search by different fields other than key field

    def repopulate_treeview_table(self, tk_event=None, tv: ttk.Treeview = None):
        # todo: function docs
        if not tv:  # if no argument is given for tv (called by tkinter GUI)
            tv = self.student_info_treeview

        selected_level = self.level_selection_var.get()

        tv.delete(*tv.get_children())  # clear tree before repopulating
        for student in self.student_table.row_dict.values():
            if student.award_level == selected_level.lower():
                username_str = f'(Username) {student.get_login_username(self.student_login_table)}'
                row_name = student.fullname if student.fullname else username_str

                approval_status = student.get_progress_summary(self.section_table)

                vol_status = student.get_section_obj('vol', self.section_table)
                vol_status = vol_status.activity_status if vol_status else 'Not started'
                skill_status = student.get_section_obj('skill', self.section_table)
                skill_status = skill_status.activity_status if skill_status else 'Not started'
                phys_status = student.get_section_obj('phys', self.section_table)
                phys_status = phys_status.activity_status if phys_status else 'Not started'

                # todo: expedition status text and column

                tv.insert(
                    parent='', index='end', text=row_name,
                    values=(approval_status, vol_status, skill_status, phys_status, 'Null - TODO', student.student_id)
                )

    # noinspection PyUnusedLocal
    def on_double_click(self, tk_event):
        selected_item = self.student_info_treeview.selection()

        treeview_item_values = self.student_info_treeview.item(selected_item)
        # first item in 'values' list is username/fullname; last is the student's id
        clicked_name, clicked_student_id = treeview_item_values['text'], treeview_item_values['values'][-1]
        self.change_to_student_page(clicked_name, clicked_student_id)

    def change_to_student_page(self, student_name: str, student_id: int):
        # todo: change to student page clicked
        logging.debug(f'Student - {student_name} id:{student_id} - selected by {self.staff_fullname}')
