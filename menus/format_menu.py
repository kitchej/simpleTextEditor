import tkinter as tk

from dialogs.font_chooser import FontChooser


class FormatMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, tearoff=0)
        self.parent = parent
        self.editor_obj = self.parent.editor
        self.add_command(label='Editor Font', command=self.change_font)
        self.font_size_menu = tk.Menu(self.parent, tearoff=0)
        self.sizes = [8, 9, 10, 11, 12, 13, 14, 18, 20, 24, 28, 30, 35, 40]
        for size in self.sizes:
            if size == self.editor_obj.font_size:
                self.font_size_menu.add_command(label=f"•{size}", command=lambda s=size: self.change_font_size(s))
            else:
                self.font_size_menu.add_command(label=f"  {size}", command=lambda s=size: self.change_font_size(s))
        self.add_cascade(label='Editor Text Size', menu=self.font_size_menu)

    def change_font(self):
        if isinstance(self.parent.FONT_CHOOSE_WIN, tk.Toplevel):
            self.parent.FONT_CHOOSE_WIN.destroy()
        self.parent.FONT_CHOOSE_WIN = tk.Toplevel()
        self.parent.FONT_CHOOSE_WIN.resizable(False, False)
        _ = FontChooser(self.parent.FONT_CHOOSE_WIN, self.editor_obj)
        self.parent.FONT_CHOOSE_WIN.focus_set()

    def change_font_size(self, text_size):
        self.editor_obj.font_size = int(text_size)
        self.editor_obj.update_font()
        self.font_size_menu.delete(0, tk.END)
        for size in self.sizes:
            if size == self.editor_obj.font_size:
                self.font_size_menu.add_command(label=f"•{size}", command=lambda s=size: self.change_font_size(s))
            else:
                self.font_size_menu.add_command(label=f"  {size}", command=lambda s=size: self.change_font_size(s))