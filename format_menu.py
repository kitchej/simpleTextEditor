import tkinter as tk

from font_chooser import FontChooser


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
        if isinstance(self.parent.FONT_CHOOSE_WIN, tk.Toplevel):
            self.parent.FONT_CHOOSE_WIN.destroy()
        self.parent.FONT_CHOOSE_WIN = tk.Toplevel()
        self.parent.FONT_CHOOSE_WIN.resizable(False, False)
        _ = FontChooser(self.parent.FONT_CHOOSE_WIN, self.text_widget)
        self.parent.FONT_CHOOSE_WIN.focus_set()

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