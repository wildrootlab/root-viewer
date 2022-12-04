import napari
from PyQt5 import QtCore
from gui.widgets.analysis import AnalysisWidget
from analysis.segmentation import widget_wrapper
class Viewer(AnalysisWidget):
    def __init__(self):
        super().__init__()
        """Show the napari viewer in the main window"""
        # ffs do not touch (╯°□°)╯︵ ┻━┻ 
        self.viewer = napari.Viewer(show=False)
        self._qt_viewer = self.viewer.window._qt_viewer

        self.viewer.window.main_menu.hide()
        self.viewer.window._status_bar.hide()

        self.qt_viewer = self.viewer.window._qt_window
        
        # workaround for https://github.com/pyapp-kit/magicgui/issues/306
        self.init_tabs()

    def init_tabs(self):
        """Initialize the tabs for the analysis widget"""
        self.segmentation_tab = self.viewer.window.add_dock_widget(widget_wrapper(), area='right', name='Auto-segmentation')
        self.filtering_tab = self.viewer.window.add_dock_widget(self.filtering_widget.layout, name='Filtering')
        self.thresholding_tab = self.viewer.window.add_dock_widget(self.thresholding_widget.layout, name='Thresholding')
        self.labeling_tab = self.viewer.window.add_dock_widget(self.labeling_widget.layout, name='Labeling')
        self.misc_tab = self.viewer.window.add_dock_widget(self.misc_widget.layout, name='Misc')
        
        self.viewer.window._qt_window.tabifyDockWidget(self.filtering_tab, self.thresholding_tab) 
        self.viewer.window._qt_window.tabifyDockWidget(self.filtering_tab, self.labeling_tab) 
        self.viewer.window._qt_window.tabifyDockWidget(self.filtering_tab, self.misc_tab)
        self.viewer.window._qt_window.tabifyDockWidget(self.filtering_tab, self.segmentation_tab)

    def init_analysis_widget(self, widget):
        """Add a widget to the napari viewer"""
        self.viewer.window.add_dock_widget(widget, area='right')
    
    def set_analysis_widget(self):
        """Set the values for the analysis widget"""
        self._set_filtering(self)
        