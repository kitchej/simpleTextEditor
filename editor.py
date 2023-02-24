import os
import tkinter as tk
from tkinter import messagebox


class Editor(tk.Text):
    def __init__(self, parent):
        tk.Text.__init__(self, wrap=tk.WORD, undo=True)
        self.parent = parent
        self.settings_file = '.config'
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w+') as file:
                file.write('font-family:Arial\nfont-size:14')
            self.font = 'Arial'
            self.font_size = 14
        else:
            self.load_settings()
        self.tag_configure('found', foreground='white', background='red')

    def update_font(self):
        self.configure(font=(self.font, self.font_size))

    def update_config(self):
        with open(self.settings_file, 'w+') as file:
            file.write(f'font-family:{self.font}\nfont-size:{self.font_size}')

    def load_settings(self):
        try:
            with open(self.settings_file, 'r+') as file:
                settings = file.readlines()
                if not settings:
                    file.write('font-family:Arial\nfont-size:14')
                    self.font = 'Arial'
                    self.font_size = 14
                    self.configure(font=(self.font, self.font_size))
                    return
        except PermissionError:
            messagebox.showerror('Error', 'Could not open settings file')
            self.font = 'Arial'
            self.font_size = 14
        except OSError:
            messagebox.showerror('Error', 'Could not open settings file')
            self.font = 'Arial'
            self.font_size = 14
        self.font = settings[0].split(':')[1].strip('\n')
        try:
            self.font_size = int(settings[1].split(':')[1])
        except ValueError:
            self.font_size = 14
        self.update_font()
