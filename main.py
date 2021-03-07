import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font as tk_font
from pathlib import Path
import os
from datetime import datetime


class Editor(tk.Text):
    def __init__(self, parent, controller):
        tk.Text.__init__(self)
        self.parent = parent
        self.controller = controller

        if not os.path.exists('editor_settings'):
            with open('editor_settings', 'w+') as file:
                file.write('font-family monospace\nfont-size 12')
            self.font = 'monospace'
            self.font_size = 12
        else:
            try:
                with open('editor_settings', 'r') as file:
                    settings = file.readlines()
            except PermissionError:
                messagebox.showerror('Error', 'Could not open settings file')
                self.font = 'monospace'
                self.font_size = 12
            except OSError:
                messagebox.showerror('Error', 'Could not open settings file')
                self.font = 'monospace'
                self.font_size = 12

            self.font = settings[0].split()[1]
            try:
                self.font_size = int(settings[1].split()[1])
            except ValueError:
                self.font_size = 12

        self.configure(font=(self.font, self.font_size))


class FileMenu(tk.Menu):
    def __init__(self, parent, controller):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.controller = controller  # Controller should be a tk.Text object
        self.filepath = 'Untitled.txt'
        self.add_command(label='Open', accelerator='Ctrl+O', command=self.open_file)
        self.add_command(label='Save', accelerator='Ctrl+S', command=self.save_file)
        self.add_command(label='Save as', command=self.save_as)
        self.add_command(label='New', accelerator='Ctrl+N', command=self.new_file)

    def save_file(self):
        text = self.controller.get(0.0, tk.END)

        if self.filepath == 'Untitled.txt':
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

    def save_as(self):
        self.filepath = filedialog.asksaveasfilename(filetypes=[('.txt', '*.txt')], initialdir=Path.home())

        self.save_file()

    def open_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[('All', '*'), ('.txt', '*.txt')], initialdir=Path.home())

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

    def new_file(self):
        text = self.controller.get(0.0, tk.END)
        with open(self.filepath) as file:
            saved_text = file.read()

        if saved_text != text:
            filename = self.filepath.split('/')[-1]
            answer = messagebox.askyesno('Save?', f'Would you like to save {filename} first?')
            if answer:
                self.save_file()

        self.controller.delete(0.0, tk.END)
        self.filepath = 'Untitled.txt'
        self.parent.title(self.filepath)

    def mark_as_unsaved(self, event):
        filename = self.filepath.split('/')[-1]
        self.parent.title(f'*{filename}')


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

    def add_timestamp(self, event):
        self.controller.insert(tk.INSERT, datetime.now().strftime('%I:%M %p %m/%d/%Y'))


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

        self.preview = tk.Text(self.parent, width=50, height=5)
        self.preview.pack(expand=True, fill=tk.BOTH)
        self.preview.insert(0.0, "Preview text. This box is editable, feel free to type anything")

        self.confirm = tk.Button(self.parent, text="Confirm", command=self.save_font_choice)
        self.confirm.pack()

        self.font_box.bind('<Double-Button-1>', self.change_preview_font)

    def change_preview_font(self, event):
        preview_font = self.font_box.get(self.font_box.curselection())
        self.preview.configure(font=(preview_font, 12))

    def save_font_choice(self):
        self.controller.font_choice.set(self.font_box.get(self.font_box.curselection()))
        self.parent.destroy()


class FormatMenu(tk.Menu):
    def __init__(self, parent, controller):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.controller = controller
        self.font_choice = tk.StringVar()
        self.font_choice.set("")
        self.font_choice_menu = FontChooser(self, self)
        self.add_command(label='Font', command=self.change_font)
        self.add_command(label='Text Size')

    def change_font(self):
        temp = tk.Toplevel()
        f = FontChooser(temp, self)
        self.controller.configure(font=(self.font_choice.get(), self.controller.font_size))


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
        # Key Bindings
        self.bind('<Key>', self.file_menu.mark_as_unsaved)
        self.bind('<F5>', self.edit_menu.add_timestamp)

    def close(self):
        if self.file_menu.filepath == 'Untitled.txt' and self.editor.get(0.0, tk.END).strip('\n') == '':
            self.quit()
            return

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
