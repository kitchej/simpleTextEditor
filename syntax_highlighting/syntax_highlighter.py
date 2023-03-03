from abc import ABC, abstractmethod
import editor
import utils
import tkinter as tk
import re


class SyntaxHighlighter(ABC):
    def __init__(self, text_obj: editor.Editor):
        ABC.__init__(self)
        self.text_obj = text_obj
        self.text = ""
        self.length = tk.IntVar()
        self.keywords = []
        self.type_names = []
        self.string_regex = "[\"\'].+[\"\']"
        self.func_name_regex = ""
        self.comment_regex = ""
        self.keyword_color = "#ff9900"
        self.type_name_color = "#0033cc"
        self.string_color = "#009900"
        self.func_name_color = "#b300b3"
        self.comment_color = "#808080"
        self.text_obj.tag_configure("keywords", foreground=self.keyword_color)
        self.text_obj.tag_configure("strings", foreground=self.string_color)
        self.text_obj.tag_configure("type_names", foreground=self.type_name_color)
        self.text_obj.tag_configure("comment", foreground=self.comment_color)
        self.text_obj.tag_configure("func_names", foreground=self.func_name_color)
        self.tag_names = ["keywords", "strings", "type_names", "comment", "func_names"]
        self.regex_patterns = {}

    def highlight_keywords(self):
        for keyword in self.keywords:
            indexes = utils.get_word_indexes(f"\\m{keyword}\\M", self.text_obj, regex=True)
            for index in indexes:
                self.text_obj.tag_add("keywords", index[0], index[1])

    def highlight_type_names(self):
        for type_name in self.type_names:
            indexes = utils.get_word_indexes(f"\\m{type_name}\\M", self.text_obj, regex=True)
            for index in indexes:
                self.text_obj.tag_add("type_names", index[0], index[1])

    def highlight_strings(self):
        # indexes = utils.get_word_indexes(self.string_regex, self.text_obj, regex=True)
        # for index in indexes:
        #     self.text_obj.tag_add("strings", index[0], index[1])
        length = tk.IntVar()
        text = self.text_obj.get(0.0, tk.END)
        matches = re.findall(self.string_regex, text)
        for match in matches:
            start = self.text_obj.search(match, '1.0', count=length)
            word_start_index = start.split(".")
            start_row = int(word_start_index[0])
            start_column = int(word_start_index[1])
            end_column = start_column + length.get()
            word_end = f"{start_row}.{end_column}"
            self.text_obj.tag_add("strings", start, word_end)

    def highlight_comments(self):
        # indexes = utils.get_word_indexes(self.comment_regex, self.text_obj, regex=True)
        # for index in indexes:
        #     self.text_obj.tag_add("comment", index[0], index[1])

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

    def highlight_func_names(self):
        indexes = utils.get_word_indexes(self.func_name_regex, self.text_obj, regex=True)
        for index in indexes:
            self.text_obj.tag_add("func_names", index[0], index[1])

    def highlight_other(self):
        pass

    def highlight_syntax(self):
        self.text = self.text_obj.get("1.0", tk.END)
        self.highlight_keywords()
        self.highlight_type_names()
        self.highlight_strings()
        self.highlight_func_names()
        self.highlight_comments()
        self.highlight_other()




