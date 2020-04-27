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

    @classmethod
    def from_org(cls, table, header=None, first_column_as_index=True, **kwargs):
        table = [i for i in table if i is not None]

        if header is None:
            header = table[0]
            table = table[1:]
        else:
            if type(header) == str:
                header = header.split(",")
        res = dict(zip(header, zip(*table)))
        res = cls(res, **kwargs)
        if first_column_as_index:
            res = res.set_index(header[0])
        return res

    def describe(self, *args, **kwargs):
        res = DataFrame(super(DataFrame, self).describe(*args, **kwargs))
        res.loc["std/mean"] = res.loc["std"] / res.loc["mean"]
        return res


def read_csv(filename, *args, **kwargs):
    if not isfile(filename):
        filename = io.StringIO(filename)
    return DataFrame(pd.read_csv(filename, *args, **kwargs))


def to_org(df, formatter=dict(f="%.3f", i="%i", u="%i")):
    N = len(df)
    values = df.values.reshape(N, -1)
    index = df.index.values
    iname = df.index.name
    if iname is None:
        iname = "Index"

    try:
        cols = df.columns.values.tolist()
        dtypes = np.concatenate([[df.index.dtype], df.dtypes.values])
    except AttributeError:  # Its a Series and not a DF
        cols = [df.name]
        dtypes = np.array([df.index.dtype, df.dtype])

    res = [[iname] + cols, None] + np.concatenate([np.reshape(index, (N, 1)), values], axis=1).tolist()

    # Format values for display
    for i in np.arange(N) + 2:
        for j, dtype in zip(np.arange(len(res[i])), dtypes):
            if dtype.kind in formatter:
                res[i][j] = formatter[dtype.kind] % res[i][j]
    return res


if __name__ == '__main__':
    df = DataFrame(dict(A=[0, 1, 2], B=[1.1, 2.2, 3.3]))
    to_org(df)
