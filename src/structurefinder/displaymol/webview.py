from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import sys


class WebViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()


    def init_ui(self):
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full-size display

        # Create QWebEngineView instance
        self.web_view = QWebEngineView()

        # Enable JavaScript
        self.web_view.settings().setAttribute(
            self.web_view.settings().JavascriptEnabled, True)

        # Add web view to layout
        layout.addWidget(self.web_view)

        # Example HTML with Miew molecular viewer
        html_content = """
                       <!DOCTYPE html>
                       <html>
                       <head>
                           <meta charset="UTF-8"/>
                           <script src="https://unpkg.com/lodash@^4.17.21/lodash.js"></script>
                           <script src="https://unpkg.com/three@0.153.0/build/three.min.js"></script>
                           <script src="https://unpkg.com/miew@0.11.0/dist/Miew.min.js"></script>
                           <link rel="stylesheet" href="https://unpkg.com/miew@0.11.0/dist/Miew.min.css"/>
                           <style>
                               body, html {
                                   margin: 0;
                                   padding: 0;
                                   width: 100%;
                                   height: 100%;
                                   overflow: hidden;
                               }
                               .miew-container {
                                   width: 100%;
                                   height: 100%;
                                   position: absolute;
                                   top: 0;
                                   left: 0;
                               }
                           </style>
                       </head>
                       <body>
                       Hello
                       <div class="miew-container"></div>
                       <script>
                           var viewer;
                           (function () {
                               viewer = new Miew({
                                    load: '1CRN',
                                    container: document.querySelector('.miew-container'),
                                    settings: {
                                        fps: false  // This hides the frames counter
                                    }
                                });
                               if (viewer.init()) {
                                   viewer.run();
                               }
                           })();

                       </script>
                       </body>
                       </html>
                       """

        # Load the HTML content
        self.set_html(html_content)

    def set_html(self, html_content):
        """Set the HTML content of the web view"""
        self.web_view.setHtml(html_content)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Create and set the central widget
        self.web_viewer = WebViewer()
        self.setCentralWidget(self.web_viewer)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())