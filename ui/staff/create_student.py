import logging
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.ttk as ttk

import ui
from data_tables import data_handling
from processes import password_logic, validation


class CreateStudent(ui.GenericPage):
    page_name = 'STAFF_USERNAME - Create new student'

    def __init__(self, pager_frame: ui.PagedMainFrame):
        super().__init__(pager_frame=pager_frame)

        self.back_button = ttk.Button(self, text='Back', command=self.page_back)
        self.back_button.grid(row=0, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.title_label = ttk.Label(self, text='Create new student', font=ui.HEADING_FONT)
        self.title_label.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        self.username_label = ttk.Label(self, text='Username:', justify='right')
        self.username_label.grid(row=2, column=0, pady=self.pady, sticky='e')
        self.username_entry_var = tk.StringVar()
        self.username_entry = ttk.Entry(self, textvariable=self.username_entry_var)
        self.username_entry.grid(row=2, column=1, pady=self.pady, sticky='we')

        self.password_label = ttk.Label(self, text='Password:', justify='right')
        self.password_label.grid(row=3, column=0, pady=self.pady, sticky='e')
        ui.create_tooltip(self.password_label, password_logic.PASSWORD_NOTICE)
        self.password_entry = ui.PasswordEntryFrame(self)
        self.password_entry.grid(row=3, column=1, pady=self.pady, sticky='we')

        self.confirm_password_label = ttk.Label(self, text='Confirm Password:', justify='right')
        self.confirm_password_label.grid(row=4, column=0, pady=self.pady, sticky='e')
        self.confirm_password_entry = ui.PasswordEntryFrame(self)
        self.confirm_password_entry.grid(row=4, column=1, pady=self.pady, sticky='we')

        self.centre_id_label = ttk.Label(self, text='Centre ID:', justify='right')
        self.centre_id_label.grid(row=5, column=0, pady=self.pady, sticky='e')
        self.centre_id_entry = ui.DigitEntry(0, master=self)
        self.centre_id_entry.grid(row=5, column=1, pady=self.pady, sticky='we')

        self.award_level_label = ttk.Label(self, text='Award level:', justify='right')
        self.award_level_label.grid(row=6, column=0, pady=self.pady, sticky='e')
        self.award_level_var = tk.StringVar()
        self.award_level_selection = ttk.Combobox(self, state='readonly',
                                                  values=('Bronze', 'Silver', 'Gold'),
                                                  textvariable=self.award_level_var)
        self.award_level_selection.grid(row=6, column=1, pady=self.pady, sticky='we')

        self.year_group_label = ttk.Label(self, text='Year Group:', justify='right')
        self.year_group_label.grid(row=7, column=0, pady=self.pady, sticky='e')
        self.year_group_entry = ui.DigitEntry(0, master=self)
        self.year_group_entry.grid(row=7, column=1, pady=self.pady, sticky='we')

        self.create_button = ttk.Button(self, text='Create Student', command=self.attempt_creation)
        self.create_button.grid(row=8, column=0, columnspan=2, padx=self.padx, pady=self.pady)

        self.staff_origin = None
        self.staff_fullname = None

    def update_attributes(self, staff_origin: data_handling.Staff) -> None:
        # updates attributes with submitted parameters
        self.staff_origin = staff_origin
        self.staff_fullname = self.staff_origin.fullname

        self.page_name = f'{self.staff_origin.username} - Create new student'

        self.award_level_var.set('Bronze')

    def page_back(self):
        """
        Returns the staff to the overview page
        """
        self.pager_frame.change_to_page(
            destination_page=ui.staff.StudentOverview,
            staff=self.staff_origin,
        )

    def attempt_creation(self):
        username = self.username_entry_var.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        centre_id = self.centre_id_entry.get()
        award_level = self.award_level_var.get()
        year_group = self.year_group_entry.get()

        if password != confirm_password:
            msg.showerror('Error with field data', 'Passwords do not match')
            return

        db = self.pager_frame.master_root.db
        student_table = db.get_table_by_name('StudentTable')
        new_id = student_table.get_new_key_id()

        try:
            password_logic.enforce_strength(password)

            # create objects first before adding to tables to validate inputs
            new_login = data_handling.StudentLogin(
                username=username,
                password_hash=password_logic.hash_pwd_str(password),
                student_id=new_id
            )

            new_student = data_handling.Student(
                student_id=new_id,
                centre_id=centre_id,
                award_level=award_level,
                year_group=year_group
            )

            # adding new login needs to be attempted first to test for username uniqueness
            db.get_table_by_name('StudentLoginTable').add_row(new_login)

            student_table.add_row(new_student)

        except password_logic.PasswordError as e:
            msg.showerror('Error with field data', str(e))

        except validation.ValidationError as e:
            msg.showerror('Error with field data', str(e))

        except KeyError:
            msg.showerror('Error with field data', f'The username {username!r} is already taken by another student')

        else:
            msg.showinfo('Student creation successful',
                         'New student successfully created with entered details. '
                         "They can now login on the 'Student Login' page.")
            self.page_back()
