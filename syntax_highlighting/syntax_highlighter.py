from abc import ABC, abstractmethod
import editor
import utils
import tkinter as tk
import re


class SyntaxHighlighter(ABC):
    def __init__(self, text_obj: editor.Editor):
        ABC.__init__(self)
        self._match_length = tk.IntVar()
        self._text = ""
        self._text_obj = text_obj
        self._patterns = {}
        self._tag_names = []

    def get_tag_names(self):
        return self._tag_names

    def add_tag(self, tag_name: str, color: str):
        self._text_obj.tag_configure(tag_name, foreground=color)
        self._tag_names.append(tag_name)

    def remove_tag(self, tag_name: str):
        if tag_name in self._tag_names:
            self._tag_names.remove(tag_name)
            self._text_obj.tag_delete(tag_name)
            return True
        else:
            return False

    def highlight_pattern(self, pattern: re.Pattern, tag_name):
        if self._text == "":
            return False
        matches = re.findall(pattern, self._text)
        if len(matches) == 0:
            return False
        for match in matches:
            indexes = utils.get_word_indexes(match, self._text_obj)
            for index in indexes:
                self._text_obj.tag_add(tag_name, index[0], index[1])
        return True, matches

    def highlight_word(self, word, tag_name):
        indexes = utils.get_word_indexes(f"\\m{word}\\M", self._text_obj, regex=True)
        if len(indexes) == 0:
            return False, indexes
        for index in indexes:
            self._text_obj.tag_add(tag_name, index[0], index[1])
        return True

    @abstractmethod
    def highlight_syntax(self):
        pass
