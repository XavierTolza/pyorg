import io
from os.path import isfile
import pandas as pd


class DataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return DataFrame

    def to_org(self):
        col = self.columns.tolist()
        val = self.values.tolist()
        return [col, None] + val


def read_csv(filename, *args, **kwargs):
    if not isfile(filename):
        filename = io.StringIO(filename)
    return DataFrame(pd.read_csv(filename, *args, **kwargs))
