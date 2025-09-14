import sys

from qtpy import QtWidgets

"""
Ideas:

* Two comboboxes for x and y values each
* One x or y may be the db index number
* Allow point, histogram or pie plot
* Options to remove empty values or set them to zero
* Histogram has counts as x axis
* Each change in the gui replots the data
* Allow mouse wheel zoom and drag of plot.

Nice to have:
* Show information about data point on mouse hover
* 3D plot of three values
"""
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout

import pyqtgraph as pg


class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.scatter = None

    def plot_points(self, results: list[tuple[int|float, int|float, int]], x_title: str = '', y_title: str = ''):
        self.plot_widget.clear()
        spots = []
        for id, xi, yi in results:
            spots.append({'pos': (xi, yi),
                          'data': id,
                          'symbol': 'o',
                          'size': 10,
                          'brush': pg.mkBrush(0, 0, 255, 150)})
        self.scatter = pg.ScatterPlotItem(spots=spots, hoverable=True)
        self.plot_widget.addItem(self.scatter)
        self.plot_widget.setLabel('bottom', x_title)
        self.plot_widget.setLabel('left', y_title)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PlotWidget()
    w.plot_points2([(1, 0.2, 1), (2, 0.3, 2), (3, 0.8, 3), (0.99, 0.99, 4)], 'x_axe', 'y-axe')
    w.show()
    sys.exit(app.exec())
