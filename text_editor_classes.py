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


class Editor(tk.Text):
    def __init__(self, parent):
        tk.Text.__init__(self)
        self.parent = parent
        self.settings_file = 'editor_settings'
        
        # Create an editor settings file if not already present
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w+') as file:
                file.write('font-family:monospace\nfont-size:12')
            self.font = 'monospace'
            self.font_size = 12
        else:
            self.load_settings()
            
        self.scrollbar = tk.Scrollbar(self, command=self.yview_scroll)
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
        self.saved = True
        
        self.recent_files = self.open_recent_files()
        self.filepath = ''
        self.add_command(label='Open', accelerator='Ctrl+O', command=lambda: self.open_file(event=None))

        self.recent_menu = tk.Menu(self.parent, tearoff=0)
        for f in self.recent_files:
            self.recent_menu.add_command(label=f"{f.split('/')[-1].strip()}",
                                         command=lambda name=f.strip(): self.open_file(in_filename=name, event=None))
        self.add_cascade(label='Recent Files', menu=self.recent_menu)

        self.add_command(label='Save', accelerator='Ctrl+S', command=self.quick_save)
        self.add_command(label='Save as', command=self.save_as)
        self.add_command(label='New', accelerator='Ctrl+N', command=self.new_file)

       
    def save_recent_files(self):
        with open(self.recent_files_save, 'w+') as file:
            for f in self.recent_files:
                file.write(f"{f},")

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
        self.saved = True

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
        
        self.save_file()

    def open_file(self, event, in_filename=None):
        if not self.saved:
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
        self.saved = True

        # Add to recent files
        if self.filepath in self.recent_files:
            self.recent_files.remove(self.filepath)
        self.recent_files.insert(0, self.filepath)
        if len(self.recent_files) > 5:
            self.recent_files.pop()

        # Reload the recent files menu
        self.recent_menu.delete(0, tk.END)
        for f in self.recent_files:
            self.recent_menu.add_command(label=f"{f.split('/')[-1].strip()}",
                                         command=lambda name=f.strip(): self.open_file(in_filename=name, event=None))

    def new_file(self, *args):
        if not self.saved:
            filename = self.filepath.split('/')[-1]
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.quick_save()

        self.text_widget.delete(0.0, tk.END)
        self.filepath = 'Untitled.txt'
        self.parent.title(self.filepath)
        self.saved = True

    def open_recent_files(self):
        with open(self.recent_files_save, 'r') as f:
            files = f.read()
            recent_files = []
        for file in files.split(','):
            if not os.path.exists(file):
                continue
            recent_files.append(file)
        return recent_files


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
        self.add_command(label='Add Timestamp', accelerator='F5',
                         command=self.add_timestamp)

    def add_timestamp(self, *args):
        self.text_widget.insert(tk.INSERT, datetime.now().strftime('%I:%M %p %m/%d/%Y'))


class FormatMenu(tk.Menu):
    def __init__(self, parent, text_widget):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.text_widget = text_widget
        self.font_choice_menu = FontChooser(self, self)
        self.add_command(label='Font', command=self.change_font)

        self.font_size_menu = tk.Menu(self.parent, tearoff=0)
        self.sizes = [8, 9, 10, 11, 12, 13, 14, 18, 20, 24, 28, 30, 35, 40]
        for size in self.sizes:
            self.font_size_menu.add_command(label=f"{size}", command=lambda s=size: self.change_font_size(s))
        self.add_cascade(label='Text Size', menu=self.font_size_menu)

    def change_font(self):
        temp = tk.Toplevel()
        f = FontChooser(temp, self.text_widget)

    def change_font_size(self, text_size):
        with open(self.text_widget.settings_file, 'r') as file:
            lines = file.readlines()
        with open(self.text_widget.settings_file, 'w') as file:
            lines[1] = f"font-size:{text_size}"
            file.write(f"{lines[0].strip()}\n{lines[1]}")
        self.text_widget.load_settings()


# Simple interface for choosing a font
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
    root.configure(menu=main_menu)
    root.mainloop()
