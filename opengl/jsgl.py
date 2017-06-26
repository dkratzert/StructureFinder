#!python3
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtQml import QJSEngine
from PyQt5.QtWebEngine import QtWebEngine
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow

"""
http://3dmol.csb.pitt.edu/


HTML5
-----

JSmol.min.js   required if no other jQuery
or
JSmol.min.nojq.js  required if you provide jQuery

j2s/     required (JavaScript files)
idioma/  recommended (adds language localization)

<script type="text/javascript" src="js/JSmol.js"></script>
"""

class JSGl(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #myEngine = QJSEngine()
        #three = myEngine.evaluate("1 + 2")
        #print(three.toNumber())
        view = QWebEngineView()
        QtWebEngine.initialize()
        view.load(QUrl("http://gleborgne.github.io/molvwr/#cyanocobalamin"))
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


