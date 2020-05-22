from unittest import TestCase

from pyorg.cache import *


class TestCache(TestCase):
    def test_json(self):
        with JsonCache() as (c, data):
            if data is None:
                data = dict(a=10, b=20)
                c(data)
        pass

    def test_numpy(self):
        with NumpyCache() as (c, data):
            if data is None:
                data = np.random.normal(0, 1, 100)
                c(data)
