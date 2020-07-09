import numpy as np


def get_cdf(x):
    x = np.sort(x.ravel())
    x = x[~np.isnan(x)]
    y = np.linspace(0, 1, x.size)
    return x, y


def describe(x):
    return {k: getattr(np, k)(x) for k in "mean,std,median,min,max".split(",")}
