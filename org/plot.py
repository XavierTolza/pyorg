from os import makedirs
from os.path import dirname, abspath, isdir

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.legend import _get_legend_handles_labels
from matplotlib.transforms import Bbox


class Axis(object):
    def __init__(self, ax):
        self.ax = ax

    def __getattribute__(self, item):
        ax = object.__getattribute__(self, "ax")
        if hasattr(ax, item):
            return getattr(ax, item)
        return super(Axis, self).__getattribute__(item)

    def set_info(self, title=None, xlabel=None, ylabel=None):
        for k, v in zip("title,xlabel,ylabel".split(","), [title, xlabel, ylabel]):
            if v is not None:
                getattr(self, f"set_{k}")(v)

    def saveaxe(self, filename, pad=0):
        ax = object.__getattribute__(self, "ax")
        fig = ax.figure

        ax.figure.canvas.draw()
        items = ax.get_xticklabels() + ax.get_yticklabels()
        items += [ax, ax.title]
        bbox = Bbox.union([item.get_window_extent() for item in items])

        extent = bbox.expanded(*(np.array([1, 1]) + pad))
        extent = extent.transformed(fig.dpi_scale_trans.inverted())
        # extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(filename, bbox_inches=extent)


class Subplots(object):
    def __init__(self, filename, *args, tight_layout=True, grid=None, legend=False, **kwargs):
        self.legend = legend
        self.filename = filename
        dir = dirname(abspath(filename))
        if not isdir(dir):
            makedirs(dir)
        if grid is None:
            grid = dict(alpha=.2)
        self.grid = grid
        self.tight_layout = tight_layout
        self.args = args
        self.kwargs = kwargs
        self.fig = None
        self.axes = None

    def __enter__(self):
        fig, axes = plt.subplots(*self.args, **self.kwargs)
        ndim = np.ndim(axes)
        shape = np.shape(axes)
        axes = [Axis(i) for i in np.ravel([axes])]
        if ndim > 0:
            axes = np.reshape(axes, shape)
        else:
            axes = axes[0]

        self.fig, self.axes = fig, axes
        return fig, axes

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tight_layout:
            plt.tight_layout()

        grid = self.grid
        for ax in np.ravel([self.axes]):
            if grid is not None and grid:
                ax.grid(**grid)
            if self.legend:
                ax.legend()

        self.fig.savefig(self.filename)
        print(self.filename)
        plt.close(self.fig)


def printcf(filename):
    """
    Saves current figure to a file and print it
    """
    plt.gcf().savefig(filename)
    print(filename)
