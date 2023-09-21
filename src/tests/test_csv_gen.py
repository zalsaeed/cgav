import unittest

from src.csv_gen import CSVGen


class TestCSVGen(unittest.TestCase):

    def test_all_have_same_len_on_new_keys(self):
        csv_gen = CSVGen()
        csv_gen.add_datapoint({"a": 1, "b": 1})
        csv_gen.add_datapoint({"a": 2, "b": 2})
        csv_gen.add_datapoint({"a": 3, "c": 1})

        for key, value in csv_gen.dataset.items():
            self.assertEqual(len(value), 3, f"key: {key} has {value}")

    def test_all_have_same_len_on_new_keys_explicit(self):
        csv_gen = CSVGen()
        csv_gen.add_datapoint({"a": 1, "b": 1})
        csv_gen.add_datapoint({"a": 2, "b": 2})
        csv_gen.add_datapoint({"a": 3, "c": 1})

        self.assertEqual(csv_gen.dataset["a"], [1, 2, 3])
        self.assertEqual(csv_gen.dataset["b"], [1, 2, None])
        self.assertEqual(csv_gen.dataset["c"], [None, None, 1])

    def test_all_have_same_len_on_missing_keys(self):
        csv_gen = CSVGen()
        csv_gen.add_datapoint({"a": 1, "b": 1})
        csv_gen.add_datapoint({"a": 2, "b": 2})
        csv_gen.add_datapoint({"a": 3})

        for key, value in csv_gen.dataset.items():
            self.assertEqual(len(value), 3, f"key: {key} has {value}")
