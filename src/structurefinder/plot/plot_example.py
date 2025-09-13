import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyQt6 Plot with 10 Points")
        layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)

    def plot_points(self, x: list[float], y: list[float], x_title: str = '', y_title: str = ''):
        self.ax.clear()
        self.ax.plot(x, y, "o")
        self.ax.set_title("Residual plot")
        self.ax.set_xlabel(x_title)
        self.ax.set_ylabel(y_title)
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PlotWidget()
    w.show()
    sys.exit(app.exec())