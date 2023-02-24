"""
TEXT EDITOR FOR TKINTER
Written by Joshua Kitchen - March 2021
A basic text editor app with file, edit, format, and tool menus implemented in tkinter.
"""

import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

from editor import Editor
from menus.file_menu import FileMenu
from menus.edit_menu import EditMenu
from menus.format_menu import FormatMenu
from status_bar import StatusBar


class Main(tk.Tk):
    def __init__(self, in_file=None):
        tk.Tk.__init__(self)

        self.FIND_AND_REP_WIN = None
        self.FONT_CHOOSE_WIN = None

        self.filename = 'Untitled.txt'
        self.geometry('1000x500')
        self.title(self.filename)
        self.protocol('WM_DELETE_WINDOW', self.close)

        self.editor_frame = tk.Frame(self)
        self.editor_frame.pack_propagate(False)
        self.editor = Editor(self.editor_frame)

        self.scrollbar = ttk.Scrollbar(self, command=self.editor.yview, cursor='arrow')
        self.editor.configure(yscrollcommand=self.scrollbar.set, relief=tk.FLAT)

        self.status = StatusBar(self)

        self.main_menu = tk.Menu(self)
        self.file_menu = FileMenu(self)
        self.edit_menu = EditMenu(self)
        self.format_menu = FormatMenu(self)
        self.main_menu.add_cascade(menu=self.file_menu, label='File')
        self.main_menu.add_cascade(menu=self.edit_menu, label='Edit')
        self.main_menu.add_cascade(menu=self.format_menu, label='Format')
        self.configure(menu=self.main_menu)

        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.bind('<F5>', self.edit_menu.add_timestamp)
        self.bind('<Control_L>f', self.edit_menu.find_and_replace)
        self.bind('<Control_L>o', self.file_menu.open_from_filemanager)
        self.bind('<Control_L>s', self.file_menu.save)
        self.bind('<Control_L>n', self.file_menu.new_file)

        self.in_file = in_file
        if in_file:
            self.file_menu.open_file(self.in_file)
        self.update_gui()

    def update_gui(self):
        if self.editor.edit_modified():
            self.filename = os.path.split(self.file_menu.filepath)[-1]
            self.title(f'*{self.filename}')

        index = self.editor.index(tk.INSERT)
        index = index.split('.')
        self.status.update_line_and_col(index[0], index[1])
        # Update the GUI every 100 milliseconds
        self.after(100, self.update_gui)

    def close(self):
        self.file_menu.store_recent_files()
        if self.editor.edit_modified() == 0:
            self.editor.update_config()
            self.quit()
        else:
            answer = messagebox.askyesnocancel(title='Save?', message=f'Do you want to save {self.filename}'
                                                                      f' before quitting?')
            if answer:
                self.file_menu.save()
                self.editor.update_config()
                self.quit()
            elif answer is None:
                return
            else:
                self.editor.update_config()
                self.quit()


def main():
    args = sys.argv
    if len(args) > 2:
        print("Usage: simpleTextEditor.py [filepath]")
        return
    elif len(args) == 1:
        m = Main()
    else:
        m = Main(args[1])
    m.mainloop()


if __name__ == '__main__':
    main()
