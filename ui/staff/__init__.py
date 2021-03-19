import logging
import tkinter.ttk as ttk

import ui
import ui.landing
from data_tables import data_handling


class StudentOverview(ui.GenericPage):
    page_name = 'Student Overview Dashboard'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        self.title_text = ttk.Label(self, text='Student Overview', font=ui.HEADING_FONT)
        self.title_text.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        self.import_export_button = ttk.Button(self, text='Import/Export data')
        self.import_export_button.grid(row=0, column=1, padx=self.padx, pady=self.pady)

        self.logout_button = ttk.Button(self, text='Logout', command=self.logout)
        self.logout_button.grid(row=0, column=2, padx=self.padx, pady=self.pady)

        self.test = ttk.Label(self, text='test', font=ui.BODY_FONT)
        self.test.grid(row=1, column=0)
        ui.add_underline_link_on_hover(
            self.test,
            lambda event, s_id=2: self.change_to_student_page(event, s_id)
        )

        self.staff = None
        self.staff_fullname = ''

    def update_attributes(self, staff: data_handling.Staff) -> None:
        # updates attributes with submitted parameters
        self.staff = staff
        self.staff_fullname = self.staff.fullname
        self.page_name = f'{self.staff_fullname} - Student Overview Dashboard'

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

    # noinspection PyUnusedLocal
    def change_to_student_page(self, event, student_id: int):
        # todo: change to student page clicked
        print(student_id, self.staff_fullname)
