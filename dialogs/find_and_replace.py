import tkinter as tk
import tkinter.ttk as ttk

import editor
from utils import get_word_indexes, clear_tags


class FindAndReplaceWin:
    """Simple interface for find and replace operations"""
    def __init__(self, parent, editor_obj: editor.Editor):
        self.parent = parent
        self.parent.title("Find and Replace")
        self.editor_obj = editor_obj
        self.counter = 1
        self.found_words = []
        self.find_entry = ttk.Entry(self.parent, width=25)
        self.find_button = ttk.Button(self.parent, text="Find", command=lambda: self.find_words(False))
        self.find_all_button = ttk.Button(self.parent, text="Find All", command=lambda: self.find_words(True))
        self.replace_entry = ttk.Entry(self.parent, width=25)
        self.replace_button = ttk.Button(self.parent, text="Replace", command=self.replace)
        self.replace_all_button = ttk.Button(self.parent, text="Replace All", command=self.replace_all)
        self.navigation_frame = tk.Frame(self.parent)
        self.next = ttk.Button(self.navigation_frame, text="Next", command=self.next_instance)
        self.prev = ttk.Button(self.navigation_frame, text="Prev", command=self.previous_instance)
        self.word_count_label = tk.Label(self.navigation_frame, text="0/0")
        self.find_entry.grid(row=0, column=0, padx=10)
        self.find_button.grid(row=0, column=1, padx=5)
        self.find_all_button.grid(row=0, column=2, padx=(0, 10))
        self.replace_entry.grid(row=1, column=0, padx=5)
        self.replace_button.grid(row=1, column=1)
        self.replace_all_button.grid(row=1, column=2, padx=(0, 10))
        self.navigation_frame.grid(row=2, column=0, columnspan=4, sticky='w', padx=10, pady=10)
        self.prev.pack(side=tk.LEFT)
        self.word_count_label.pack(side=tk.LEFT, padx=5)
        self.next.pack(side=tk.LEFT)

        clear_tags('found', self.editor_obj)

    def find_words(self, highlight_all):
        word = self.find_entry.get()
        if word == '':
            return
        self.found_words = get_word_indexes(word, self.editor_obj)
        clear_tags('found', self.editor_obj)
        if self.found_words:
            self.counter = 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
            if highlight_all:
                for word in self.found_words:
                    self.editor_obj.tag_add('found', word[0], word[1])
            else:
                self.editor_obj.tag_add('found', self.found_words[self.counter - 1][0],
                                        self.found_words[self.counter - 1][1])
        else:
            self.word_count_label.configure(text="None")

    def find(self):
        word = self.find_entry.get()
        if word == '':
            return
        self.found_words = get_word_indexes(word, self.editor_obj)
        clear_tags('found', self.editor_obj)
        if self.found_words:
            self.counter = 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
            self.editor_obj.tag_add('found', self.found_words[self.counter - 1][0],
                                           self.found_words[self.counter - 1][1])
        else:
            self.word_count_label.configure(text="None")

    def find_all(self):
        word = self.find_entry.get()
        if word == '':
            return
        self.found_words = get_word_indexes(word, self.editor_obj)
        clear_tags('found', self.editor_obj)
        if self.found_words:
            self.counter = 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
            for word in self.found_words:
                self.editor_obj.tag_add('found', word[0], word[1])
        else:
            self.word_count_label.configure(text="None")

    def replace(self):
        if not self.found_words:
            return
        word = self.found_words.pop(self.counter - 1)
        self.editor_obj.delete(word[0], word[1])
        self.editor_obj.insert(word[0], self.replace_entry.get())
        self.found_words = get_word_indexes(self.find_entry.get(), self.editor_obj)
        if not self.found_words:
            self.word_count_label.configure(text="None")
            return
        self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
        self.counter -= 1
        self.next_instance()

    def replace_all(self):
        if not self.found_words:
            return
        clear_tags('found', self.editor_obj)
        for i in range(len(self.found_words)):
            next_word = get_word_indexes(self.find_entry.get(), self.editor_obj)[0]
            self.editor_obj.delete(next_word[0], next_word[1])
            self.editor_obj.insert(next_word[0], self.replace_entry.get())
        self.found_words = []
        self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")

    def next_instance(self):
        if self.counter + 1 > len(self.found_words):
            return
        if not self.found_words:
            return
        clear_tags('found', self.editor_obj)
        self.found_words = get_word_indexes(self.find_entry.get(), self.editor_obj)
        self.counter += 1
        self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
        self.editor_obj.tag_add('found', self.found_words[self.counter - 1][0],
                                       self.found_words[self.counter - 1][1])
        self.editor_obj.see(self.found_words[self.counter - 1][0])

    def previous_instance(self):
        if self.counter == 1:
            return
        if not self.found_words:
            return
        else:
            clear_tags('found', self.editor_obj)
            self.found_words = get_word_indexes(self.find_entry.get(), self.editor_obj)
            self.counter -= 1
            self.word_count_label.configure(text=f"{self.counter}/{len(self.found_words)}")
            self.editor_obj.tag_add('found', self.found_words[self.counter - 1][0],
                                           self.found_words[self.counter - 1][1])
            self.editor_obj.see(self.found_words[self.counter - 1][0])


if __name__ == '__main__':
    class Dummy:
        def __init__(self):
            self.editor = tk.Text()

    root = tk.Tk()
    d = Dummy()
    f = FindAndReplaceWin(root, d)
    root.mainloop()