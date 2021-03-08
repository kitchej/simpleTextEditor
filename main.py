import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font as tk_font
from pathlib import Path
import os
from datetime import datetime

SETTINGS_FILE = os.path.abspath('editor_settings')
RECENT_FILES = os.path.abspath('recent_files')


class Editor(tk.Text):
    def __init__(self, parent, controller):
        tk.Text.__init__(self)
        self.parent = parent
        self.controller = controller
        self.saved = True
        self.scrollbar = tk.Scrollbar(self, command=self.yview_scroll)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.configure(yscrollcommand=self.scrollbar.set)

        # Create an editor settings file if not already present
        if not os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'w+') as file:
                file.write('font-family:monospace\nfont-size:12')
            self.font = 'monospace'
            self.font_size = 12
        else:
            self.load_settings()

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, 'r+') as file:
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
    def __init__(self, parent, controller):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.controller = controller  # Controller should be a tk.Text object
        self.recent_files = self.open_recent_files()
        self.filepath = 'Untitled.txt'
        self.add_command(label='Open', accelerator='Ctrl+O', command=self.open_file)

        self.recent_menu = tk.Menu(self.parent, tearoff=0)
        for f in self.recent_files:
            self.recent_menu.add_command(label=f"{f.split('/')[-1].strip()}",
                                         command=lambda name=f.strip(): self.open_file(name))
        self.add_cascade(label='Recent Files', menu=self.recent_menu)

        self.add_command(label='Save', accelerator='Ctrl+S', command=self.save_file)
        self.add_command(label='Save as', command=self.save_as)
        self.add_command(label='New', accelerator='Ctrl+N', command=self.new_file)

    def save_file(self, *args):
        text = self.controller.get(0.0, tk.END)

        if not os.path.exists(self.filepath):
            self.save_as()
            return

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
        self.controller.saved = True

    def save_as(self):
        chosen_filepath = filedialog.asksaveasfilename(filetypes=[('All', '*'), ('.txt', '*.txt')],
                                                       initialdir=Path.home())
        if chosen_filepath == ():
            messagebox.showerror('Error', 'File not saved!')
            return
        else:
            self.filepath = chosen_filepath

        self.save_file()

    def open_file(self, in_filename=None, *args):
        if not self.controller.saved:
            filename = self.filepath.split('/')[-1]
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.save_file()

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

        self.controller.delete(0.0, tk.END)
        self.controller.insert(0.0, text.strip('\n'))
        self.parent.title(self.filepath.split('/')[-1])
        self.controller.saved = True

        if self.filepath in self.recent_files:
            self.recent_files.remove(self.filepath)
        self.recent_files.insert(0, self.filepath)
        if len(self.recent_files) > 5:
            self.recent_files.pop()

        # Reload the recent files menu
        self.recent_menu.delete(0, tk.END)
        for f in self.recent_files:
            self.recent_menu.add_command(label=f"{f.split('/')[-1].strip()}",
                                         command=lambda name=f.strip(): self.open_file(name))

    def new_file(self, *args):
        if not self.controller.saved:
            filename = self.filepath.split('/')[-1]
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.save_file()

        self.controller.delete(0.0, tk.END)
        self.filepath = 'Untitled.txt'
        self.parent.title(self.filepath)
        self.controller.saved = True

    @staticmethod
    def open_recent_files():
        with open(RECENT_FILES, 'r') as f:
            files = f.read()
            recent_files = []
        for file in files.split(','):
            if not os.path.exists(file):
                continue
            recent_files.append(file)
        return recent_files


class EditMenu(tk.Menu):
    def __init__(self, parent, controller):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.controller = controller  # Controller should be a tk.Text object
        self.add_command(label='Cut', accelerator='Ctrl+X',
                         command=lambda: self.controller.event_generate('<<Cut>>'))

        self.add_command(label='Copy', accelerator='Ctrl+C',
                         command=lambda: self.controller.event_generate('<<Copy>>'))

        self.add_command(label='Paste', accelerator='Ctrl+V',
                         command=lambda: self.controller.event_generate('<<Paste>>'))
        self.add_command(label='Add Timestamp', accelerator='F5',
                         command=self.add_timestamp)

    def add_timestamp(self, *args):
        self.controller.insert(tk.INSERT, datetime.now().strftime('%-I:%M %p %-m/%-d/%Y'))
        self.controller.saved = False


class FontChooser(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self)
        self.parent = parent
        self.controller = controller
        self.font_list = sorted(tk_font.families())

        self.font_box = tk.Listbox(self.parent, selectmode='single')
        for font in self.font_list:
            if '@' in font:
                continue
            self.font_box.insert(tk.END, font)
        self.font_box.pack(expand=True, fill=tk.BOTH)

        self.scrollbar = tk.Scrollbar(self.font_box)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.configure(command=self.font_box.yview)
        self.font_box.configure(yscrollcommand=self.scrollbar.set)

        self.preview = tk.Text(self.parent, width=50, height=5)
        self.preview.pack(expand=True, fill=tk.BOTH)
        self.preview.insert(0.0, "Preview text. This box is editable, feel free to type anything")

        self.confirm = tk.Button(self.parent, text="Confirm", command=self.save_font_choice)
        self.confirm.pack()

        self.font_box.bind('<Double-Button-1>', self.change_preview_font)

    def change_preview_font(self, *args):
        preview_font = self.font_box.get(self.font_box.curselection())
        self.preview.configure(font=(preview_font, 12))

    def save_font_choice(self):
        with open(SETTINGS_FILE, 'r') as file:
            lines = file.readlines()
        with open(SETTINGS_FILE, 'w') as file:
            new_font = self.font_box.get(self.font_box.curselection())
            if new_font == "":
                return
            lines[0] = f"font-family:{new_font}"
            file.write(f"{lines[0]}\n{lines[1]}")
        self.controller.load_settings()
        self.parent.destroy()


class FormatMenu(tk.Menu):
    def __init__(self, parent, controller):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.controller = controller
        self.font_choice_menu = FontChooser(self, self)
        self.add_command(label='Font', command=self.change_font)

        self.font_size_menu = tk.Menu(self.parent, tearoff=0)
        self.sizes = [8, 9, 10, 11, 12, 13, 14, 18, 20, 24, 28, 30, 35, 40]
        for size in self.sizes:
            self.font_size_menu.add_command(label=f"{size}", command=lambda s=size: self.change_font_size(s))
        self.add_cascade(label='Text Size', menu=self.font_size_menu)

    def change_font(self):
        temp = tk.Toplevel()
        f = FontChooser(temp, self.controller)

    def change_font_size(self, text_size):
        with open(SETTINGS_FILE, 'r') as file:
            lines = file.readlines()
        with open(SETTINGS_FILE, 'w') as file:
            lines[1] = f"font-size:{text_size}"
            file.write(f"{lines[0].strip()}\n{lines[1]}")
        self.controller.load_settings()


class StatusBar(tk.Label):
    def __init__(self, parent, controller):
        tk.Label.__init__(self)
        self.parent = parent
        self.controller = controller
        self.line = tk.StringVar()
        self.column = tk.StringVar()
        self.line.set("0")
        self.column.set("0")
        self.status_text = f"Ln: {self.line.get()} Col: {self.column.get()}"
        self.configure(relief='sunken', text=self.status_text, anchor='e')

    def update_text(self):
        print(self.controller.INSERT)


class Main(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('1000x500')
        self.title('Untitled.txt')
        self.protocol('WM_DELETE_WINDOW', self.close)
        # Editor
        self.editor = Editor(self, self)
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
        self.status = StatusBar(self, self.editor)
        self.status.pack(fill=tk.X)
        # Key Bindings
        self.bind('<Key>', self.general_update)
        self.bind('<Button-1>', self.general_update)
        self.bind('<F5>', self.edit_menu.add_timestamp)
        self.bind('<Control_L>o', self.file_menu.open_file)
        self.bind('<Control_L>s', self.file_menu.save_file)
        self.bind('<Control_L>n', self.file_menu.new_file)

        # Create recent files file if not already created
        if not os.path.exists(RECENT_FILES):
            with open(RECENT_FILES, 'w+') as file:
                file.write('')

    def save_recent_files(self):
        with open(RECENT_FILES, 'w+') as file:
            for f in self.file_menu.recent_files:
                file.write(f"{f},")
    
    # Updates:
    #       - The self.editor.save flag 
    #       - Line and Column number
    def general_update(self, *args):
        # Update self.editor.saved flag and modify self.title
        self.editor.saved = False
        filename = self.file_menu.filepath.split('/')[-1]
        self.title(f'*{filename}')
        # Update Line and Column
        index = self.editor.index(tk.INSERT)
        index = index.split('.')
        self.status.line.set(index[0])
        self.status.column.set(index[1])
        self.status.configure(text=f"Line: {self.status.line.get()} Col: {self.status.column.get()}")

    def close(self):
        self.save_recent_files()
        if self.editor.saved:
            self.quit()
        else:
            name = self.file_menu.filepath.split('/')[-1]
            answer = messagebox.askyesnocancel(title='Save?', message=f'Do you want to save {name} before quitting?')

            if answer == 'yes':
                self.file_menu.save_file()
                self.quit()
            elif answer is None:
                return
            else:
                self.quit()


if __name__ == '__main__':
    Main().mainloop()
