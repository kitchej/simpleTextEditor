import tkinter as tk
from tkinter import messagebox
import sys

from text_editor_classes import Editor, FileMenu, EditMenu, ToolsMenu, FormatMenu


class StatusBar(tk.Label):
    def __init__(self, parent, text_widget):
        tk.Label.__init__(self)
        self.parent = parent
        self.text_widget = text_widget
        self.line = tk.StringVar()
        self.column = tk.StringVar()
        self.line.set("0")
        self.column.set("0")
        self.status_text = f"Ln: {self.line.get()} Col: {self.column.get()}"
        self.configure(relief='sunken', text=self.status_text, anchor='e')


class Main(tk.Tk):
    def __init__(self, in_file=None):
        tk.Tk.__init__(self)
        self.geometry('1000x500')
        self.title('Untitled.txt')
        self.protocol('WM_DELETE_WINDOW', self.close)
        # Editor
        self.editor = Editor(self)
        self.editor.pack(expand=True, fill=tk.BOTH)
        # Menu
        self.main_menu = tk.Menu(self)
        self.file_menu = FileMenu(self, self.editor)
        self.edit_menu = EditMenu(self, self.editor)
        self.tools_menu = ToolsMenu(self, self.editor, self.file_menu)
        self.format_menu = FormatMenu(self, self.editor)
        self.main_menu.add_cascade(menu=self.file_menu, label='File')
        self.main_menu.add_cascade(menu=self.edit_menu, label='Edit')
        self.main_menu.add_cascade(menu=self.tools_menu, label='Tools')
        self.main_menu.add_cascade(menu=self.format_menu, label='Format')
        self.configure(menu=self.main_menu)
        # Status Bar
        self.status = StatusBar(self, self.editor)
        self.status.pack(fill=tk.X)
        # Key Bindings
        self.bind('<Key>', self.general_update)
        self.bind('<Button-1>', self.general_update)
        self.bind('<F5>', self.edit_menu.add_timestamp)
        self.bind('<F7>', self.tools_menu.spell_check)
        self.bind('<Control_L>f', self.tools_menu.find_and_replace)
        self.bind('<Control_L>o', self.file_menu.open_file)
        self.bind('<Control_L>s', self.file_menu.quick_save)
        self.bind('<Control_L>n', self.file_menu.new_file)
        # Load recent files
        self.in_file = in_file
        if in_file:
            self.file_menu.open_file(in_filename=self.in_file, event=None)

    def general_update(self, *args):
        # Update self.file_menu.saved flag and modify self.title
        if self.editor.edit_modified():
            filename = self.file_menu.filepath.split('/')[-1]
            self.title(f'*{filename}')
        # Update Line and Column
        index = self.editor.index(tk.INSERT)
        index = index.split('.')
        self.status.line.set(index[0])
        self.status.column.set(index[1])
        self.status.configure(text=f"Line: {self.status.line.get()} Col: {self.status.column.get()}")

    def close(self):
        self.file_menu.save_recent_files()
        if self.editor.edit_modified() == 0:
            self.quit()
        else:
            name = self.file_menu.filepath.split('/')[-1]
            answer = messagebox.askyesnocancel(title='Save?', message=f'Do you want to save {name} before quitting?')

            if answer == 'yes':
                self.file_menu.quick_save()
                self.quit()
            elif answer is None:
                return
            else:
                self.quit()


def main():
    args = sys.argv
    if len(args) > 2:
        print("Too many parameters!")
        return
    elif len(args) == 1:
        m = Main()
    else:
        m = Main(args[1])
    m.mainloop()


if __name__ == '__main__':
    main()
