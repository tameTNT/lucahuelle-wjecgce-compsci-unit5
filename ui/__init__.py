from __future__ import annotations  # needed for typing of classes not yet defined

import logging
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from typing import Iterable, Type, Callable

from data_tables import data_handling

# Font constants
BODY_FONT = 'TkTextFont'
HEADING_FONT = 'TkHeadingFont 15'
ITALIC_CAPTION_FONT = 'TEMP - set in main.py'
BOLD_CAPTION_FONT = 'TEMP - set in main.py'
TOOLTIP_FONT = 'TkTooltipFont 9'
TEXT_ENTRY_FONT = 'TkTextFont 9'


# Tooltip class and create_tooltip function adapted from
# https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
class ToolTip:
    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.text = ''
        self.x = self.y = 0

    def show_tooltip(self, text: str):
        """
        Display text in a tooltip window
        """
        self.text = text
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_pointerx() + 5
        y = self.widget.winfo_pointery() + 5
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(1)
        self.tip_window.wm_geometry(f'+{x}+{y}')
        label = ttk.Label(self.tip_window, text=self.text, justify='left',
                          background='#ffffff', relief='solid', borderwidth=2,
                          font=TOOLTIP_FONT)
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


def create_tooltip(widget: tk.Widget, text: str):
    """
    Create a tooltip with text that is shown when the user hovers over widget.
    """
    tool_tip = ToolTip(widget)

    # noinspection PyUnusedLocal
    def enter(tk_event: tk.Event):
        tool_tip.show_tooltip(text)

    # noinspection PyUnusedLocal
    def leave(tk_event: tk.Event):
        tool_tip.hide_tooltip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


# todo: function not needed anymore?
def add_underline_link_on_hover(l_widget: ttk.Label, change_page_func: Callable):
    """
    Underlines the label widget when the user hovers over it
    indicating a clickable link to them.

    :param l_widget: the ttk label widget which the user hovers over.
        Should have a font attribute already set (otherwise font may change on hover)
    :param change_page_func: the change page function to be called when
        the user clicks (mouse button 1) the label.
        First argument must be able to accept tkinter event details: e.g. func(event, a, b): ...
    """
    l_widget.bind('<Button-1>', change_page_func)

    # noinspection PyUnusedLocal
    def enter(tk_event: tk.Event):
        f = font.Font(l_widget, l_widget.cget('font'))
        f.configure(underline=True)
        l_widget.configure(font=f)

    # noinspection PyUnusedLocal
    def leave(tk_event: tk.Event):
        f = font.Font(l_widget, l_widget.cget('font'))
        f.configure(underline=False)
        l_widget.configure(font=f)

    l_widget.bind('<Enter>', enter)
    l_widget.bind('<Leave>', leave)


# Class design adapted from
# https://www.reddit.com/r/learnpython/comments/985umy/limit_user_input_to_only_int_with_tkinter/e4dj9k9
class DigitEntry(ttk.Entry):
    """
    An adapted Entry widget that only allows numerical digits to be entered (i.e. 0,1,...,9).
    Retrieve and store values (as *strings*) using .get() and .set() methods.
    """

    def __init__(self, initial_value: int, master: tk.Widget = None, **kwargs):
        start_string = f'{initial_value if initial_value else ""}'
        self.var = tk.StringVar(value=start_string)
        ttk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = start_string
        self.var.trace('w', self.check)  # calls self.check() when self.var is written to
        self.get, self.set = self.var.get, self.var.set

    # noinspection PyUnusedLocal
    def check(self, *args):
        current_value = self.get()
        if current_value.isdigit() or current_value == '':
            # the current value is only digits (or an empty string); allow this
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this
            self.set(self.old_value)


class PasswordEntryFrame(ttk.Frame):
    def __init__(self, master: tk.Widget = None, **kwargs):
        """
        A ttk.Frame object containing a password entry field (which shows dots while typing)
        and a button to toggle password visibility.
        The entered data can be get/set as usual using .get()/.set().
        The password's visibility can also be toggled, shown and hidden using the methods below.
        """
        super().__init__(master, **kwargs)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self,  # \u2022 is a unicode bullet pt/dot
                                        textvariable=self.password_var, show='\u2022')
        self.password_entry.grid(row=0, column=1, sticky='we')

        self.get, self.set = self.password_var.get, self.password_var.set

        self.show_pwd_button = ttk.Button(self, text='👁',
                                          width=2, command=self.toggle_password_visibility)
        self.show_pwd_button.grid(row=0, column=2, sticky='w')
        create_tooltip(self.show_pwd_button, 'Show/Hide password')

    def toggle_password_visibility(self):
        """
        Show/hide password with unicode dot characters by changing Entry widget's show option
        """
        if self.password_entry['show'] == '\u2022':  # password currently hidden
            self.show_password()
        else:  # password currently revealed
            self.hide_password()

    def show_password(self):
        self.password_entry.config(show='')

    def hide_password(self):
        self.password_entry.config(show='\u2022')


# 'Page-based approach' adapted from the framework provided at
# https://pythonprogramming.net/change-show-new-frame-tkinter/ and
# https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
class RootWindow:
    def __init__(self, tk_root: tk.Tk, db: data_handling.Database,
                 padx: int = 10, pady: int = 5):
        """
        A wrapper for a tkinter 'root' which also contains the frame
        holding the actual application.

        :param tk_root: tk.Tk() object to act as tkinter root
        :param db: main database object to manipulate throughout application
        :param padx: padx value to use in all .grid() calls
        :param pady: pady value to use in all .grid() calls
        """
        self.tk_root = tk_root

        # wouldbenice: store all tables within generic pages by default instead of
        #  layered accessing this variable so many layers up
        self.db = db
        self.padx = padx
        self.pady = pady

        self.main_frame = ttk.Frame(self.tk_root)
        self.main_frame.pack()

        self.window_frame = ttk.Frame(self.main_frame)
        self.window_frame.grid(row=0, column=0)

        logging.debug(f'{type(self).__name__} initialised')

    def initialise_window(self,
                          page_obj_list: Iterable[Type[GenericPage]],
                          start_page: Type[GenericPage]):
        """
        Actually 'starts' the application by setting the originally empty
        self.window_frame to another with content 'layered' inside.

        :param page_obj_list: a list of GenericPage objects that the tkinter
            window can be 'built up'/layered from (see PagedMainFrame docs)
        :param start_page: a designated class (contained in page_obj_list)
            to use as the start/landing page for the application.
            This is the first page that the user will see on startup.
        """
        self.window_frame = PagedMainFrame(self, page_obj_list, start_page)


class GenericPage(ttk.Frame):
    # The name to be used in a .title() call when this window is displayed to the user
    page_name = 'DofE - FRAME_NAME'  # updated in update_attributes() method of subclasses

    def __init__(self, pager_frame: PagedMainFrame):
        """
        The base class for all pages within the application.

        :param pager_frame: a PagedMainFrame object responsible for controlling
            which page is displayed to the user at any time. Must therefore have
            a change_to_page method
        """
        super().__init__(pager_frame)  # initialises object as ttk.Frame with pager_frame as master
        self.pager_frame = pager_frame

        self.padx = pager_frame.padx
        self.pady = pager_frame.pady

    def update_attributes(self, **kwargs) -> None:
        """
        A base method for all pages.
        Overwritten by children if the window is dynamic
        (e.g. fields that rely on particular student data).
        This method is then called every time that window needs to be displayed
        in order to update any such variables/fields.
        Additional requested data should be passed as kwargs (e.g. student=..., name=...).
        Which parameters are required depends on the specific class.
        """
        pass


# wouldbenice: create a HomePage class that includes a logout method


class PagedMainFrame(ttk.Frame):
    def __init__(self,
                 master_root: RootWindow,
                 page_obj_list: Iterable[Type[GenericPage]],
                 start_page: Type[GenericPage]):
        """
        Initialises a MainPageFrame object: the main tkinter window which contains
        the 'pages'/frames for all operations in the application.
        The user can navigate the different pages using buttons on each page.
        These buttons call the change_to_page method which cycles through the
        layered frames by elevating them to the top of the tkinter window.
        Should only be called using RootWindow.initialise_window()

        :param master_root: a tkinter 'root' wrapper which is used to changed
            windows' titles, dimensions, etc.
        """
        super().__init__(master_root.window_frame)

        self.master_root = master_root

        self.padx = self.master_root.padx
        self.pady = self.master_root.pady

        # ensures that layered frames are packed/gridded seamlessly
        # into this main controller/'pager' frame
        # wouldbenice: why aren't pages centered in the whole frame?
        self.pack(side='top', fill='both', expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # a dictionary of all the 'pages' (GenericPage)/frames to be contained in the tkinter window
        self.page_frames = dict()

        # goes through each page object in turn and creates their frame within the window
        for Page in page_obj_list:
            page_frame = Page(pager_frame=self)
            self.page_frames[Page] = page_frame
            # all use same grid row and column so that frames are stacked
            page_frame.grid(row=0, column=0, sticky='nsew')

        # keeps track of the currently elevated/main page the user can see
        self.current_page = ttk.Frame()
        # sets the initial page to start_page specified in initialisation call
        self.change_to_page(start_page)

    def change_to_page(self, destination_page: Type[GenericPage],
                       clear_fields=True, **kwargs) -> None:
        """
        Changes the page displayed in the tkinter window to destination_page.
        This page must be present in the page_obj_list given when this object was initialised.
        If clear_fields, then text variable (e.g. tk.StringVar) field values are
        also cleared as the frame is left by the user.
        kwargs are required if destination_page is in any way dynamic
        and hence has an update_attributes method that requires additional parameters.
        """
        if clear_fields:
            # collects all StringVar in current page
            str_var_list = [var for var in self.current_page.__dict__.values()
                            if isinstance(var, tk.StringVar)]

            for str_var in str_var_list:
                str_var.set('')  # clears each field collected above in turn

            # collects all password fields in current page
            pass_var_list = [var for var in self.current_page.__dict__.values()
                             if isinstance(var, PasswordEntryFrame)]

            for pass_var in pass_var_list:
                pass_var.set('')  # clears each password field collected above in turn

            # collects all tk.Text fields in current page
            text_field_list = [var for var in self.current_page.__dict__.values()
                               if isinstance(var, tk.Text)]

            for text_field in text_field_list:
                # if the text_field state is 'disabled' it can't be cleared
                text_field['state'] = 'normal'
                text_field.delete('1.0', 'end')

        next_frame = self.page_frames[destination_page]  # gets the specified next page/frame
        next_frame.update_attributes(**kwargs)  # updates the page's variables if necessary

        # changes window title based on name specified in the new page
        self.master_root.tk_root.title(f'DofE - {next_frame.page_name}')

        next_frame.tkraise()  # elevates the frame to the top of frame stack/'changes pages'

        self.current_page = next_frame

        logging.debug(f'User changed displayed page to {type(self.current_page).__name__}')
