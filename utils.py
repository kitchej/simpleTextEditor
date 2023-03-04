import tkinter as tk


def get_first_string_index(string, text_widget, regex=False, no_case=False, start="1.0"):
    """
    A helper function that finds the start and end index of the FIRST instance of a string within a text widget
    """
    length = tk.IntVar()
    word_start = text_widget.search(string, start, regexp=regex, stopindex=tk.END, nocase=no_case, count=length)
    if word_start == '':
        return None
    word_start_index = word_start.split(".")
    start_row = int(word_start_index[0])
    start_column = int(word_start_index[1])
    end_row = start_row + string.count('\n')
    end_column = start_column + length.get()
    word_end = f"{end_row}.{end_column}"
    return word_start, word_end


def get_string_indexes(string, text_widget, regex=False, no_case=False, start="1.0"):
    """
    A helper function that finds the start and end indexes of ALL instances of a string within a text widget
    """
    length = tk.IntVar()
    out = []
    while start != text_widget.index(tk.END):
        word_start = text_widget.search(string, start, regexp=regex, stopindex=tk.END, nocase=no_case, count=length)
        if word_start == '':
            break
        word_start_index = word_start.split(".")
        start_row = int(word_start_index[0])
        start_column = int(word_start_index[1])
        end_row = start_row + string.count('\n')
        end_column = start_column + length.get()
        word_end = f"{end_row}.{end_column}"
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
