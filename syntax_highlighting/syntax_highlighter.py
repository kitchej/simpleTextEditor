"""
Syntax Highlighter for tkEdit
Written by Joshua Kitchen - March 2023

Abstract base class for creating custom syntax highlighters
See syntax_highlighting/python.py for an example implementation

NOTE: While Tkinter has it's own regex engine (it uses TCL's regex engine), I chose to go with the Python's regex
engine because it's a little more sophisticated than the one provided by Tkinter. If you don't want to use Python's
regex engine, you can always override the highlight_pattern() method to use whatever regex engine you want. If you're
dead set on using Tkinter's regex engine, utils.get_string_indexes() supports TCL's regex engine. Just set the
'regex' option to True.
"""


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
        '''
        Interface for adding a tag from the editor
        NOTE: In Tkinter, tags have a stack order. Tags added last will show up over tags added earlier
        if you want to customize this order, use self._text_obj.tag_lower(tagName, belowThis=None) and
        self._text_obj.tag_raise(tagName, aboveThis=None)

        '''
        self._text_obj.tag_configure(tag_name, foreground=color)
        self._tag_names.append(tag_name)

    def remove_tag(self, tag_name: str):
        '''
        Interface for removing a tag from the editor
        Returns:
            True if the tag was successfully removed
            False if the tag did not exist
        '''
        if tag_name in self._tag_names:
            self._tag_names.remove(tag_name)
            self._text_obj.tag_delete(tag_name)
            return True
        else:
            return False

    def highlight_pattern(self, pattern: re.Pattern, tag_name):
        '''
        Highlights a section of text given an re.Pattern object with the tag given by tag_name
        Returns:
            (True, matches) if a match or matches were found
            False if no matches were found
        '''
        matches = re.findall(pattern, self._text)
        if not matches:
            return False
        for match in matches:
            indexes = utils.get_string_indexes(match, self._text_obj)
            for index in indexes:
                self._text_obj.tag_add(tag_name, index[0], index[1])
        return True, matches

    def highlight_word(self, word, tag_name):
        '''
        Highlights a word within the text with the tag given by tag_name
        Returns:
            (True, indexes) if a the word was found
            False if the word was not found in the text
        '''
        indexes = utils.get_string_indexes(f"\\m{word}\\M", self._text_obj, regex=True)
        if not indexes:
            return False
        for index in indexes:
            self._text_obj.tag_add(tag_name, index[0], index[1])
        return True, indexes

    @abstractmethod
    def highlight_syntax(self):
        '''
        This is the method called when syntax highlighting takes place (in Main.update_syntax_highlighting)
        self._text should always assigned here first with self._text_obj.get("0.0", "end")
        '''
        pass
