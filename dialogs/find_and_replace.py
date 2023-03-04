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
        self.word_counter = 1
        self.found_words = []
        self.match_word = tk.IntVar()
        self.match_case = tk.IntVar()
        self.match_case.set(0)
        self.match_word.set(0)
        self.is_find_all = None

        self.find_entry = ttk.Entry(self.parent, width=25)
        self.find_button = ttk.Button(self.parent, text="Find", command=self.find)
        self.find_all_button = ttk.Button(self.parent, text="Find All", command=self.find_all)
        self.match_case_label = ttk.Label(self.parent, text="Match Case")
        self.match_case_check = ttk.Checkbutton(self.parent, variable=self.match_case, command=self.refresh_found_words)
        self.match_case_check.state(['!alternate'])
        self.match_word_label = ttk.Label(self.parent, text="Match Word")
        self.match_word_check = ttk.Checkbutton(self.parent, variable=self.match_word, command=self.refresh_found_words)
        self.match_word_check.state(['!alternate'])
        self.replace_entry = ttk.Entry(self.parent, width=25)
        self.replace_button = ttk.Button(self.parent, text="Replace", command=self.replace)
        self.replace_all_button = ttk.Button(self.parent, text="Replace All", command=self.replace_all)
        self.navigation_frame = tk.Frame(self.parent)
        self.next = ttk.Button(self.navigation_frame, text="Next", command=self.next_instance)
        self.prev = ttk.Button(self.navigation_frame, text="Prev", command=self.previous_instance)
        self.word_count_label = tk.Label(self.navigation_frame, text="0/0")

        self.find_entry.grid(row=0, column=0, padx=10)
        self.find_button.grid(row=0, column=1)
        self.find_all_button.grid(row=0, column=2, padx=(0, 3))
        self.match_case_label.grid(row=0, column=3)
        self.match_case_check.grid(row=0, column=4)
        self.match_word_label.grid(row=0, column=5)
        self.match_word_check.grid(row=0, column=6, padx=(0, 10))
        self.replace_entry.grid(row=1, column=0, padx=5)
        self.replace_button.grid(row=1, column=1)
        self.replace_all_button.grid(row=1, column=2)
        self.navigation_frame.grid(row=2, column=0, columnspan=4, sticky='w', padx=10, pady=10)

        clear_tags('found', self.editor_obj)

    def refresh_found_words(self):
        if self.find_all is None:
            return
        if self.is_find_all:
            self.find_all()
        else:
            self.find()

    def find_words(self):
        word = self.find_entry.get()
        if word == '':
            return

        if self.match_word.get():
            self.found_words = get_word_indexes(f"\\m{word}\\M", self.editor_obj, regex=True,
                                                no_case=not self.match_case.get())
        else:
            self.found_words = get_word_indexes(word, self.editor_obj, no_case=not self.match_case.get())
        clear_tags('found', self.editor_obj)
        if self.found_words:
            self.word_counter = 1
            if self.is_find_all:
                for word in self.found_words:
                    self.editor_obj.tag_add('found', word[0], word[1])
                self.word_count_label.configure(text=f"Total: {len(self.found_words)}")
            else:
                self.editor_obj.tag_add('found', self.found_words[self.word_counter - 1][0],
                                        self.found_words[self.word_counter - 1][1])
                self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_words)}")
        else:
            self.word_count_label.configure(text="None")

    def find(self):
        if self.is_find_all or self.is_find_all is None:
            self.is_find_all = False
            self.word_count_label.pack_forget()
            self.prev.pack(side=tk.LEFT)
            self.word_count_label.pack(side=tk.LEFT, padx=5)
            self.next.pack(side=tk.LEFT)
        self.find_words()

    def find_all(self):
        if not self.is_find_all or self.is_find_all is None:
            self.is_find_all = True
            self.word_count_label.pack_forget()
            self.prev.pack_forget()
            self.next.pack_forget()
            self.word_count_label.pack(padx=45)
        self.find_words()

    def replace(self):
        if not self.found_words:
            return
        word = self.found_words.pop(self.word_counter - 1)
        self.editor_obj.delete(word[0], word[1])
        self.editor_obj.insert(word[0], self.replace_entry.get())

        self.found_words = get_word_indexes(self.find_entry.get(), self.editor_obj, match_word=self.match_word.get(),
                                            match_case=self.match_case.get())
        if not self.found_words:
            self.word_count_label.configure(text="None")
            return
        self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_words)}")
        self.word_counter -= 1
        self.next_instance()

    def replace_all(self):
        if not self.found_words:
            return
        clear_tags('found', self.editor_obj)
        start = '1.0'
        for i in range(len(self.found_words)):
            self.found_words = get_word_indexes(self.find_entry.get(), self.editor_obj,
                                                match_word=self.match_word.get(),
                                                match_case=self.match_case.get(),
                                                start=start)
            if not self.found_words:
                return
            next_word = self.found_words[0]
            self.editor_obj.delete(next_word[0], next_word[1])
            self.editor_obj.insert(next_word[0], self.replace_entry.get())
            start = next_word[1]
        self.found_words = []
        self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_words)}")

    def next_instance(self):
        if self.word_counter + 1 > len(self.found_words):
            return
        if not self.found_words:
            return
        clear_tags('found', self.editor_obj)
        self.word_counter += 1
        self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_words)}")
        self.editor_obj.tag_add('found', self.found_words[self.word_counter - 1][0],
                                self.found_words[self.word_counter - 1][1])
        self.editor_obj.see(self.found_words[self.word_counter - 1][0])

    def previous_instance(self):
        if self.word_counter == 1:
            return
        if not self.found_words:
            return
        else:
            clear_tags('found', self.editor_obj)
            self.word_counter -= 1
            self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_words)}")
            self.editor_obj.tag_add('found', self.found_words[self.word_counter - 1][0],
                                    self.found_words[self.word_counter - 1][1])
            self.editor_obj.see(self.found_words[self.word_counter - 1][0])
