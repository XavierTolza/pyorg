import re
import traceback
from hashlib import md5
from os import mkdir
from os.path import isdir, join, isfile, abspath

import numpy as np

from pyorg.config import cache_folder


class Cache(object):
    extension = None

    def __init__(self, folder=None, name=None):
        if folder is None:
            folder = cache_folder
        self.folder = abspath(folder)
        self.saved = False
        self.hash = name

        if not isdir(self.folder):
            mkdir(self.folder)

    def _get_hash(self):
        stack = traceback.extract_stack()
        f, last_line = self._get_origin_info(stack)
        with open(f) as fin:
            lines = list(fin)[last_line - 1:]
        lines = [i for i in lines if re.match("( |\t)+[^# ].+\n?", i)]
        padding = re.match("(( |\t)+)", lines[0]).groups()[0]
        stop_context = [re.match(f"{padding}", i) is None for i in lines]
        if np.any(stop_context):
            stop_line = np.where(stop_context)[0][0]
            lines = lines[:stop_line]
        lines = "".join(lines)
        hash = md5(bytes(lines, encoding="utf-8")).digest().hex()
        return hash

    def __enter__(self):
        if self.hash is None:
            self.hash = self._get_hash()
        val = None if not self.exist() else self.load()
        return self, val

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def filename(self):
        fn = self.hash
        extension = self.extension
        if extension is not None:
            fn = f"{fn}.{extension}"
        return join(self.folder, fn)

    def exist(self):
        return isfile(self.filename)

    def open(self, mode="w"):
        return open(self.filename, mode)

    def save(self, value):
        raise NotImplementedError("Save method is not implemented for this cache")

    def load(self):
        raise NotImplementedError('Load method is not implemented for this cache')

    def __call__(self, *args, **kwargs):
        self.save(*args, **kwargs)

    def _get_origin_info(self, stack):
        origin = None
        for i, x in enumerate(stack[::-1]):
            if x[2] == '__enter__':
                origin = stack[::-1][i + 1]
                break

        return origin[0], origin[1] + 1


try:
    import dill


    class DillCache(Cache):
        def load(self):
            with self.open("rb") as fp:
                dill.load(fp)

        def save(self, value):
            with self.open("wb") as fp:
                return dill.dump(value, fp)
except ImportError:
    pass


class NumpyCache(Cache):
    extension = "npy"

    def save(self, value):
        assert issubclass(type(value), np.ndarray)
        np.save(self.filename, value)

    def load(self):
        return np.load(self.filename)


try:
    import json


    class JsonCache(Cache):
        extension = "json"

        def save(self, value):
            with self.open("w") as fp:
                json.dump(value, fp)

        def load(self):
            with self.open("r") as fp:
                return json.load(fp)
except ImportError:
    pass
