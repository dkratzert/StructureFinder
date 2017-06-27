#!python3
import sys

from PyQt5.QtCore import QUrl, QFile, QIODevice
from PyQt5.QtQml import QJSEngine
from PyQt5.QtWebEngine import QtWebEngine
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow

"""
http://3dmol.csb.pitt.edu/


"""

class JSGl(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #myEngine = QJSEngine()
        #three = myEngine.evaluate("1 + 2")
        #print(three.toNumber())
        view = QWebEngineView()
        QtWebEngine.initialize()
        #view.load(QUrl("http://www.heise.de"))
        view.load(QUrl.fromLocalFile("/Users/daniel/GitHub/StructureDB/opengl/jmolview.html"))
        #f = QFile(QUrl("/Users/daniel/GitHub/StructureDB/opengl/jmolview.html").path())
        #f.open(QIODevice.ReadOnly | QIODevice.Text)
        #print(f.readAll())
        view.show()
        self.setCentralWidget(view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = JSGl()
    myapp.show()
    myapp.raise_()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        sys.exit()


