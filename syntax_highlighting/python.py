from syntax_highlighting.syntax_highlighter import SyntaxHighlighter
import editor
import re


class PythonSyntaxHighlighter(SyntaxHighlighter):
    def __init__(self, text_obj: editor.Editor):
        SyntaxHighlighter.__init__(self, text_obj)
        self.keywords = ['and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
                         'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
                         'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield']

        self.builtins = list(__builtins__.keys())
        for keyword in self.keywords:
            if keyword in self.builtins:
                self.builtins.remove(keyword)

        self.string_regex = re.compile(r"(?i:r|u|f|fr|rf|b|br|rb)?[\"\'][^\"\'].*?[\"\']")
        self.one_line_comment_regex = re.compile(r"#.*(?=\n)")
        self.multiline_comment_regex = re.compile(r"[\"\']{3}.*?[\"\']{3}", re.DOTALL)
        self.func_name_regex = re.compile(r"(?<=def).*(?=\()")

        self.add_tag("keywords", "#cc7a00")
        self.add_tag("bultins", "#0099ff")
        self.add_tag("strings", "#009900")
        self.add_tag("func_names", "#0033cc")
        self.add_tag("comments", "#808080")
        self.add_tag("self", "#b300b3")

    def highlight_syntax(self):
        self._text = self._text_obj.get(0.0, "end")
        for keyword in self.keywords:
            self.highlight_word(keyword, "keywords")
        for builtin in self.builtins:
            self.highlight_word(builtin, "bultins")
        self.highlight_word("self", "self")
        self.highlight_pattern(self.string_regex, "strings")
        self.highlight_pattern(self.func_name_regex, "func_names")
        self.highlight_pattern(self.one_line_comment_regex, "comments")
        self.highlight_pattern(self.multiline_comment_regex, "strings")
