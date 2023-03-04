import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

from syntax_highlighting.python import PythonSyntaxHighlighter
from syntax_highlighting.c import CSyntaxHighlighter


class FileMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, tearoff=0)
        self.recent_files_save_file = '../.recentFiles'
        if not os.path.exists(self.recent_files_save_file):
            with open(self.recent_files_save_file, 'w+') as file:
                file.write('')
        self.parent = parent
        self.editor_obj = self.parent.editor
        self.recent_files = self.get_recent_files()
        self.filepath = 'Untitled.txt'
        self.add_command(label='Open', accelerator='Ctrl+O', command=lambda: self.open_from_filemanager())
        self.recent_menu = tk.Menu(self.parent, tearoff=0)
        for f in self.recent_files:
            if os.path.exists(f):
                self.recent_menu.add_command(
                    label=f"{os.path.split(f)[-1].strip()}",
                    command=lambda name=f.strip(): self.open_file(name))
        self.add_cascade(label='Recent Files', menu=self.recent_menu)
        self.add_command(label='Save', accelerator='Ctrl+S', command=self.save)
        self.add_command(label='Save as', command=self.save_as)
        self.add_command(label='New', accelerator='Ctrl+N', command=self.new_file)

        self.syntax_highlighters = {"py": PythonSyntaxHighlighter(self.editor_obj),
                                    'c': CSyntaxHighlighter(self.editor_obj)}

    def __config_syntax_highlighter(self, filename):
        filename = os.path.split(filename)[-1]
        extension = filename.split('.')
        if len(extension) > 1:
            extension = extension[-1]
            try:
                self.parent.syntax_highlighter = self.syntax_highlighters[extension]
            except KeyError:
                self.parent.syntax_highlighter = None
        else:
            self.parent.syntax_highlighter = None
        self.parent.update_syntax_highlighting()

    def __save_file(self):
        text = self.editor_obj.get(0.0, tk.END)
        try:
            with open(self.filepath, 'w+') as file:
                file.write(text)
        except PermissionError:
            messagebox.showerror('Error', 'Permission denied!')
            return
        except OSError:
            messagebox.showerror('Error', 'Could not save file!')
            return
        self.parent.title(os.path.split(self.filepath)[-1])
        self.editor_obj.edit_modified(False)

    def get_recent_files(self):
        with open(self.recent_files_save_file, 'r') as f:
            files = f.read()
            recent_files = []
        for file in files.split(','):
            if not os.path.exists(file):
                continue
            recent_files.append(file)
        return recent_files

    def store_recent_files(self):
        with open(self.recent_files_save_file, 'w+') as file:
            for f in self.recent_files:
                file.write(f"{f},")

    def update_recent_files(self):
        path = self.filepath
        if os.name == 'nt':
            path = path.replace('/', '\\')
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        if len(self.recent_files) > 5:
            self.recent_files.pop()
        self.recent_menu.delete(0, tk.END)
        for f in self.recent_files:
            if os.path.exists(f):
                self.recent_menu.add_command(
                    label=f"{os.path.split(f)[-1].strip()}",
                    command=lambda name=f.strip(): self.open_file(name))

    def save(self, *args):
        if os.path.exists(self.filepath):
            self.__save_file()
        else:
            self.save_as()

    def save_as(self):
        chosen_filepath = filedialog.asksaveasfilename(filetypes=[('All', '*'), ('.txt', '*.txt')],
                                                       initialdir=Path.home())
        if chosen_filepath == ():
            messagebox.showerror('Error', 'File not saved!')
            return
        else:
            self.filepath = chosen_filepath
        self.update_recent_files()
        self.__save_file()
        self.__config_syntax_highlighter(os.path.split(self.filepath)[-1])

    def open_file(self, filepath):
        filename = os.path.split(self.filepath)[-1]
        if self.editor_obj.edit_modified() == 1:
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.save()
        try:
            filepath = os.path.abspath(filepath)
            with open(filepath, 'r') as file:
                text = file.read()
        except PermissionError as e:
            messagebox.showerror('Error', f'Could not open {filepath}')
            return
        except UnicodeDecodeError as e:
            messagebox.showerror('Error', f'Could not open {filepath}')
            return
        except OSError as e:
            messagebox.showerror('Error', f'Could not open {filepath}')
            return

        filename = os.path.split(filepath)[-1]
        self.filepath = filepath
        self.parent.title(filename)
        self.parent.filename = filename
        self.update_recent_files()
        if isinstance(self.parent.FIND_AND_REP_WIN, tk.Toplevel):
            self.parent.FIND_AND_REP_WIN.destroy()
        if isinstance(self.parent.FONT_CHOOSE_WIN, tk.Toplevel):
            self.parent.FONT_CHOOSE_WIN.destroy()
        self.editor_obj.delete(0.0, tk.END)
        self.editor_obj.insert(0.0, text.strip('\n'))
        self.editor_obj.edit_modified(False)
        self.__config_syntax_highlighter(filename)

    def open_from_filemanager(self, *args):
        filename = os.path.split(self.filepath)[-1]
        if self.editor_obj.edit_modified() == 1:
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.save()
        chosen_filepath = filedialog.askopenfilename(filetypes=[('All', '*'), ('.txt', '*.txt')],
                                                     initialdir=Path.home())

        if chosen_filepath == () or chosen_filepath == '':
            return

        if not os.path.exists(chosen_filepath):
            messagebox.showerror('Unknown File', f'Could not find file: {chosen_filepath}')
            return

        self.open_file(os.path.abspath(chosen_filepath))

    def new_file(self, *args):
        if self.editor_obj.edit_modified() == 1:
            filename = os.path.split(self.filepath)[-1]
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.save()
        self.editor_obj.delete(0.0, tk.END)
        self.filepath = 'Untitled.txt'
        self.parent.filename = self.filepath
        self.parent.title(self.filepath)
        self.parent.syntax_highlighter = None
        self.editor_obj.edit_modified(False)
        if isinstance(self.parent.FIND_AND_REP_WIN, tk.Toplevel):
            self.parent.FIND_AND_REP_WIN.destroy()
        if isinstance(self.parent.FONT_CHOOSE_WIN, tk.Toplevel):
            self.parent.FONT_CHOOSE_WIN.destroy()
