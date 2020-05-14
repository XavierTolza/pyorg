from os import makedirs, mkdir
from os.path import dirname, abspath, isdir, join

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.legend import _get_legend_handles_labels
from matplotlib.transforms import Bbox

from pyorg import config
from pyorg.config import plots_folder, enable_figure_filename_check


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
    already_plotted = []

    def __init__(self, filename, *args, tight_layout=True, grid=None, legend=False, export_svg=False,
                 print_line_return=None, **kwargs):
        self.print_line_return = print_line_return if print_line_return is not None else config.print_line_return
        self.export_svg = export_svg
        self.legend = legend
        self.filename = join(plots_folder, filename)
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

    @property
    def folder(self):
        return dirname(self.filename)

    def handle_error(self, exc_type, exc_val, exc_tb):
        import traceback
        fig, ax = plt.subplots(1, 1)
        text = traceback.format_exc()
        ax.text(0, 0, text)
        fig.savefig(self.filename)

    def __exit__(self, exc_type, exc_val, exc_tb):
        res = None
        if exc_val is not None:
            # An error occured, we will display it inside the image
            self.handle_error(exc_type, exc_val, exc_tb)
            res = True
        else:

            if self.tight_layout:
                plt.tight_layout()

            grid = self.grid
            for ax in np.ravel([self.axes]):
                if grid is not None and grid:
                    ax.grid(**grid)
                if self.legend:
                    ax.legend()

            if not isdir(self.folder):
                mkdir(self.folder)

            filename = self.filename
            if enable_figure_filename_check:
                if filename in self.already_plotted:
                    raise ValueError(f"You're trying to plot {filename} but a figure with this name has "
                                     f"already been plotted")
                self.already_plotted.append(filename)

            self.fig.savefig(filename)
            if self.export_svg:
                self.fig.savefig(".".join(filename.split(".")[:-1]) + ".svg")
        print(self.filename, end="\n" if self.print_line_return else "")
        plt.close("all")
        return res


def printcf(filename):
    """
    Saves current figure to a file and print it
    """
    filename = join(plots_folder, filename)
    plt.gcf().savefig(filename)
    print(filename)


def colormap(pos, colormap="Viridis"):
    if type(pos) == int:
        pos = np.linspace(0, 1, pos)
    return cm.get_cmap(colormap)(pos)
