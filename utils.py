import tkinter as tk


def get_word_indexes(word, text_widget, match_word=0, match_case=0, start=1.0):
    """
    A helper function that finds the start and end indexes of every instance of a word within a text widget
    """
    # we need to reverse the match_word boolean because tk.Text.search() expects a 1 to activate a no-case search
    if match_case == 1:
        match_case = 0
    else:
        match_case = 1
    punctuation = [' ', ',', '.', '!', '?', ':', ';', '"', '\'', '\\', '/', '<', '>', '`', '~', '@', '#', '$', '%',
                   '&', '*', '(', ')', '{', '}', '[', ']', '+', '=', '-', '|', '~', '`']
    out = []

    # tkinter puts a new line at the end of text in a textbox, so we will need to account for that
    text_end_column = int(text_widget.index("end - 1c").split('.')[1])

    while start != text_widget.index(tk.END):
        word_start = text_widget.search(word, start, stopindex=tk.END, nocase=match_case)
        if word_start == '':
            break
        word_start_index = word_start.split(".")
        start_row = int(word_start_index[0])
        start_column = int(word_start_index[1])
        end_column = start_column + len(word)
        word_end = f"{start_row}.{end_column}"
        start = word_end

        if match_word == 1:
            if word_start == '1.0':
                # Just check the right side of the word
                characters = text_widget.get(word_start, f"{start_row}.{end_column + 1}")
                if characters[-1] in punctuation:
                    out.append((word_start, word_end))
            elif end_column == text_end_column:
                # Just check the left side of the word
                characters = text_widget.get(f"{start_row}.{start_column - 1}", word_end)
                if characters[0] in punctuation:
                    out.append((word_start, word_end))
            elif word_start_index == '1.0' and end_column == text_end_column:
                # Check neither side of the word
                out.append((word_start, word_end))
            else:
                # Check both sides of the word
                characters = text_widget.get(f"{start_row}.{start_column - 1}", f"{start_row}.{end_column + 1}")
                if characters[0] in punctuation and characters[-1] in punctuation:
                    out.append((word_start, word_end))
        else:
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
