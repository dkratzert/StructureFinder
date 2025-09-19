import sys

import numpy as np
import pyqtgraph as pg
from qtpy import QtCore
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout

from structurefinder.searcher.database_handler import is_numeric


class PlotWidget(QWidget):
    point_clicked = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.scatter = None

    def plot_points(self, results: list[tuple[int | float, int | float, int]], x_title: str = '', y_title: str = ''):
        self.plot_widget.clear()
        results = [t for t in results if all(is_numeric(v) for v in t)]
        spots = []
        for num, xi, yi in results:
            spots.append({'pos'   : (xi, yi),
                          'data'  : num,
                          'symbol': 'o',
                          'size'  : 8,
                          # 'brush' : pg.mkBrush(0, 0, 255, 150)
                          })
        self.scatter = pg.ScatterPlotItem(spots=spots, hoverable=True)
        self.scatter.sigClicked.connect(self._on_point_clicked)
        self.plot_widget.addItem(self.scatter)
        self.plot_widget.setLabel('bottom', x_title)
        self.plot_widget.setLabel('left', y_title)

    def _on_point_clicked(self, scatter, points):
        for p in points:
            row_index = p.data()
            self.point_clicked.emit(row_index)

    def plot_histogram(self, data, bins=10, x_title: str = '', y_title: str = ''):
        self.plot_widget.clear()
        self.scatter = None
        hist, bin_edges = np.histogram([(x, y) for x, y, _ in data], bins=bins)
        # Center the bars on the bin
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        bar_graph = pg.BarGraphItem(x=bin_centers, height=hist, width=(bin_edges[1] - bin_edges[0]), brush='b')
        self.plot_widget.addItem(bar_graph)
        self.plot_widget.setLabel('bottom', x_title)
        self.plot_widget.setLabel('left', y_title)

    def plot_histogram_text(self, data: list[tuple[str, int, int]], x_title: str = '', y_title: str = ''):
        """
        data: list of (category_name, value)
        """
        self.plot_widget.clear()
        self.scatter = None

        data = [t for t in data if is_numeric(t[2])]
        data = [t for t in data if t[1]]

        # Separate labels and values
        try:
            _, labels, values = zip(*data)
        except ValueError as e:
            print(f'Error during histogram plot {e}.    ')
            return

        # Map each category to an integer position
        x_positions = np.arange(len(labels))

        try:
            bar_graph = pg.BarGraphItem(x=x_positions, height=values, width=0.6, brush='b')
            self.plot_widget.addItem(bar_graph)
        except TypeError as e:
            print(f'Error during histogram plot {e}')
            return

        self.plot_widget.setLabel('bottom', x_title)
        self.plot_widget.setLabel('left', y_title)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PlotWidget()
    w.plot_points([(1, 0.2, 1), (2, 0.3, 2), (3, 0.8, 3), (0.99, 0.99, 4)], 'x_axe', 'y-axe')
    w.show()
    sys.exit(app.exec())
