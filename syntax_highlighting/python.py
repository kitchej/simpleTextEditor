from syntax_highlighting.syntax_highlighter import SyntaxHighlighter
import editor
import tkinter as tk
import re


class PythonSyntaxHighlighter(SyntaxHighlighter):
    def __init__(self, text_obj: editor.Editor):
        SyntaxHighlighter.__init__(self, text_obj)
        self.keywords = ['and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
                         'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
                         'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield']
        self.type_names = ["int", "float", "complex", "str", "bool" "list", "tuple", "range", "bytes", "bytearray",
                           "memoryview", "set", "frozenset", "dict"]

        self.string_regex = re.compile("(r|u|f|fr|rf|b|br|rb)?[\"\'].*[\"\']")
        self.comment_regex = re.compile(r"#.*$")  # Triple quoted comments are already caught by the string regex
        self.func_name_regex = re.compile(r"(?<=def).*(?=\()")
        self.regex_patterns = [self.func_name_regex, self.comment_regex, self.string_regex]

    def highlight_func_names(self):
        length = tk.IntVar()
        text = self.text_obj.get(0.0, tk.END)
        matches = re.findall(self.func_name_regex, text)
        for match in matches:
            start = self.text_obj.search(match, '1.0', count=length)
            word_start_index = start.split(".")
            start_row = int(word_start_index[0])
            start_column = int(word_start_index[1])
            end_column = start_column + length.get()
            word_end = f"{start_row}.{end_column}"
            self.text_obj.tag_add("func_names", start, word_end)