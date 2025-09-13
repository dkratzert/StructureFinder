import sys

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog


class WebViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdb_file: str | None = None
        self.init_ui()
        self.web_view.loadFinished.connect(self.on_page_loaded)

    def on_page_loaded(self):
        pdb = self.load_pdb_file(self.pdb_file)
        self.on_load_finished(pdb)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(self.web_view.settings().JavascriptEnabled, True)
        # self.web_view.loadFinished.connect(self.on_load_finished)
        layout.addWidget(self.web_view)

        html_content = """
                       <!DOCTYPE html>
                       <html>
                       <head>
                           <meta charset="UTF-8"/>
                           <script src="https://unpkg.com/lodash@^4.17.21/lodash.js"></script>
                           <script src="https://unpkg.com/three@0.149.0/build/three.min.js"></script>
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
                       <div class="miew-container"></div>
                       <script>
                           var viewer = null;

                           function initViewer() {
                               viewer = new Miew({
                                   container: document.getElementsByClassName('miew-container')[0],
                                   reps: [{
                                       mode: 'BS',
                                       colorer: 'EL',
                                       material: 'DF',
                                   }],
                                   settings: {
                                       //bg: {color: 0xCCCCCC},
                                       //fogFarFactor: 2,
                                       fps: false,
                                       axes: true,
                                       resolution: 'high',
                                   },
                               });

                               if (viewer.init()) {
                                   viewer.run();
                               }
                           }

                           window.loadPDBContent = function(pdbContent) {
                               if (!viewer) {
                                   initViewer();
                               }
                               viewer.load(pdbContent, { 
                                   sourceType: 'immediate',
                                   fileType: 'pdb'
                               });
                           };

                           // Initialize viewer when page loads
                           window.onload = initViewer;

                           // Handle resize events
                           window.addEventListener('resize', function() {
                               if (viewer) {
                                   viewer.resize();
                               }
                           });
                       </script>
                       </body>
                       </html>
                       """

        self.set_html(html_content)

    def set_html(self, html_content):
        self.web_view.setHtml(html_content)

    def on_load_finished(self, pdb_content: str):
        if pdb_content:
            c = f"window.loadPDBContent('{pdb_content}');"
            self.web_view.page().runJavaScript(c)

    def load_pdb_file(self, file_path: str) -> str | None:
        try:
            with open(file_path, 'r') as f:
                pdb_content = f.read()
                pdb_content = pdb_content.replace('\\', '\\\\').replace('\n', '\\n').replace('\'', '\\\'')
                return pdb_content
        except Exception as e:
            print(f"Error loading PDB file: {str(e)}")
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Viewer")
        self.setGeometry(100, 100, 800, 600)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        load_button = QPushButton("Load PDB File")
        load_button.clicked.connect(self.open_pdb_file)
        main_layout.addWidget(load_button)
        self.web_viewer = WebViewer()
        main_layout.addWidget(self.web_viewer)
        self.setCentralWidget(main_widget)
        
        self.web_viewer.pdb_file = "/Users/daniel/Downloads/1crn.pdb"

    def open_pdb_file(self):
        print('open pdb file')
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDB File",
            "",
            "PDB Files (*.pdb);;All Files (*.*)"
        )
        if file_path:
            pdb = self.web_viewer.load_pdb_file(file_path)
            self.web_viewer.on_load_finished(pdb)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
