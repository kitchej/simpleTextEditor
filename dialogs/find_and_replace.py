import tkinter as tk
import tkinter.ttk as ttk


import editor
import utils


class FindAndReplaceWin:
    """Dialog window for find and replace operations"""

    def __init__(self, parent, editor_obj: editor.Editor):
        self.parent = parent
        self.parent.title("Find and Replace")
        self.editor_obj = editor_obj
        self.word_counter = 1
        self.found_word_indexes = []
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
        self.word_count_label = tk.Label(self.navigation_frame)

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

        utils.clear_tags('found', self.editor_obj)

    def refresh_found_words(self):
        if self.is_find_all is None:
            return
        elif self.is_find_all:
            self.find_all()
        else:
            self.find()

    def get_word_index(self, start='1.0'):
        '''
        Finds a word within the editor and returns it's index
        Returns False if no word was found
        '''
        word = self.find_entry.get()
        if word == '':
            return False
        if self.match_word.get():
            return utils.get_first_string_index(f"\\m{word}\\M", self.editor_obj,
                                                regex=True,
                                                no_case=not self.match_case.get(),
                                                start=start)
        else:
            return utils.get_first_string_index(word, self.editor_obj,
                                                no_case=not self.match_case.get(),
                                                start=start)

    def get_all_word_indexes(self, start='1.0'):
        '''
        Finds all instances of a word within the editor and sets self.found_word_indexes
        Returns False if no words were found
        Returns True if words were found
        '''
        word = self.find_entry.get()
        if word == '':
            return False
        if self.match_word.get():
            self.found_word_indexes = utils.get_string_indexes(f"\\m{word}\\M", self.editor_obj,
                                                               regex=True,
                                                               no_case=not self.match_case.get(),
                                                               start=start)
        else:
            self.found_word_indexes = utils.get_string_indexes(word, self.editor_obj,
                                                               no_case=not self.match_case.get(),
                                                               start=start)
        if self.found_word_indexes:
            return True
        else:
            return False

    def find(self):
        if self.is_find_all or self.is_find_all is None:
            self.is_find_all = False
            self.word_count_label.pack_forget()
            self.prev.pack(side=tk.LEFT)
            self.word_count_label.pack(side=tk.LEFT, padx=5)
            self.next.pack(side=tk.LEFT)
        utils.clear_tags('found', self.editor_obj)
        result = self.get_all_word_indexes()
        if not result:
            self.word_count_label.configure(text="None")
        else:
            self.word_counter = 1
            self.editor_obj.tag_add('found', self.found_word_indexes[self.word_counter - 1][0],
                                    self.found_word_indexes[self.word_counter - 1][1])
            self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_word_indexes)}")
            self.editor_obj.see(self.found_word_indexes[0][0])

    def find_all(self):
        if not self.is_find_all or self.is_find_all is None:
            self.is_find_all = True
            self.word_count_label.pack_forget()
            self.prev.pack_forget()
            self.next.pack_forget()
            self.word_count_label.pack(padx=45)
            self.word_counter = 1
        utils.clear_tags('found', self.editor_obj)
        result = self.get_all_word_indexes()
        if not result:
            self.word_count_label.configure(text="None")
        else:
            for word in self.found_word_indexes:
                self.editor_obj.tag_add('found', word[0], word[1])
            self.word_count_label.configure(text=f"Total: {len(self.found_word_indexes)}")

    def replace(self):
        if not self.found_word_indexes:
            return
        index = self.found_word_indexes[self.word_counter - 1]
        self.editor_obj.delete(index[0], index[1])
        self.editor_obj.insert(index[0], self.replace_entry.get())
        # Since that we changed the text, we need to redo all the indexes
        result = self.get_all_word_indexes(start=index[1])
        if not result:
            self.word_count_label.configure(text="None")
            return
        self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_word_indexes)}")
        self.word_counter -= 1
        self.next_instance()

    def replace_all(self):
        if not self.found_word_indexes:
            return
        replace_word = self.replace_entry.get()
        utils.clear_tags('found', self.editor_obj)
        # Since that are constantly changing the text, we will ignore the
        # indexes self.found_word_indexes and just find the words as we go
        start = '1.0'
        for i in range(len(self.found_word_indexes)):
            word_start, word_end = self.get_word_index(start=start)
            self.editor_obj.delete(word_start, word_end)
            self.editor_obj.insert(word_start, replace_word)
            start = word_end
        self.found_word_indexes = []
        self.word_count_label.configure(text=f"None")

    def next_instance(self):
        if self.word_counter + 1 > len(self.found_word_indexes):
            self.word_counter = 1
        else:
            self.word_counter += 1
        if not self.found_word_indexes:
            return
        utils.clear_tags('found', self.editor_obj)
        self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_word_indexes)}")
        self.editor_obj.tag_add('found', self.found_word_indexes[self.word_counter - 1][0],
                                self.found_word_indexes[self.word_counter - 1][1])
        self.editor_obj.see(self.found_word_indexes[self.word_counter - 1][0])

    def previous_instance(self):
        if self.word_counter == 1:
            self.word_counter = len(self.found_word_indexes)
        else:
            self.word_counter -= 1
        if not self.found_word_indexes:
            return
        else:
            utils.clear_tags('found', self.editor_obj)

            self.word_count_label.configure(text=f"{self.word_counter}/{len(self.found_word_indexes)}")
            self.editor_obj.tag_add('found', self.found_word_indexes[self.word_counter - 1][0],
                                    self.found_word_indexes[self.word_counter - 1][1])
            self.editor_obj.see(self.found_word_indexes[self.word_counter - 1][0])
