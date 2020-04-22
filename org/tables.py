import io
from os.path import isfile
import pandas as pd
import numpy as np


class Series(pd.Series):
    @property
    def _constructor(self):
        return Series

    @property
    def _constructor_expanddim(self):
        return DataFrame

    def to_org(self):
        val = np.array([self.index.values, self.values]).T.tolist()
        index = self.index.name
        if index is None:
            index = "Index"
        title = [index, "Values"]
        res = [title, None] + val
        return res


class DataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return DataFrame

    @property
    def _constructor_sliced(self):
        return Series

    def to_org(self):
        col = self.columns.tolist()
        val = self.values.tolist()
        return [col, None] + val

    def describe(self, *args, **kwargs):
        res = DataFrame(super(DataFrame, self).describe(*args, **kwargs))
        res.loc["std/mean"] = res.loc["std"]/res.loc["mean"]
        return res


def read_csv(filename, *args, **kwargs):
    if not isfile(filename):
        filename = io.StringIO(filename)
    return DataFrame(pd.read_csv(filename, *args, **kwargs))


def to_org(df):
    N = len(df)
    values = df.values.reshape(N, -1)
    index = df.index.values
    iname = df.index.name
    if iname is None:
        iname = "Index"

    try:
        cols = df.columns.values.tolist()
    except AttributeError:
        cols = [df.name]

    res = [[iname] + cols, None] + np.concatenate([np.reshape(index, (N, 1)), values], axis=1).tolist()

    return res
