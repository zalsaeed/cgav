import os
from collections import defaultdict

import pandas as pd


class CSVGen:

    def __init__(self):
        self.dataset = defaultdict(list)

    def add_datapoint(self, a_row: dict):
        existing_keys = list(self.dataset.keys())

        for key, value in a_row.items():
            if key in existing_keys:
                existing_keys.remove(key)

                self.dataset[str(key)].append(value)
            else:
                # this could be a key we have never seen before
                # if that is the case, then we should fill all previous entries with none
                # or just add it as this is the first pass ever
                if existing_keys:
                    self.dataset[str(key)] = ([None] * len(self.dataset[existing_keys[0]])) + [value]
                else:
                    self.dataset[str(key)].append(value)

        # if we still have an item in the list that we didn't append, append none!
        # all columns must have the same number of items.
        if existing_keys:
            for key in existing_keys:
                self.dataset[str(key)].append(None)

    def write_to_csv(self, output_dir: str, file_name: str):
        """A method that takes a dictionary and uses  its keys as headers for a CSV file.

        :param output_dir: full directory to which the output file should be saved.
        :param file_name: The desired name for the generated file.
        """
        full_dir = f"{os.path.abspath(output_dir)}/{file_name}.csv"

        with open(full_dir, "w") as e_file:
            pd.DataFrame(self.dataset).to_csv(e_file, index=False)
