import os
import errno
import base64
import hashlib

import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display


def small_hash(unique_string: str) -> str:
    """
    A method that takes a string and returns a 10-elements hash code. 
    The code is an url-safe. The shorter the hash the more likely there
    will be a hash-collision. Therefore, chose your unique string
    wisely!
    For more information see https://stackoverflow.com/a/2599654/3504748

    :param unique_string: A unique string that defines some object.
    :return: a URL-safe 10 char length hash string.
    """
    return base64.urlsafe_b64encode(hashlib.md5(unique_string.encode('utf-8')).digest())[:10].decode("utf-8")


def fix_arabic(original_string: str) -> str:
    """
    Arabic character will not print properly using fpdf if not reshaped in
    terms of characters encoding and right-to-left alignment.

    :param original_string: A string in Arabic.
    :return: The same string in Arabic after fixing it for prints.
    """
    # FIXME: The libraries arabic_reshaper and bidi don't handle Tashkel! As of now all text must NOT have any
    #  Tashlel characters
    return get_display(reshape(original_string))


def read_csv_to_dict(path: str) -> list:
    """
    Reads a CSV file (provided the path) and returns it as a list of dicts.
    Example CSV file:
    +------+-------+
    | name | email |
    +------+-------+
    | x    | x@x.x |
    | y    | y@y.y |
    +------+-------+

    Will be returned as: 
    [
        {"name": "x", "email": "x@x.x"},
        {"name": "y", "email": "y@y.y"},
    ]

    :param path: a relative path to the CSV file.
    :return: A list of dictionaries each with key as column header and value as row cell.
    """
    return pd.read_csv(path).to_dict(orient='records')


def make_sure_path_exists(path: str):
    """
    If a path does not exist, it creates it! Simple!

    :param path: a relative path to some directory.
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def break_string_into_chunks(original: str, max_char_size: int) -> list:
    """
    A method that takes a long string then break it into a max size unlimited number of chunks.

    :param original: a string; more likely a long one!
    :param max_char_size: The size of each chunk of the original string when broken.
    :return: A list of string each string with max size less than max_char_size.
    """
    lines = []
    while len(original) > max_char_size:
        original_list = original.split(" ")
        new_line = ""
        new_line_fill = 0
        while new_line_fill + len(original_list[0]) <= max_char_size:
            word = original_list.pop(0)
            new_line_fill += len(word)+1
            new_line += word+" "

        new_line = new_line[:-1]  # remove the last space added
        lines.append(new_line)  # add line to list of lines
        original = " ".join(original_list)  # reset the original str
        # TODO: what if there is still a word but the word itself is longer than the max_char_size

    # if we finish the while loop, but we still have a string of words
    # shorter than max_char_size, then add it to the list of lines.
    if original:
        lines.append(original)

    return lines


def make_file_name_compatible(file_name: str) -> str:
    """
    Remove all spaces from a string and make it all lowercase.
    """
    return file_name.lower().replace(" ", "-")


def get_gendered_full_name(first_name: str, middle_name: str, last_name: str, gender: str):
    if gender.lower() == "male":
        return f"{first_name} بن {middle_name} {last_name}"
    elif gender.lower() == "female":
        return f"{first_name} بنت {middle_name} {last_name}"
    else:
        raise RuntimeError(f"Gender '{gender}' unrecognized!")
