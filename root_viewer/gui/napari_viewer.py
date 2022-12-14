import napari
from PyQt5 import QtCore
from gui.widgets.analysis import AnalysisWidget
from analysis.segmentation import widget_wrapper as segmentation_widget_wrapper
from analysis.stardist import plugin_dock_widget as stardist_plugin_dock_widget

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
        self.segmentation_tab = self.viewer.window.add_dock_widget(segmentation_widget_wrapper(), area='right', name='Basic Segmentation')
        self.stardist_tab = self.viewer.window.add_dock_widget(stardist_plugin_dock_widget(), area='right', name='Advanced Segmentation')
        #self.filtering_tab = self.viewer.window.add_dock_widget(self.filtering_widget.layout, name='Filtering')
        #self.thresholding_tab = self.viewer.window.add_dock_widget(self.thresholding_widget.layout, name='Thresholding')
        #self.labeling_tab = self.viewer.window.add_dock_widget(self.labeling_widget.layout, name='Labeling')
        #self.misc_tab = self.viewer.window.add_dock_widget(self.misc_widget.layout, name='Misc')
        


    def init_analysis_widget(self, widget):
        """Add a widget to the napari viewer"""
        self.viewer.window.add_dock_widget(widget, area='right')
    
    def set_analysis_widget(self):
        """Set the values for the analysis widget"""
        self._set_filtering(self)
        