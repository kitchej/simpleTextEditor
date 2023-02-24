from datetime import datetime
import tkinter as tk

from dialogs.find_and_replace import FindAndReplaceWin
from utils import clear_tags


class EditMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.editor_obj = self.parent.editor
        self.add_command(label='Cut', accelerator='Ctrl+X',
                         command=lambda: self.editor_obj.event_generate('<<Cut>>'))
        self.add_command(label='Copy', accelerator='Ctrl+C',
                         command=lambda: self.editor_obj.event_generate('<<Copy>>'))
        self.add_command(label='Paste', accelerator='Ctrl+V',
                         command=lambda: self.editor_obj.event_generate('<<Paste>>'))
        self.add_command(label='Add Timestamp', accelerator='F5', command=self.add_timestamp)
        self.add_command(label='Find and Replace', accelerator='Ctrl+F', command=self.find_and_replace)

    def add_timestamp(self, *args):
        self.editor_obj.insert(tk.INSERT, datetime.now().strftime('%I:%M %p %m/%d/%Y'))
        self.editor_obj.edit_modified(True)
        self.parent.title(f'*{self.parent.filename}')

    def find_and_replace(self, *args):
        if isinstance(self.parent.FIND_AND_REP_WIN, tk.Toplevel):
            self.__quit_find_and_replace()
        self.parent.FIND_AND_REP_WIN = tk.Toplevel()
        self.parent.FIND_AND_REP_WIN.resizable(False, False)
        self.parent.FIND_AND_REP_WIN.protocol('WM_DELETE_WINDOW', self.__quit_find_and_replace)
        self.parent.FIND_AND_REP_WIN.bind('<Destroy>', self.__quit_find_and_replace)
        _ = FindAndReplaceWin(self.parent.FIND_AND_REP_WIN, self.parent.editor)

    def __quit_find_and_replace(self, *args):
        clear_tags('found', self.editor_obj)
        if isinstance(self.parent.FIND_AND_REP_WIN, tk.Toplevel):
            self.parent.FIND_AND_REP_WIN.destroy()
