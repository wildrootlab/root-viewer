import os, sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow,  QGridLayout, QWidget, QAction, QDockWidget
from PyQt5.QtCore import QSettings, Qt
import ctypes
from gui.napari_viewer import Viewer
from gui.config import Settings
DEBUG = os.getenv('DEBUG')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# set the application user mode id for windows
myappid = 'Root-Viewer'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow, Viewer, Settings):
    def __init__(self):
        super().__init__()
        self._main = QWidget()
        self.debug=DEBUG
        print(self.debug)
        self.settings = QSettings('Root-Viewer')
        self.get_settings()
        self.setWindowTitle("2P Analysis")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", "logo_light.png")))
        self.setCentralWidget(self._main)

        # create a grid box layout widget
        self.layout = QGridLayout(self._main)

        # add an empty menuBar
        self.menu = self.menuBar()

        # add a napari viewer
        self.layout.addWidget(self.qt_viewer, 0, 0)
        self.create_analysis_widget()

        # populate the menuBar
        self.create_menue_bar()
        
        # initialize settings
        self.conf_settings = Settings()

        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

    def create_analysis_widget(self):
        """Creates the analysis widgets and adds them to the main window."""  
        # This is a temporary method to add the analysis widget to the main window
        # TODO: create private class for the analysis widget
        
        segmentation = self.segmentation_tab
        segmentation._close_btn = False
        segmentation._hide_btn = False
        segmentation._float_btn = False

        self.addDockWidget(Qt.RightDockWidgetArea, segmentation)
        
        stardist = self.stardist_tab
        stardist._close_btn = False
        stardist._hide_btn = False
        stardist._float_btn = False
        self.tabifyDockWidget(segmentation, stardist)
    
    def closeEvent(self, event):
        try:
            self.set_settings() # set the settings
        except: 
            pass
    
    def get_settings(self):
        """Load Settings"""
        try:
            self.resize(self.settings.value("window_size"))
            self.move(self.settings.value("window_pos"))
        except:
            pass
    
    def set_settings(self):
        self.settings.setValue("window_size", self.size())
        self.settings.setValue("window_pos", self.pos())
    
    def create_menue_bar(self):
        for action in self.viewer.window.file_menu.actions():
            data = action.data()
            try:
                name = data.get('text')
                if name in ['Save Screenshot...', 'Save Screenshot with Viewer...','Copy Screenshot to Clipboard','Copy Screenshot with Viewer to Clipboard', 'Close Window']:
                    self.viewer.window.file_menu.removeAction(action)
            except: pass
        for action in self.viewer.window.view_menu.actions():
            data = action.data()
            try:
                name = data.get('text')
                if name in ['Toggle Full Screen', 'Toggle Menubar Visibility']:
                    self.viewer.window.view_menu.removeAction(action)
            except: pass

        file_menu = self.menu.addMenu(self.viewer.window.file_menu)
        edit_menu = self.menu.addMenu(self.viewer.window.view_menu)
        window_menu = self.menu.addMenu(self.viewer.window.window_menu)
