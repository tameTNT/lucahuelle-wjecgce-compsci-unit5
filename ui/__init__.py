from __future__ import annotations  # needed for typing of classes not yet defined

import logging
import tkinter as tk
import tkinter.ttk as ttk
from typing import Iterable, Type

from data_tables import data_handling


# By CC attribution, this Tooltip class and create_tooltip func are adapted from
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
                          font='TkTooltipFont 9')
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
    def enter(event):
        tool_tip.show_tooltip(text)

    # noinspection PyUnusedLocal
    def leave(event):
        tool_tip.hide_tooltip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


# By CC attribution, this 'page-based approach' is based on the framework provided at
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

        :param page_obj_list: A list of GenericPage objects that the tkinter
            window can be 'built up'/layered from (see PagedMainFrame docs)
        :param start_page: A designated class (contained in page_obj_list)
            to use as the start/landing page for the application.
            This is the first page that the user will see on startup.
        """
        self.window_frame = PagedMainFrame(self, page_obj_list, start_page)


class GenericPage(ttk.Frame):
    # The name to be used in a .title() call when this window is displayed to the user
    page_name = ''

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

        :param master_root: A tkinter 'root' wrapper which is used to changed
            windows' titles, dimensions, etc.
        """
        super().__init__(master_root.window_frame)

        self.master_root = master_root

        self.padx = self.master_root.padx
        self.pady = self.master_root.pady

        # ensures that layered frames are packed/gridded seamlessly
        # into this main controller/'pager' frame
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
        If clear_fields, then text variable (tk.StringVar) field values are
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

        next_frame = self.page_frames[destination_page]  # gets the specified next page/frame
        next_frame.update_attributes(**kwargs)  # updates the page's variables if necessary

        # changes window title based on name specified in the new page
        self.master_root.tk_root.title(f'DofE - {next_frame.page_name}')

        next_frame.tkraise()  # elevates the frame to the top of frame stack/'changes pages'

        self.current_page = next_frame

        logging.debug(f'User changed displayed page to {type(self.current_page).__name__}')
