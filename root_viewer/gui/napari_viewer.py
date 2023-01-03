import root_viewer.backend as napari
from gui.widgets.analysis import AnalysisWidget


class Viewer(AnalysisWidget):
    def __init__(self):
        super().__init__()
        """Show the napari viewer in the main window"""
        # ffs do not touch (╯°□°)╯︵ ┻━┻
        self.viewer = napari.Viewer(show=False)

        self.viewer.window.main_menu.hide()
        self.viewer.window._status_bar.hide()

        self._qt_viewer = self.viewer.window._qt_viewer

        self.qt_viewer = self.viewer.window._qt_window

        # workaround for https://github.com/pyapp-kit/magicgui/issues/306
        self.init_widgets()

    def init_widgets(self):
        """Initialize widgets that reqire hookins to napari"""

        self.N_basic_seg = self.viewer.window.add_dock_widget(
            self.basic_segmentation_widget,
            name="Basic Segmentation",
            area="right",
            add_custom_title_bar=False,
        )

        self.N_adv_seg = self.viewer.window.add_dock_widget(
            self.advanced_segmentation_widget,
            name="Advanced Segmentation",
            area="right",
            add_custom_title_bar=False,
        )

        self.filtering_tab = self.viewer.window.add_dock_widget(
            self.filtering_widget.layout,
            name="Filtering",
            area="right",
            add_custom_title_bar=False,
        )
        # self.thresholding_tab = self.viewer.window.add_dock_widget(self.thresholding_widget.layout, name='Thresholding')
        # self.labeling_tab = self.viewer.window.add_dock_widget(self.labeling_widget.layout, name='Labeling')
        # self.misc_tab = self.viewer.window.add_dock_widget(self.misc_widget.layout, name='Misc')

    def init_analysis_widget(self, widget):
        """Add a widget to the napari viewer"""
        self.viewer.window.add_dock_widget(widget, area="right")

    def set_analysis_widget(self):
        """Set the values for the analysis widget"""
        self._set_filtering(self)
