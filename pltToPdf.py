from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import cv2
import numpy as np
from typing import override, TypedDict, Unpack

def kwargsPopAndReturnIfExists(key: str, default: any, kwargs) -> any:
    if key not in kwargs:
        return default
    val = kwargs.get(key)
    kwargs.pop(key)
    return val

class FigureKwargs(TypedDict, total=False):
    showAsNewWindow: bool = False
    showXTicks: bool = False
    showYTicks: bool = False
    xTicks: list[any] = None
    yTicks: list[any] = None
    yLim: float | tuple[float, float] = None

class PdfFigure:
    showXTicks = False
    showYTicks = False
    def __init__(self, title: str = "", **kwargs: Unpack[FigureKwargs]):
        """
        :key showAsNewWindow: show as new window instead printing to pdf (default False)
        :key showXTicks: show x ticks (default PdfFigure.showXTicks)
        :key showYTicks: show y ticks (default PdfFigure.showYTicks)
        :key xTicks: which x ticks should be displayed instead of defult ones (showXTicks must be True)
        :key yTicks: which y ticks should be displayed instead of defult ones (showYTicks must be True)
        :key yLim: plt.ylim argument
        """
        self.title = title
        self.showAsNewWindow = kwargsPopAndReturnIfExists("showAsNewWindow", False, kwargs)
        self.showXTicks = kwargsPopAndReturnIfExists("showXTicks", PdfFigure.showXTicks, kwargs)
        self.showYTicks = kwargsPopAndReturnIfExists("showYTicks", PdfFigure.showYTicks, kwargs)
        self.xTicks = kwargsPopAndReturnIfExists("xTicks", None, kwargs)
        self.yTicks = kwargsPopAndReturnIfExists("yTicks", None, kwargs)
        self.yLim = kwargsPopAndReturnIfExists("yLim", None, kwargs)
        self.kwargs = kwargs


    def print(self):
        pass

    def configTicks(self):
        if not self.showXTicks:
            plt.xticks([])
        elif self.xTicks is not None:
            plt.xticks(self.xTicks)
        if not self.showYTicks:
            plt.yticks([])
        elif self.yTicks is not None:
            plt.yticks(self.yTicks)
        elif self.yLim is not None:
            plt.ylim(self.yLim)

class PdfImageFigure(PdfFigure):
    def __init__(self, image: cv2.typing.MatLike, title: str = "", **kwargs: Unpack[FigureKwargs]):
        super().__init__(title, **kwargs)
        self.image = np.copy(image)

    @override
    def print(self):
        self.configTicks()
        plt.imshow(self.image, **self.kwargs)
        if self.title != "":
            plt.title(self.title)

class BarFigureKwargs(TypedDict, FigureKwargs, total=False):
    width: float

class PdfBarFigure(PdfFigure):
    def __init__(self, bars: list[int], title: str = "", **kwargs: Unpack[BarFigureKwargs]):
        """
        :key width: width of a bar (default 0.8)
        """
        super().__init__(title, **kwargs)
        self.bars = bars
        self.width = kwargsPopAndReturnIfExists("width", 0.8, kwargs)

    @override
    def print(self):
        plt.bar(range(len(self.bars)), self.bars, self.width)
        self.configTicks()
        if self.title != "":
            plt.title(self.title)

class PlotKwargs(TypedDict, total=False):
    fmt: str
    xVals: list[any]

class PdfPlot():
    """
    This must be then passed in `plots` to `PdfPlotFigure` to be drawn.
    """
    def __init__(self, data: np.ndarray, **kwargs: Unpack[PlotKwargs]):
        """
        :key fmt: line format
        :key xVals: x values of data
        """
        self.data = data
        self.fmt = kwargsPopAndReturnIfExists("fmt", "", kwargs)
        self.x = kwargsPopAndReturnIfExists("xVals", np.empty(0), kwargs)
        if self.x.size != self.data.size:
            self.x = np.arange(data.size)
        self.kwargs = kwargs

class ScatterKwargs(TypedDict, total=False):
    xVals: list[any]

class PdfScatter():
    """
    When passed to `PdfPlotFigure` in `plots`, this is drawn using `plt.scatter()`
    """
    def __init__(self, data: np.ndarray, **kwargs: Unpack[ScatterKwargs]):
        """
        :key Vals: x values of data
        """
        self.data = data
        self.x = kwargsPopAndReturnIfExists("xVals", np.empty(0), kwargs)
        if self.x.size != self.data.size:
            self.x = np.arange(data.size)
        self.kwargs = kwargs

class PdfPlotFigure(PdfFigure):
    def __init__(self, plots: list[PdfPlot], title = "", **kwargs: Unpack[FigureKwargs]):
        """
        :param plots: list of `PdfPlot`s, which are drawn on the plot
        """
        super().__init__(title, **kwargs)
        self.plots = plots

    @override
    def print(self):
        self.configTicks()
        label = False
        for p in self.plots:
            if isinstance(p, PdfPlot):
                plt.plot(p.x, p.data, p.fmt, **p.kwargs)
            elif isinstance(p, PdfScatter):
                plt.scatter(p.x, p.data, **p.kwargs)
            if "label" in p.kwargs:
                label = True
        if label:
            plt.legend()


class SubplotFigureKwargs(TypedDict, FigureKwargs, total=False):
    width: float
    height: float

class PdfSubplotFigure(PdfFigure):
    def __init__(self, subfigures: list[PdfFigure], title: str = "", **kwargs: Unpack[SubplotFigureKwargs]):
        """
        :param subfigures: list of `PdfFigure`s, which are drawn on the subplot
        :key width: width of subplot. If width * height < len(subfigures), height = 1, width = len(subfigures)
        :key height: height of subplot. If width * height < len(subfigures), height = 1, width = len(subfigures)
        """
        super().__init__(title, **kwargs)
        self.subfigures = subfigures
        self.width = kwargsPopAndReturnIfExists("width", len(subfigures), kwargs)
        self.height = kwargsPopAndReturnIfExists("height", 1, kwargs)

        if self.width * self.height < len(subfigures):
            self.width = len(subfigures)
            self.height = 1

    @override
    def print(self):
        for i in range(len(self.subfigures)):
            plt.subplot(self.height, self.width, i + 1)
            self.subfigures[i].print()
        if self.title != "":
            plt.suptitle(self.title)


def printFigures(pages: list[PdfFigure], doc: str = "output.pdf"):
    with PdfPages(doc) as pdf:
        for page in pages:
            # Page is landscape A4 format
            plt.figure(figsize=(29.7, 21, "cm"))
            page.print()
            if page.showAsNewWindow:
                plt.show()
            else:
                pdf.savefig()  # saves the current figure into a pdf page
            
            plt.close()


# Usage: put all the different `PdfFigure`s into a list, then call `printFigures`
# with the list as an argument at the end.