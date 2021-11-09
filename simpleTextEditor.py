
"""
TEXT EDITOR FOR TKINTER
Written by Joshua Kitchen - March 2021
A basic text editor app with file, edit, format, and tool menus implemented in tkinter.
UPDATED MAY 2021:
- added find and replace functionality
- various tweaks and bug fixes
"""

from datetime import datetime
import os
from pathlib import Path
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog, font as tk_font


FIND_AND_REP_WIN = None
FONT_CHOOSE_WIN = None


class Editor(tk.Text):
    def __init__(self, parent):
        tk.Text.__init__(self, wrap=tk.WORD, undo=True)
        self.parent = parent
        self.settings_file = 'editor_settings'
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w+') as file:
                file.write('font-family:monospace\nfont-size:12')
            self.font = 'monospace'
            self.font_size = 12
        else:
            self.load_settings()
        self.scrollbar = ttk.Scrollbar(self.parent, command=self.yview, cursor='arrow')
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.configure(yscrollcommand=self.scrollbar.set, relief=tk.FLAT)
        self.tag_configure('found', foreground='white', background='red')

    def load_settings(self):
        try:
            with open(self.settings_file, 'r+') as file:
                settings = file.readlines()
                if not settings:
                    file.write('font-family:monospace\nfont-size:12')
                    self.font = 'monospace'
                    self.font_size = 12
                    self.configure(font=(self.font, self.font_size))
                    return
        except PermissionError:
            messagebox.showerror('Error', 'Could not open settings file')
            self.font = 'monospace'
            self.font_size = 12
        except OSError:
            messagebox.showerror('Error', 'Could not open settings file')
            self.font = 'monospace'
            self.font_size = 12
        self.font = settings[0].split(':')[1].strip('\n')
        try:
            self.font_size = int(settings[1].split(':')[1])
        except ValueError:
            self.font_size = 12
        self.configure(font=(self.font, self.font_size))


class FileMenu(tk.Menu):
    def __init__(self, parent, text_widget):
        tk.Menu.__init__(self, tearoff=0)
        self.recent_files_save_file = 'recent_files'
        if not os.path.exists(self.recent_files_save_file):
            with open(self.recent_files_save_file, 'w+') as file:
                file.write('')
        self.parent = parent
        self.text_widget = text_widget
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

    def __save_file(self):
        text = self.text_widget.get(0.0, tk.END)
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
        self.text_widget.edit_modified(False)

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
        if self.filepath in self.recent_files:
            self.recent_files.remove(self.filepath)
        self.recent_files.insert(0, self.filepath)
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
            if os.path.exists(f"{os.path.split(self.filepath)[-1]}_ignore"):
                os.rename(f"{os.path.split(self.filepath)[-1]}_ignore", f"{os.path.split(chosen_filepath)[-1]}_ignore")
            self.filepath = chosen_filepath
        self.update_recent_files()
        self.__save_file()

    def open_file(self, filepath):
        global FIND_AND_REP_WIN, FONT_CHOOSE_WIN
        try:
            filepath = os.path.abspath(filepath)
            with open(filepath, 'r') as file:
                text = file.read()
        except PermissionError:
            messagebox.showerror('Error', 'Permission denied!')
            return
        except OSError:
            messagebox.showerror('Error', 'Could not open file!')
            return
        except UnicodeDecodeError:
            messagebox.showerror('Error', 'Could not open file!')
            return
        filename = os.path.split(filepath)[-1]
        self.filepath = filepath
        self.parent.title(filename)
        self.parent.filename = filename
        self.update_recent_files()
        if isinstance(FIND_AND_REP_WIN, tk.Toplevel):
            FIND_AND_REP_WIN.destroy()
        if isinstance(FONT_CHOOSE_WIN, tk.Toplevel):
            FONT_CHOOSE_WIN.destroy()
        self.text_widget.delete(0.0, tk.END)
        self.text_widget.insert(0.0, text.strip('\n'))
        self.text_widget.edit_modified(False)

    def open_from_filemanager(self, *args):
        filename = os.path.split(self.filepath)[-1]
        if self.text_widget.edit_modified() == 1:
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
        global FIND_AND_REP_WIN, FONT_CHOOSE_WIN
        if self.text_widget.edit_modified() == 1:
            filename = os.path.split(self.filepath)[-1]
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.save()
        self.text_widget.delete(0.0, tk.END)
        self.filepath = 'Untitled.txt'
        self.parent.filename = self.filepath
        self.parent.title(self.filepath)
        self.text_widget.edit_modified(False)
        if isinstance(FIND_AND_REP_WIN, tk.Toplevel):
            FIND_AND_REP_WIN.destroy()
        if isinstance(FONT_CHOOSE_WIN, tk.Toplevel):
            FONT_CHOOSE_WIN.destroy()


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
        global FIND_AND_REP_WIN
        if isinstance(FIND_AND_REP_WIN, tk.Toplevel):
            self.__quit_find_and_replace()
        FIND_AND_REP_WIN = tk.Toplevel()
        FIND_AND_REP_WIN.protocol('WM_DELETE_WINDOW', self.__quit_find_and_replace)
        FIND_AND_REP_WIN.bind('<Destroy>', self.__quit_find_and_replace)
        _ = FindAndReplaceWin(FIND_AND_REP_WIN, self.text_widget)

    def __quit_find_and_replace(self, *args):
        global FIND_AND_REP_WIN
        clear_tags('found', self.text_widget)
        if isinstance(FIND_AND_REP_WIN, tk.Toplevel):
            FIND_AND_REP_WIN.destroy()


class FormatMenu(tk.Menu):
    def __init__(self, parent, text_widget):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.text_widget = text_widget
        self.add_command(label='Editor Font', command=self.change_font)
        self.font_size_menu = tk.Menu(self.parent, tearoff=0)
        self.sizes = [8, 9, 10, 11, 12, 13, 14, 18, 20, 24, 28, 30, 35, 40]
        for size in self.sizes:
            if size == self.text_widget.font_size:
                self.font_size_menu.add_command(label=f"•{size}", command=lambda s=size: self.change_font_size(s))
            else:
                self.font_size_menu.add_command(label=f"  {size}", command=lambda s=size: self.change_font_size(s))
        self.add_cascade(label='Editor Text Size', menu=self.font_size_menu)

    def change_font(self):
        global FONT_CHOOSE_WIN
        if isinstance(FONT_CHOOSE_WIN, tk.Toplevel):
            FONT_CHOOSE_WIN.destroy()
        FONT_CHOOSE_WIN = tk.Toplevel()
        _ = FontChooser(FONT_CHOOSE_WIN, self.text_widget)
        FONT_CHOOSE_WIN.focus_set()

    def change_font_size(self, text_size):
        with open(self.text_widget.settings_file, 'r') as file:
            lines = file.readlines()
        with open(self.text_widget.settings_file, 'w') as file:
            lines[1] = f"font-size:{text_size}"
            file.write(f"{lines[0].strip()}\n{lines[1]}")
        self.text_widget.load_settings()
        self.font_size_menu.delete(0, tk.END)
        for size in self.sizes:
            if size == self.text_widget.font_size:
                self.font_size_menu.add_command(label=f"•{size}", command=lambda s=size: self.change_font_size(s))
            else:
                self.font_size_menu.add_command(label=f"  {size}", command=lambda s=size: self.change_font_size(s))


class FontChooser:
    """Simple interface for choosing a font"""
    def __init__(self, parent, controller):
        self.parent = parent
        self.parent.title("Font")
        self.parent.geometry("400x250")
        self.controller = controller
        self.font_list = sorted(set(tk_font.families()))
        self.font_box = tk.Listbox(self.parent, height=1100, takefocus=1, exportselection=0)
        for font in self.font_list:
            self.font_box.insert(tk.END, font)
        self.font_box.pack(expand=True, fill=tk.BOTH)
        self.scrollbar = ttk.Scrollbar(self.font_box)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.configure(command=self.font_box.yview)
        self.font_box.configure(yscrollcommand=self.scrollbar.set)
        self.preview = tk.Text(self.parent, width=50, height=2.5)
        self.preview.insert(0.0, "Preview text. This box is editable, feel free to type anything")
        self.confirm = ttk.Button(self.parent, text="Confirm", command=self.save_font_choice)
        self.preview.pack(expand=True, fill=tk.BOTH, pady=10)
        self.confirm.pack()
        self.font_box.bind('<ButtonRelease-1>', self.change_preview_font)
        self.font_box.bind('<KeyRelease-Up>', self.change_preview_font)
        self.font_box.bind('<KeyRelease-Down>', self.change_preview_font)
        # TODO: get current font to be the default selected font
        self.font_box.select_set(0)
        self.font_box.activate(0)
        self.font_box.event_generate("<<ListboxSelect>>")
        self.font_box.focus_set()

    def change_preview_font(self, event):
        preview_font = self.font_box.get(tk.ACTIVE if event.type.name == 'KeyRelease' else tk.ANCHOR)
        self.preview.configure(font=(preview_font, 12))

    def save_font_choice(self):
        with open(self.controller.settings_file, 'r') as file:
            lines = file.readlines()
        with open(self.controller.settings_file, 'w') as file:
            new_font = self.font_box.get(self.font_box.curselection())
            if new_font == "":
                return
            lines[0] = f"font-family:{new_font}"
            file.write(f"{lines[0]}\n{lines[1]}")
        self.controller.load_settings()
        self.parent.destroy()


class FindAndReplaceWin:
    """Simple interface for find and replace operations"""
    def __init__(self, parent, text_widget):
        self.parent = parent
        self.parent.title("Find and Replace")
        self.text_widget = text_widget
        self.counter = 1
        self.found_words = []
        self.find_entry = ttk.Entry(self.parent)
        self.find_button = ttk.Button(self.parent, text="Find", command=self.find)
        self.replace_entry = ttk.Entry(self.parent)
        self.replace_button = ttk.Button(self.parent, text="Replace", command=self.replace)
        self.replace_all_button = ttk.Button(self.parent, text="Replace All", command=self.replace_all)
        self.next = ttk.Button(self.parent, text="Next", command=self.next_instance)
        self.prev = ttk.Button(self.parent, text="Prev", command=self.previous_instance)
        self.word_count_label = tk.Label(self.parent, text="0/0")
        self.whitespace1 = ttk.Label(self.parent, text="    ")
        self.whitespace2 = ttk.Label(self.parent, text="    ")
        self.find_entry.grid(row=0, column=0, padx=10)
        self.find_button.grid(row=0, column=1)
        self.next.grid(row=0, column=2)
        self.prev.grid(row=0, column=3)
        self.replace_entry.grid(row=1, column=0, padx=10)
        self.replace_button.grid(row=1, column=1)
        self.replace_all_button.grid(row=1, column=2)
        self.word_count_label.grid(row=2, column=0)
        clear_tags('found', self.text_widget)

    def find(self):
        self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
        clear_tags('found', self.text_widget)
        if self.found_words:
            self.counter = 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
            self.text_widget.tag_add('found', self.found_words[self.counter - 1][0],
                                     self.found_words[self.counter - 1][1])
        else:
            self.word_count_label.configure(text="None")

    def find_all(self):
        self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
        clear_tags('found', self.text_widget)
        if self.found_words:
            self.counter = 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
            for word in self.found_words:
                self.text_widget.tag_add('found', word[0], word[1])
        else:
            self.word_count_label.configure(text="None")

    def replace(self):
        if not self.found_words:
            return
        word = self.found_words.pop(self.counter - 1)
        self.text_widget.delete(word[0], word[1])
        self.text_widget.insert(word[0], self.replace_entry.get())
        self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
        if not self.found_words:
            self.word_count_label.configure(text="None")
            return
        self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
        self.counter -= 1
        self.next_instance()

    def replace_all(self):
        if not self.found_words:
            return
        clear_tags('found', self.text_widget)
        for i in range(len(self.found_words)):
            next_word = get_word_indexes(self.find_entry.get(), self.text_widget)[0]
            self.text_widget.delete(next_word[0], next_word[1])
            self.text_widget.insert(next_word[0], self.replace_entry.get())
        self.found_words = []
        self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")

    def next_instance(self):
        if self.counter + 1 > len(self.found_words):
            return
        if not self.found_words:
            return
        clear_tags('found', self.text_widget)
        self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
        self.counter += 1
        self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
        self.text_widget.tag_add('found', self.found_words[self.counter - 1][0],
                                 self.found_words[self.counter - 1][1])

    def previous_instance(self):
        if self.counter == 1:
            return
        if not self.found_words:
            return
        else:
            clear_tags('found', self.text_widget)
            self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
            self.counter -= 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
            self.text_widget.tag_add('found', self.found_words[self.counter - 1][0],
                                     self.found_words[self.counter - 1][1])


class FindWin:
    def __init__(self, parent, text_widget):
        self.parent = parent
        self.parent.title("Find")
        self.text_widget = text_widget
        # below is a flag that prevents next and previous methods from being called while user has activated "find_all"
        self.find_mode = False
        self.counter = 1
        self.found_words = []
        self.find_entry = ttk.Entry(self.parent)
        self.find_button = ttk.Button(self.parent, text="Find", command=self.find)
        self.find_all_button = ttk.Button(self.parent, text="Find all", command=self.find_all)
        self.next = ttk.Button(self.parent, text="Next", command=self.next_instance)
        self.prev = ttk.Button(self.parent, text="Previous", command=self.previous_instance)
        self.word_count_label = tk.Label(self.parent, text="0/0 Instances")
        self.whitespace1 = ttk.Label(self.parent, text="    ")
        self.whitespace2 = ttk.Label(self.parent, text="    ")
        self.find_entry.grid(row=0, column=0, padx=10)
        self.find_button.grid(row=0, column=1)
        self.find_all_button.grid(row=0, column=2)
        self.prev.grid(row=1, column=1)
        self.next.grid(row=1, column=2)
        self.word_count_label.grid(row=1, column=0)
        clear_tags('found', self.text_widget)

    def find(self):
        self.find_mode = True
        self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
        clear_tags('found', self.text_widget)
        if self.found_words:
            self.counter = 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)} Instances")
            self.text_widget.tag_add('found', self.found_words[self.counter - 1][0],
                                     self.found_words[self.counter - 1][1])
        else:
            self.word_count_label.configure(text="None")

    def find_all(self):
        self.find_mode = False
        self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
        clear_tags('found', self.text_widget)
        if self.found_words:
            self.counter = 1
            self.word_count_label.configure(text=f"{len(self.found_words)} Instances")
            for word in self.found_words:
                self.text_widget.tag_add('found', word[0], word[1])
        else:
            self.word_count_label.configure(text="None")

    def next_instance(self):
        if self.find is False:
            return
        if self.counter + 1 > len(self.found_words):
            return
        if not self.found_words:
            return
        clear_tags('found', self.text_widget)
        self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
        self.counter += 1
        self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)} Instances")
        self.text_widget.tag_add('found', self.found_words[self.counter - 1][0],
                                 self.found_words[self.counter - 1][1])

    def previous_instance(self):
        if self.find is False:
            return
        if self.counter == 1:
            return
        if not self.found_words:
            return
        else:
            clear_tags('found', self.text_widget)
            self.found_words = get_word_indexes(self.find_entry.get(), self.text_widget)
            self.counter -= 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)} Instances")
            self.text_widget.tag_add('found', self.found_words[self.counter - 1][0],
                                     self.found_words[self.counter - 1][1])


def get_word_indexes(word, text_widget, start=1.0):
    """
    A helper function that finds the start and end indexes of every instance of a word within a text widget
    """
    out = []
    while start != text_widget.index(tk.END):
        word_start = text_widget.search(word, start, stopindex=tk.END)
        if word_start == '':
            break
        index = word_start.split(".")
        column = index[0]
        row = index[1]
        new_row = int(row) + len(word)
        word_end = f"{column}.{new_row}"
        start = word_end
        out.append((word_start, word_end))
    return out


def clear_tags(tag, text_widget):
    """
    A helper function that clears a specified tag from within a text widget
    """
    old_tags = []
    ranges = text_widget.tag_ranges(tag)
    for i in range(0, len(ranges), 2):
        start = ranges[i]
        stop = ranges[i + 1]
        old_tags.append((tag, str(start), str(stop)))
    for old_tag in old_tags:
        text_widget.tag_remove(old_tag[0], old_tag[1], old_tag[2])


class StatusBar(ttk.Label):
    def __init__(self, parent):
        ttk.Label.__init__(self)
        self.parent = parent
        self.line = tk.StringVar()
        self.column = tk.StringVar()
        self.line.set("0")
        self.column.set("0")
        self.status_text = f"Ln {self.line.get()}, Col {self.column.get()}"
        self.configure(text=self.status_text, anchor='e')


class Main(tk.Tk):
    def __init__(self, in_file=None):
        tk.Tk.__init__(self)
        self.filename = 'Untitled.txt'
        self.geometry('1000x500')
        self.title(self.filename)
        self.protocol('WM_DELETE_WINDOW', self.close)
        # Editor
        self.editor = Editor(self)
        self.editor.pack(expand=True, fill=tk.BOTH)
        # Menu
        self.main_menu = tk.Menu(self)
        self.file_menu = FileMenu(self, self.editor)
        self.edit_menu = EditMenu(self, self.editor)
        self.format_menu = FormatMenu(self, self.editor)
        self.main_menu.add_cascade(menu=self.file_menu, label='File')
        self.main_menu.add_cascade(menu=self.edit_menu, label='Edit')
        self.main_menu.add_cascade(menu=self.format_menu, label='Format')
        self.configure(menu=self.main_menu)
        # Status Bar
        self.status = StatusBar(self)
        self.status.pack(fill=tk.X)
        # Key Bindings
        self.bind('<F5>', self.edit_menu.add_timestamp)
        self.bind('<Control_L>f', self.edit_menu.find_and_replace)
        self.bind('<Control_L>o', self.file_menu.open_from_filemanager)
        self.bind('<Control_L>s', self.file_menu.save)
        self.bind('<Control_L>n', self.file_menu.new_file)
        # Handle file passed as command line arg
        self.in_file = in_file
        if in_file:
            self.file_menu.open_file(self.in_file)
        self.general_update()

    def general_update(self):
        # Update edit_modified flag in self.editor and modify self.title
        if self.editor.edit_modified():
            self.filename = os.path.split(self.file_menu.filepath)[-1]
            self.title(f'*{self.filename}')
        # Update Line and Column
        index = self.editor.index(tk.INSERT)
        index = index.split('.')
        self.status.line.set(index[0])
        self.status.column.set(index[1])
        self.status.configure(text=f"Ln {self.status.line.get()}, Col {self.status.column.get()}")
        self.after(100, self.general_update)  # runs general update every 100 milliseconds

    def close(self):
        self.file_menu.store_recent_files()
        if self.editor.edit_modified() == 0:
            self.quit()
        else:
            answer = messagebox.askyesnocancel(title='Save?', message=f'Do you want to save {self.filename} '
                                                                      f'before quitting?')
            if answer == 'yes':
                self.file_menu.save()
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
