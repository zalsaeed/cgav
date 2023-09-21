import string
import random
import unittest

from src import util


def generate_sentences(num_words: int) -> str:
    words = []
    for _ in range(num_words):
        ''.join(random.choices(string.ascii_letters + " ", k=random.randint(2, 10)))
    return ' '.join(words)


class TestUtilHash(unittest.TestCase):

    def test_small_hash_diff(self):
        input1 = "Some String"
        input2 = "A different string"
        result1 = util.small_hash(input1)
        result2 = util.small_hash(input2)
        self.assertNotEqual(result1, result2)

    def test_small_hash_same(self):
        some_input = "A string"
        result1 = util.small_hash(some_input)
        result2 = util.small_hash(some_input)
        self.assertEqual(result1, result2)

    def test_small_hash_length(self):
        for i in range(20):
            some_string = ''.join(random.choices(string.ascii_uppercase + string.digits,
                                                 k=random.randint(20, 100)))
            result = util.small_hash(some_string)
            self.assertLessEqual(len(result), 10, f"The string '{some_string}', results in a hash longer "
                                                  f"than 10 character '{result}'")

    def test_for_hash_collision(self):
        a_lot_of_characters = string.ascii_letters + string.digits + string.punctuation + string.whitespace
        a_base_string = "short"
        all_generated_hashes = []
        for char in a_lot_of_characters:
            new_hash = util.small_hash(a_base_string + char)
            self.assertNotIn(new_hash, all_generated_hashes, f"The string '{a_base_string + char}' resulted in a "
                                                             f"hash '{new_hash}' we have seen before!")
            all_generated_hashes.append(new_hash)

    def test_small_hash_with_arabic_character(self):
        a1 = "حمد"
        a2 = "حسن"

        result1 = util.small_hash(a1)
        result2 = util.small_hash(a1)
        self.assertEqual(result1, result2)

        result3 = util.small_hash(a2)
        self.assertNotEqual(result1, result3)


class TestUtilStringBreaker(unittest.TestCase):

    def test_correct_length(self):
        some_string = generate_sentences(50)
        size = 12

        list_of_lines = util.break_string_into_chunks(some_string, size)
        for line in list_of_lines:
            self.assertLessEqual(len(line), size, f"The line '{line}' is still larger than {size}")
