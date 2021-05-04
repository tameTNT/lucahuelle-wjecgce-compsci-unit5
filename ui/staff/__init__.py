import logging
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.ttk as ttk
from typing import List

import ui
import ui.landing
from data_tables import data_handling
from ui.staff import student_info


class StudentOverview(ui.GenericPage):
    page_name = 'STAFF_USERNAME - Student Overview Dashboard'

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
                                      validatecommand=self.initial_search_text_clear)
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
        self.treeview_frame = ttk.Frame(self)
        self.treeview_frame.grid(row=3, column=0, columnspan=5, sticky='we', padx=self.padx, pady=(0, self.pady))

        self.student_info_treeview = ttk.Treeview(self.treeview_frame,
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

        self.student_info_treeview.pack(side='left')
        self.student_info_treeview.bind('<Double-1>', self.on_double_click)

        self.treeview_scroll = ttk.Scrollbar(self.treeview_frame, orient='vertical',
                                             command=self.student_info_treeview.yview)
        self.treeview_scroll.pack(side='right', fill='y')
        self.student_info_treeview['yscrollcommand'] = self.treeview_scroll.set
        # == end table config ==

        # todo: add functionality to add students
        self.add_student_button = ttk.Button(self, text='New Student', command=lambda: None)
        self.add_student_button.grid(row=4, column=0, columnspan=5, padx=self.padx, pady=self.pady)

        # == calendar frame contents ==
        self.event_frame = ttk.Labelframe(self, text='Coming Up')
        self.event_frame.grid(row=5, column=0, columnspan=5, padx=self.padx, pady=self.pady)

        # todo: event frame/'Coming Up' and ability to manage events with button
        self.temp_event_label = ttk.Label(self.event_frame, text='Temp coming up text...')
        self.temp_event_label.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        # == end of self.event_frame contents ==

        self.staff = None
        self.staff_fullname = ''

        db = self.pager_frame.master_root.db
        # noinspection PyTypeChecker
        self.student_login_table: data_handling.StudentLoginTable = db.get_table_by_name('StudentLoginTable')
        # noinspection PyTypeChecker
        self.student_table: data_handling.StudentTable = db.get_table_by_name('StudentTable')
        # noinspection PyTypeChecker
        self.section_table: data_handling.SectionTable = db.get_table_by_name('SectionTable')

        self.DEFAULT_SEARCH_PLACEHOLDER = 'Search names...'

    def update_attributes(self, staff: data_handling.Staff) -> None:
        # updates attributes with submitted parameters
        self.staff = staff
        self.staff_fullname = self.staff.fullname
        self.page_name = f'{self.staff.username} - Student Overview Dashboard'

        self.level_selection_var.set('Bronze')
        self.search_query_var.set(self.DEFAULT_SEARCH_PLACEHOLDER)

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
    #         destination_page=ui.student.enrolment.Enrolment,
    #         student=self.student,
    #         username=self.student_username,
    #     )

    def initial_search_text_clear(self) -> True:  # 'validation' function must return True
        if self.search_query_var.get() == self.DEFAULT_SEARCH_PLACEHOLDER:
            self.search_query_var.set('')
        elif self.search_query_var.get() == '':
            self.search_query_var.set(self.DEFAULT_SEARCH_PLACEHOLDER)
        return True

    def search(self):
        self.initial_search_text_clear()  # prevent searching with 'Search names...'
        query = self.search_query_var.get().lower()
        self.initial_search_text_clear()

        if query:
            # wouldbenice: use detach and reattach instead (see link)
            # https://stackoverflow.com/questions/44565358/how-to-filter-a-ttk-treeview-in-python/47055786#47055786
            self.repopulate_treeview_table()  # reset table so all values are searched

            tv = self.student_info_treeview
            # gets user/full names of all items visible in current treeview
            current_item_dict = [tv.item(tv_item_id)['text'] for tv_item_id in tv.get_children()]

            # builds dictionary of item_text (username removed) to treeview item id
            searchable_dict = dict()
            for item_text in current_item_dict:
                org_label = item_text
                # Removes '(Username) ' prefix if it exists
                if '(Username)' in item_text:
                    item_text = item_text.split(') ', maxsplit=1)[-1]

                searchable_dict[item_text.lower()] = org_label

            # set of all name (item_text) strings where *query* is present
            matches = {item_text for item_text in searchable_dict.keys() if query in item_text}
            # list of all treeview item ids corresponding to matches found above
            results = [org_label for (item_text, org_label) in searchable_dict.items() if item_text in matches]

            if not results:  # if result list is empty
                msg.showwarning('Search', f'No results found for search query for current award level: "{query}"')
                self.search_query_var.set(self.DEFAULT_SEARCH_PLACEHOLDER)

        else:
            msg.showinfo('Search', 'No search query entered.')
            results = []

        self.repopulate_treeview_table(item_list=results)

        # wouldbenice: add 'reset' link when searching to clear box and reset results
        # wouldbenice: search by different fields other than key field

    def repopulate_treeview_table(self, tk_event: tk.Event = None, item_list: List[str] = None) -> None:
        """
        Populates the treeview (student overview) table with student usernames and details etc.

        :param tk_event: An event object generated by tkinter - automatically passed to function if called by tkinter
        :param item_list: A list of strings (username/fullname field val) specifying items to show in the treeview
        :return:
        """
        tv = self.student_info_treeview
        # clears search box on award level change triggered by Combobox
        if tk_event:
            # noinspection PyUnresolvedReferences
            if isinstance(tk_event.widget, ttk.Combobox):
                self.search_query_var.set(self.DEFAULT_SEARCH_PLACEHOLDER)

        selected_level = self.level_selection_var.get()

        tv.delete(*tv.get_children())  # clear tree before repopulating
        for student in self.student_table.row_dict.values():
            if student.award_level == selected_level.lower():
                username = student.get_login_username(self.student_login_table)
                username_display_str = f'(Username) {username}'
                row_name = student.fullname if student.fullname else username_display_str

                approval_status = student.get_progress_summary(self.section_table)

                vol_status = student.get_section_obj('vol', self.section_table)
                vol_status = vol_status.activity_status if vol_status else 'Not started'
                skill_status = student.get_section_obj('skill', self.section_table)
                skill_status = skill_status.activity_status if skill_status else 'Not started'
                phys_status = student.get_section_obj('phys', self.section_table)
                phys_status = phys_status.activity_status if phys_status else 'Not started'

                # todo: expedition status text and column

                should_insert_item = False
                if item_list:
                    if row_name in item_list:
                        should_insert_item = True
                else:
                    should_insert_item = True

                if should_insert_item:
                    tv.insert(
                        parent='', index='end', text=row_name,
                        values=(approval_status, vol_status, skill_status, phys_status, 'Null - TODO',
                                # dictionary with extra info not shown - used within code.
                                # tkinter saves this dict using repr() so use eval() to get the dict back
                                {'id': student.student_id, 'username': username, 'fullname': student.fullname})
                    )

    # noinspection PyUnusedLocal
    def on_double_click(self, tk_event: tk.Event):
        """
        To be bound to a the treeview object. (requires tk_event for call from within tkinter)
        When this is double clicked, the currently selected item is retrieved and its values extracted.
        The method then calls self.change_to_student_page() to show the selected student's info to the user.
        """
        selected_item = self.student_info_treeview.selection()

        treeview_item_values = self.student_info_treeview.item(selected_item)
        # 'text' value of row is username/fullname; last is the dictionary of extra info including student_id
        clicked_name, clicked_student_id = treeview_item_values['text'], eval(treeview_item_values['values'][-1])['id']

        logging.debug(f'Student - {clicked_name} id:{clicked_student_id} - double clicked by {self.staff_fullname}')

        self.change_to_student_page(clicked_name, clicked_student_id)

    def change_to_student_page(self, clicked_name: str, student_id: int):
        student_obj = self.student_table.row_dict[student_id]

        self.pager_frame.change_to_page(
            destination_page=student_info.StudentInfo,
            clicked_name=clicked_name,
            student=student_obj,
            staff_origin=self.staff
        )
