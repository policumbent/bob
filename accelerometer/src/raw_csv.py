import csv

axis = ['x', 'y', 'z']


class RawCsv:
    def __init__(self, filename: str):
        self._csv_file = None
        self._csv_writer: csv.DictWriter = None
        self.init(filename)

    def write(self, data: dict):
        self._csv_writer.writerow(data)

    def close(self):
        if self._csv_file is not None:
            self._csv_file.close()

    def init(self, filename: str):
        self._csv_file = open(f"data/{filename}.csv", 'w', newline='')
        self._csv_writer = csv.DictWriter(self._csv_file, fieldnames=axis)
        self._csv_writer.writeheader()

