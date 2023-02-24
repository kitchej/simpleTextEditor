import tkinter.ttk as ttk


class StatusBar(ttk.Label):
    def __init__(self, parent):
        ttk.Label.__init__(self)
        self.parent = parent
        self.line = 1
        self.column = 1
        self.status_text = f"Ln {self.line}, Col {self.column}"
        self.configure(text=self.status_text, anchor='e')

    def update_line_and_col(self, line, col):
        self.line = line
        self.column = col
        self.configure(text=f"Ln {self.line}, Col {self.column}")
