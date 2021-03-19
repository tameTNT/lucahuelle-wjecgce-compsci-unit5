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

        self.select_level_label = ttk.Label(self, text='Select level:', width=13, justify='right')
        self.select_level_label.grid(row=1, column=0, sticky='e', padx=0, pady=self.pady)

        self.level_selection_var = tk.StringVar()
        self.select_level = ttk.Combobox(self,
                                         state='readonly',
                                         values=('Bronze', 'Silver', 'Gold'),
                                         textvariable=self.level_selection_var,
                                         width=15)
        self.select_level.grid(row=1, column=1, sticky='w', padx=(0, self.padx), pady=self.pady)

        self.search_query_var = tk.StringVar()
        on_focus_wrapper = self.pager_frame.master_root.tk_root.register(self.initial_search_clear)
        self.search_entry = ttk.Entry(self,
                                      textvariable=self.search_query_var,
                                      width=20,
                                      validate='focus',
                                      validatecommand=on_focus_wrapper)
        self.search_entry.grid(row=1, column=2, pady=self.pady)

        self.search_button = ttk.Button(self, text='🔎', width=2, command=self.search)
        self.search_button.grid(row=1, column=3, sticky='w', pady=self.pady)

        self.staff = None
        self.staff_fullname = ''

    def update_attributes(self, staff: data_handling.Staff) -> None:
        # updates attributes with submitted parameters
        self.staff = staff
        self.staff_fullname = self.staff.fullname
        self.page_name = f'{self.staff.username} - Student Overview Dashboard'

        self.level_selection_var.set('Bronze')
        self.search_query_var.set('Search...')

        # todo: populate student table (Treeview) - separate method also called by 'search' button
        # self.test = ttk.Label(self, text='test', font=ui.BODY_FONT)
        # self.test.grid(row=1, column=0)
        # ui.add_underline_link_on_hover(
        #     self.test,
        #     lambda event, s_id=2: self.change_to_student_page(event, s_id)
        # )

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

    def initial_search_clear(self) -> True:
        if self.search_query_var.get() == 'Search...':
            self.search_query_var.set('')
        elif self.search_query_var.get() == '':
            self.search_query_var.set('Search...')
        return True

    def search(self):
        query = self.search_query_var.get()
        # todo: search primary keys and repopulate Treeview
        # todo: add 'reset' link when searching to clear box and reset results
        # wouldbenice: search/sort by different fields other than key field

    # noinspection PyUnusedLocal
    def change_to_student_page(self, event, student_id: int):
        # todo: change to student page clicked
        print(student_id, self.staff_fullname)
