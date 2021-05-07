"""
TEXT EDITOR KIT FOR TKINTER
Written by Joshua Kitchen - March 2021

Simple editor widget with file, edit, and format menus for a tkinter app
"""
import tkinter as tk
from tkinter import messagebox, filedialog, font as tk_font
from datetime import datetime
import os
from pathlib import Path

from spellchecker import SpellChecker


class Editor(tk.Text):
    def __init__(self, parent):
        tk.Text.__init__(self)
        self.parent = parent
        self.settings_file = 'editor_settings'
        self.configure(undo=True)
        
        # Create an editor settings file if not already present
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w+') as file:
                file.write('font-family:monospace\nfont-size:12')
            self.font = 'monospace'
            self.font_size = 12
        else:
            self.load_settings()
            
        self.scrollbar = tk.Scrollbar(self, command=self.yview, cursor='arrow')
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.configure(yscrollcommand=self.scrollbar.set)

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
        self.recent_files_save = 'recent_files'

        # Create recent files file if not already created
        if not os.path.exists(self.recent_files_save):
            with open(self.recent_files_save, 'w+') as file:
                file.write('')
        self.parent = parent
        self.text_widget = text_widget
        self.recent_files = self.open_recent_files()
        self.filepath = ''
        self.add_command(label='Open', accelerator='Ctrl+O', command=lambda: self.open_file(event=None))
        self.recent_menu = tk.Menu(self.parent, tearoff=0)
        for f in self.recent_files:
            if os.path.exists(f):
                self.recent_menu.add_command(label=f"{f.split('/')[-1].strip()}",
                                             command=lambda name=f.strip(): self.open_file(in_filename=name, event=None))
        self.add_cascade(label='Recent Files', menu=self.recent_menu)
        self.add_command(label='Save', accelerator='Ctrl+S', command=self.quick_save)
        self.add_command(label='Save as', command=self.save_as)
        self.add_command(label='New', accelerator='Ctrl+N', command=self.new_file)

    def open_recent_files(self):
        with open(self.recent_files_save, 'r') as f:
            files = f.read()
            recent_files = []
        for file in files.split(','):
            if not os.path.exists(file):
                continue
            recent_files.append(file)
        return recent_files

    def save_recent_files(self):
        with open(self.recent_files_save, 'w+') as file:
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
                self.recent_menu.add_command(label=f"{f.split('/')[-1].strip()}",
                                             command=lambda name=f.strip(): self.open_file(in_filename=name, event=None))

    def save_file(self):
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
        self.parent.title(self.filepath.split('/')[-1])
        self.text_widget.edit_modified(False)

    def quick_save(self, *args):
        if not os.path.exists(self.filepath):
            self.save_as()
            return
        else:
            self.save_file()

    def save_as(self):
        chosen_filepath = filedialog.asksaveasfilename(filetypes=[('All', '*'), ('.txt', '*.txt')],
                                                       initialdir=Path.home())
        if chosen_filepath == ():
            messagebox.showerror('Error', 'File not saved!')
            return
        else:
            self.filepath = chosen_filepath
        self.update_recent_files()
        self.save_file()

    def open_file(self, event, in_filename=None):
        if self.text_widget.edit_modified() == 1:
            filename = self.filepath.split('/')[-1]
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.quick_save()

        if in_filename:
            self.filepath = in_filename
        else:
            chosen_filepath = filedialog.askopenfilename(filetypes=[('All', '*'), ('.txt', '*.txt')],
                                                         initialdir=Path.home())
            if chosen_filepath == ():
                return
            else:
                self.filepath = chosen_filepath

        if not os.path.exists(self.filepath):
            filename = self.filepath.split('/')[-1]
            messagebox.showerror('Unknown File', f'Could not find file: {filename}')
            return

        try:
            with open(self.filepath, 'r') as file:
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

        self.text_widget.delete(0.0, tk.END)
        self.text_widget.insert(0.0, text.strip('\n'))
        self.parent.title(self.filepath.split('/')[-1])
        self.update_recent_files()
        self.text_widget.edit_modified(False)

    def new_file(self, *args):
        if self.text_widget.edit_modified() == 1:
            filename = self.filepath.split('/')[-1]
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.quick_save()
        self.text_widget.delete(0.0, tk.END)
        self.filepath = 'Untitled.txt'
        self.parent.title(self.filepath)
        self.text_widget.edit_modified(False)


class EditMenu(tk.Menu):
    def __init__(self, parent, text_widget):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.text_widget = text_widget
        self.spell_check_instance = None
        self.add_command(label='Cut', accelerator='Ctrl+X',
                         command=lambda: self.text_widget.event_generate('<<Cut>>'))
        self.add_command(label='Copy', accelerator='Ctrl+C',
                         command=lambda: self.text_widget.event_generate('<<Copy>>'))
        self.add_command(label='Paste', accelerator='Ctrl+V',
                         command=lambda: self.text_widget.event_generate('<<Paste>>'))
        self.add_command(label='Add Timestamp', accelerator='F5',
                         command=self.add_timestamp)
        self.add_command(label='Spell Check', accelerator='F7',
                         command=self.spell_check)

    def add_timestamp(self, *args):
        self.text_widget.insert(tk.INSERT, datetime.now().strftime('%I:%M %p %m/%d/%Y'))

    def spell_check(self, *args):
        if self.spell_check_instance is not None:
            self.spell_check_instance.destroy()
        self.spell_check_instance = tk.Toplevel()
        f = SpellCheckWin(self.spell_check_instance, self.text_widget)


class FormatMenu(tk.Menu):
    def __init__(self, parent, text_widget):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.text_widget = text_widget
        self.font_chooser_instance = None
        self.font_choice_menu = FontChooser(self, self)
        self.add_command(label='Font', command=self.change_font)
        self.font_size_menu = tk.Menu(self.parent, tearoff=0)
        self.sizes = [8, 9, 10, 11, 12, 13, 14, 18, 20, 24, 28, 30, 35, 40]
        for size in self.sizes:
            self.font_size_menu.add_command(label=f"{size}", command=lambda s=size: self.change_font_size(s))
        self.add_cascade(label='Text Size', menu=self.font_size_menu)

    def change_font(self):
        if self.font_chooser_instance is not None:
            self.font_chooser_instance.destroy()
        temp = tk.Toplevel()
        f = FontChooser(temp, self.text_widget)

    def change_font_size(self, text_size):
        with open(self.text_widget.settings_file, 'r') as file:
            lines = file.readlines()
        with open(self.text_widget.settings_file, 'w') as file:
            lines[1] = f"font-size:{text_size}"
            file.write(f"{lines[0].strip()}\n{lines[1]}")
        self.text_widget.load_settings()


class FontChooser:
    """Simple interface for choosing a font"""
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.font_list = sorted(tk_font.families())
        self.font_box = tk.Listbox(self.parent, selectmode='single', height=1100)
        for font in self.font_list:
            if '@' in font:
                continue
            self.font_box.insert(tk.END, font)
        self.font_box.pack(expand=True, fill=tk.BOTH)
        self.scrollbar = tk.Scrollbar(self.font_box)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.configure(command=self.font_box.yview)
        self.font_box.configure(yscrollcommand=self.scrollbar.set)
        self.preview = tk.Text(self.parent, width=50, height=2.5)
        self.preview.insert(0.0, "Preview text. This box is editable, feel free to type anything")
        self.confirm = tk.Button(self.parent, text="Confirm", command=self.save_font_choice)
        self.preview.pack(expand=True, fill=tk.BOTH)
        self.confirm.pack()
        self.font_box.bind('<Double-Button-1>', self.change_preview_font)

    def change_preview_font(self, *args):
        preview_font = self.font_box.get(self.font_box.curselection())
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


class SpellCheckWin:
    def __init__(self, parent, text_widget):
        self.parent = parent
        self.text_widget = text_widget
        self.suggestions = []
        self.punctuation = ['`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '-', '=', '{', '}',
                            '|', '[', ']', '\\', ':', '\"', ';', '\'', '<', '>', '?', ',', '.', '/']
        self.text = self.text_widget.get(0.0, tk.END)
        self.counter = 0
        self.spell_checker = SpellChecker()
        self.current_word = tk.StringVar()
        self.preview = tk.Label(self.parent, textvariable=self.current_word, fg='red')
        self.suggestions_label = tk.Label(self.parent, text="Did you mean?: ")
        self.suggestions_box = tk.Listbox(self.parent, height=5)
        self.replace_button = tk.Button(self.parent, text='Replace', command=self.replace)
        self.replace_all_button = tk.Button(self.parent, text='Replace All', command=self.replace_all)
        self.ignore_button = tk.Button(self.parent, text='Ignore', command=self.ignore)
        self.ignore_all_button = tk.Button(self.parent, text='Ignore All', command=self.ignore_all)
        self.preview.grid(row=0, column=0, pady=10)
        self.suggestions_label.grid(row=1, column=0, pady=5)
        self.suggestions_box.grid(row=2, column=0, columnspan=2)
        self.replace_button.grid(row=3, column=0)
        self.ignore_button.grid(row=3, column=1)
        self.replace_all_button.grid(row=4, column=0)
        self.ignore_all_button.grid(row=4, column=1)
        words = self.parse_words()
        self.misspelled_words = list(self.spell_checker.unknown(words))
        if self.misspelled_words:
            for w in self.misspelled_words:
                self.suggestions.append([w, tuple(self.spell_checker.candidates(w))])
            self.current_word.set(self.suggestions[0][0])
            for i in self.suggestions[0][1]:
                self.suggestions_box.insert(tk.END, i)

    @staticmethod
    def sort_key(item):
        return float(item[1])

    def parse_words(self):
        out = []
        for word in self.text.split():
            if word[0] in self.punctuation:
                word = word.strip(word[1])
            elif word[-1] in self.punctuation:
                word = word.strip(word[-1])
            out.append(word)
        return out

    def get_indexes(self, word):
        """Finds the indexes of misspelled words to aid in replacement"""
        out = []
        start = 1.0
        while start != self.text_widget.index(tk.END):
            word_start = self.text_widget.search(word, start, stopindex=tk.END)
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

    def refresh(self):
        if self.counter > len(self.suggestions) - 1:
            messagebox.showinfo("Complete", "Spell check is complete")
            self.parent.destroy()
            return
        self.current_word.set(self.suggestions[0][0])
        self.suggestions_box.delete(0, tk.END)
        for i in self.suggestions[0][1]:
            self.suggestions_box.insert(tk.END, i)

    def ignore(self):
        self.suggestions.pop(self.counter)
        self.refresh()

    def ignore_all(self):
        word = self.current_word.get()
        self.suggestions = [i for i in self.suggestions if i[0] != word]
        self.refresh()

    def replace(self):
        if self.suggestions_box.curselection() == ():
            return
        indexes = self.get_indexes(self.current_word.get())
        new_word = self.suggestions_box.get(self.suggestions_box.curselection())
        self.text_widget.delete(indexes[0][0], indexes[0][1])
        self.text_widget.insert(indexes[0][0], new_word)
        self.suggestions.pop(self.counter)
        self.refresh()

    def replace_all(self):
        if self.suggestions_box.curselection() == ():
            return
        word = self.current_word.get()
        indexes = self.get_indexes(word)
        new_word = self.suggestions_box.get(self.suggestions_box.curselection())
        for i in indexes:
            self.text_widget.delete(i[0], i[1])
            self.text_widget.insert(i[0], new_word)
        self.suggestions = [i for i in self.suggestions if i[0] != word]
        self.refresh()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1000x500')
    editor = Editor(root)
    editor.pack(expand=True, fill=tk.BOTH)
    main_menu = tk.Menu(root)
    file_menu = FileMenu(root, editor)
    edit_menu = EditMenu(root, editor)
    format_menu = FormatMenu(root, editor)
    main_menu.add_cascade(menu=file_menu, label='File')
    main_menu.add_cascade(menu=edit_menu, label='Edit')
    main_menu.add_cascade(menu=format_menu, label='Format')
    root.bind('<F5>', edit_menu.add_timestamp)
    root.bind('<Control_L>o', file_menu.open_file)
    root.bind('<Control_L>s', file_menu.quick_save)
    root.bind('<Control_L>n', file_menu.new_file)
    root.configure(menu=main_menu)
    root.mainloop()
