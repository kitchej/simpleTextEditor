from syntax_highlighting.syntax_highlighter import SyntaxHighlighter
import editor
import tkinter as tk
import re


class CSyntaxHighlighter(SyntaxHighlighter):
    def __init__(self, text_obj: editor.Editor):
        SyntaxHighlighter.__init__(self, text_obj)

        self.keywords = ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else',
                         'enum', 'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short',
                         'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
                         'volatile', 'while', 'NULL']

        self.string_regex = re.compile(r"[\"\'<][^\"\'].*?[\"\'>]")
        self.marcro_regex = re.compile(r"#.*?\s")
        self.one_line_comment_regex = re.compile(r"//.*(?=\n)")
        self.multiline_comment_regex = re.compile(r"/\*.*?\*/", re.DOTALL)
        self.func_name_regex = re.compile(r"(?<=int)\s[\w_]*(?=\()")

        self.add_tag("keywords", "#cc7a00")
        self.add_tag("strings", "#009900")
        self.add_tag("func_names", "#0033cc")
        self.add_tag("macros", "#b300b3")

    def highlight_syntax(self):
        self._text = self._text_obj.get(0.0, tk.END)
        for keyword in self.keywords:
            self.highlight_word(keyword, "keywords")
        self.highlight_pattern(self.marcro_regex, "macros")
        self.highlight_pattern(self.string_regex, "strings")
        self.highlight_pattern(self.func_name_regex, "func_names")
        self.highlight_pattern(self.one_line_comment_regex, "comments")
        self.highlight_pattern(self.multiline_comment_regex, "strings")