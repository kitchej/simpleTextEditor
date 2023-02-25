import tkinter as tk


def get_word_indexes(word, text_widget, match_word=False, start=1.0):
    """
    A helper function that finds the start and end indexes of every instance of a word within a text widget
    """
    out = []
    end_of_text = text_widget.index(tk.END)
    while start != text_widget.index(tk.END):
        word_start = text_widget.search(word, start, stopindex=tk.END)
        if word_start == '':
            break
        index = word_start.split(".")
        column = index[0]
        row = index[1]
        new_row = int(row) + len(word)
        if match_word:
            pass
        else:
            word_end = f"{column}.{new_row}"
        start = word_end
        out.append((word_start, word_end))
    return out


def clear_tags(tag, text_widget):
    """
    A helper function that clears a specified tag from within a text widget
    """
    old_tags = []
    ranges = text_widget.tag_ranges(tag)
    for i in range(0, len(ranges), 2):
        start = ranges[i]
        stop = ranges[i + 1]
        old_tags.append((tag, str(start), str(stop)))
    for old_tag in old_tags:
        text_widget.tag_remove(old_tag[0], old_tag[1], old_tag[2])
