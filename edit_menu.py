from datetime import datetime
import tkinter as tk

from find_and_replace import FindAndReplaceWin
from utils import clear_tags


class EditMenu(tk.Menu):
    def __init__(self, parent, text_widget):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.text_widget = text_widget
        self.add_command(label='Cut', accelerator='Ctrl+X',
                         command=lambda: self.text_widget.event_generate('<<Cut>>'))
        self.add_command(label='Copy', accelerator='Ctrl+C',
                         command=lambda: self.text_widget.event_generate('<<Copy>>'))
        self.add_command(label='Paste', accelerator='Ctrl+V',
                         command=lambda: self.text_widget.event_generate('<<Paste>>'))
        self.add_command(label='Add Timestamp', accelerator='F5', command=self.add_timestamp)
        self.add_command(label='Find and Replace', accelerator='Ctrl+F', command=self.find_and_replace)

    def add_timestamp(self, *args):
        self.text_widget.insert(tk.INSERT, datetime.now().strftime('%I:%M %p %m/%d/%Y'))
        self.text_widget.edit_modified(True)
        self.parent.title(f'*{self.parent.filename}')

    def find_and_replace(self, *args):
        if isinstance(self.parent.FIND_AND_REP_WIN, tk.Toplevel):
            self.__quit_find_and_replace()
        self.parent.FIND_AND_REP_WIN = tk.Toplevel()
        self.parent.FIND_AND_REP_WIN.resizable(False, False)
        self.parent.FIND_AND_REP_WIN.protocol('WM_DELETE_WINDOW', self.__quit_find_and_replace)
        self.parent.FIND_AND_REP_WIN.bind('<Destroy>', self.__quit_find_and_replace)
        _ = FindAndReplaceWin(self.parent.FIND_AND_REP_WIN, self.parent)

    def __quit_find_and_replace(self, *args):
        clear_tags('found', self.text_widget)
        if isinstance(self.parent.FIND_AND_REP_WIN, tk.Toplevel):
            self.parent.FIND_AND_REP_WIN.destroy()
