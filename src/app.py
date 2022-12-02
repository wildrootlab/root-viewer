import sys
import os
import napari

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QGridLayout, QWidget, QApplication, QTextEdit
from PyQt5.QtCore import QSettings
import qdarktheme
from magicgui import magicgui

from enum import Enum
from typing import Callable
import ctypes

from config import Settings
import func_filters as ff
from mpl_widget import MplWidget

# set the application user mode id for windows
myappid = '2P-Analysis'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow, Settings):
    def __init__(self):
        super().__init__()
        self._main = QWidget()

        self.settings = QSettings('2P-Analysis')
        self.get_settings()
        self.setWindowTitle("2P Analysis")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "logo_light.png")))
        self.setCentralWidget(self._main)

        # create a vertical box layout widget
        self.layout = QGridLayout(self._main)

        # add an empty menuBar
        self.menu = self.menuBar()

        # add a napari viewer
        self.show_image_viewer()
        # populate the menuBar
        self.create_menue_bar()
        
        # initialize settings
        self.settings = Settings()

        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

        self.analysis_functions = {}
        self.mpl_widget = MplWidget(self)

        # create utilites
        self.create_analysis_widget()
        self.create_mpl_widget()
        self.create_processing_widget()
        # update after load completes
        self.update_window_menue()

        

    def set_settings(self):
        self.settings.setValue("window_size", self.size())
        self.settings.setValue("window_pos", self.pos())
    
    def get_settings(self):
        """Load Settings"""
        try:
            self.resize(self.settings.value("window_size"))
            self.move(self.settings.value("window_pos"))
        except:
            pass

    def show_image_viewer(self):
        """Show the napari viewer in the main window"""
        # ffs do not touch (╯°□°)╯︵ ┻━┻ 
        self.viewer = napari.Viewer(show=False)
        self._qt_viewer = self.viewer.window._qt_viewer

        self.viewer.window.main_menu.hide()
        self.viewer.window._status_bar.hide()

        qt_viewer = self.viewer.window._qt_window
        self.layout.addWidget(qt_viewer, 1, 0)
    
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
    
    def plot_visibility(self):
        self.mpl_widget_dock.setVisible(not self.mpl_widget_dock.isVisible())
    
    def analysis_widget_visibility(self):
        self.analysis_widget_dock.setVisible(not self.mpl_widget_dock.isVisible())

    def update_window_menue(self):

        self.plot_visibility_action = QAction("plot", checkable=True)
        self.viewer.window.window_menu.addAction(self.plot_visibility_action)
        self.plot_visibility_action.triggered.connect(self.plot_visibility)
        
        self.analysis_widget_visibility_action = QAction("analysis", checkable=True, checked=True)
        self.viewer.window.window_menu.addAction(self.analysis_widget_visibility_action)
        self.analysis_widget_visibility_action.triggered.connect(self.analysis_widget_visibility)

    def create_analysis_widget(self):
        self.analysis_widget_dock = self.viewer.window.add_dock_widget(self.analysis_widget, area="right", name="Analysis")
        self.analysis_widget_dock._close_btn = False
    
    def create_mpl_widget(self):
        self.mpl_widget_dock = self.viewer.window.add_dock_widget(self.mpl_widget, area='bottom', name='Plot')
        self.mpl_widget_dock.setVisible(False)
        self.mpl_widget_dock.setFloating(True)
        self.mpl_widget_dock._close_btn = False

    def create_processing_widget(self):
        self.processing_widget_dock = self.viewer.window.add_dock_widget(self.processing_widget, area="right", name="Processing")
        self.processing_widget_dock._close_btn = False

    def closeEvent(self, event):
        try:
            self.set_settings() # set the settings
            self.tempconfig.del_tmp_images() # delete temp images
        except: 
            pass

    class Functions(Enum):
        """Enumerator for the different fuctions"""
        gaussian_blur = "gaussian_blur"
        subtract_background = "subtract_background"
        threshold_otsu = "threshold_otsu"
        threshold_yen = "threshold_yen"
        threshold_isodata = "threshold_isodata"
        threshold_li = "threshold_li"
        threshold_mean = "threshold_mean"
        threshold_minimum = "threshold_minimum"
        threshold_triangle = "threshold_triangle"
        binary_invert = "binary_invert"
        split_touching_objects = "split_touching_objects"
        connected_component_labeling = "connected_component_labeling"
        seeded_watershed = "seeded_watershed"
        voronoi_otsu_labeling = "voronoi_otsu_labeling"
        gauss_otsu_labeling = "gauss_otsu_labeling"
        gaussian_laplace = "gaussian_laplace"
        median_filter = "median_filter"
        maximum_filter = "maximum_filter"
        minimum_filter = "minimum_filter"
        percentile_filter = "percentile_filter"
        black_tophat = "black_tophat"
        white_tophat = "white_tophat"
        morphological_gradient = "morphological_gradient"
        local_minima_seeded_watershed = "local_minima_seeded_watershed"
        thresholded_local_minima_seeded_watershed = "thresholded_local_minima_seeded_watershed"
        sum_images = "sum_images"
        multiply_images = "multiply_images"
        divide_images = "divide_images"
        invert_image = "invert_image"
        skeletonize = "skeletonize"
        Manually_merge_labels = "Manually_merge_labels"
        wireframe = "wireframe"
        Manually_split_labels = "Manually_split_labels"
        extract_slic = "extract_slic"

    def register_function(self, func: Callable, *args, **kwargs) -> Callable:
        """Register a function into into the function dictionary"""
        self.analysis_functions[func.__code__] = [func, "function", args, kwargs]
        return func
            
    def open_func_gui(self, func: Callable):
        self.register_function(func)
        action, type_, args, kwargs = self.analysis_functions[func.__code__]
        self.viewer.window.add_dock_widget(make_gui(action, self.viewer, *args, **kwargs), area='right', name=func.__name__)
    
    @magicgui(call_button="Open function")
    def analysis_widget(self, Function=Functions.gaussian_blur, Explanation=False):
        from inspect import getdoc
        # call the relevent function !!FIX THIS WITH REGISTERED FUNCTIONS!!
        func_dict = {
        "gaussian_blur" : ff.gaussian_blur,
        "subtract_background" : ff.subtract_background,
        "threshold_otsu" : ff.threshold_otsu,
        "threshold_yen" : ff.threshold_yen,
        "threshold_isodata" : ff.threshold_isodata,
        "threshold_li" : ff.threshold_li,
        "threshold_mean" : ff.threshold_mean,
        "threshold_minimum" : ff.threshold_minimum,
        "threshold_triangle" : ff.threshold_triangle,
        "binary_invert" : ff.binary_invert,
        "split_touching_objects" : ff.split_touching_objects,
        "connected_component_labeling" : ff.connected_component_labeling,
        "seeded_watershed" : ff.seeded_watershed,
        "voronoi_otsu_labeling" : ff.voronoi_otsu_labeling,
        "gauss_otsu_labeling" : ff.gauss_otsu_labeling,
        "gaussian_laplace" : ff.gaussian_laplace,
        "median_filter" : ff.median_filter,
        "maximum_filter" : ff.maximum_filter,
        "minimum_filter" : ff.minimum_filter,
        "percentile_filter" : ff.percentile_filter,
        "black_tophat" : ff.black_tophat,
        "white_tophat" : ff.white_tophat,
        "morphological_gradient" : ff.morphological_gradient,
        "local_minima_seeded_watershed" : ff.local_minima_seeded_watershed,
        "thresholded_local_minima_seeded_watershed" : ff.thresholded_local_minima_seeded_watershed,
        "sum_images" : ff.sum_images,
        "multiply_images" : ff.multiply_images,
        "divide_images" : ff.divide_images,
        "invert_image" : ff.invert_image,
        "skeletonize" : ff.skeletonize,
        "Manually_merge_labels" : ff.Manually_merge_labels,
        "wireframe" : ff.wireframe,
        "Manually_split_labels" : ff.Manually_split_labels,
        }
        try:
            self.open_func_gui(func_dict[Function.value])
            # create function help widget
            if Explanation == True:
                func_help_dock = self.viewer.window.add_dock_widget(self.func_help(func_dict[Function.value]), area='right', name=f"Help: {func_dict[Function.value].__name__}")
                func_help_dock.setFloating(True)

        except Exception as e:
            print(e)

    @magicgui(call_button="Polt")
    def processing_widget(label_image: "napari.types.LabelsData"):
        print(f'{label_image}processing_function')

    def func_help(self, func):
        """Create a basic help widget for functions"""
        func_doc = func.__doc__
        text = [f'{func.__name__}: ', f'{func_doc}', 'Parameters: ', f'{func.__code__}']
        text2 = '\n'.join(text)

        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)
        
        text_area = QTextEdit()
        text_area.setText(text2)
        text_area.setReadOnly(True)
        text_area.setLineWrapColumnOrWidth(75)
        layout.addWidget(text_area, 0,0)
        
        return widget


"""
Labels layer -> data processing -> plot
"""




def make_gui(func, viewer, *args, **kwargs):
    """Create a magicgui widget for a function"""
    gui = None
    from napari.types import ImageData, LabelsData, PointsData, SurfaceData
    import inspect
    from functools import wraps
    import numpy as np
    sig = inspect.signature(func)
    @wraps(func)
    def worker_func(*iargs, **ikwargs):
        """Wrapper function to pass arguments to the function"""
        data = func(*iargs, **ikwargs)
        if data is None:
            return None
        # determine scale of passed data
        scale = None
        from napari_workflows._workflow import _get_layer_from_data
        for passed_data in iargs:
            layer = _get_layer_from_data(viewer, passed_data)
            if layer is not None and isinstance(layer, napari.layers.Image):
                scale = layer.scale
        target_layer = None
        if sig.return_annotation in [ImageData, "napari.types.ImageData", LabelsData, "napari.types.LabelsData",
                                     PointsData, "napari.types.PointsData", SurfaceData, "napari.types.SurfaceData"]:
            op_name = func.__name__
            new_name = f"Result of {op_name}"
            # we now search for a layer that has -this- magicgui attached to it
            try:
                # look for an existing layer
                target_layer = next(x for x in viewer.layers if x.source.widget is gui)
                target_layer.data = data
                target_layer.name = new_name
                # layer.translate = translate
                if sig.return_annotation in [PointsData, "napari.types.PointsData"]:
                    target_layer.size = np.asarray(viewer.dims.range).max() * 0.01
            except StopIteration:
                # otherwise create a new one
                from napari.layers._source import layer_source
                with layer_source(widget=gui):
                    if sig.return_annotation in [ImageData, "napari.types.ImageData"]:
                        target_layer = viewer.add_image(data, name=new_name)
                    elif sig.return_annotation in [LabelsData, "napari.types.LabelsData"]:
                        target_layer = viewer.add_labels(data, name=new_name)
                    elif sig.return_annotation in [PointsData, "napari.types.PointsData"]:
                        target_layer = viewer.add_points(data, name=new_name)
                        target_layer.size = np.asarray(viewer.dims.range).max() * 0.01
                    elif sig.return_annotation in [SurfaceData, "napari.types.SurfaceData"]:
                        target_layer = viewer.add_surface(data, name=new_name)
                # apply scale to data if successfully determined above
                if scale is not None and target_layer is not None:
                    if len(target_layer.data.shape) == len(scale):
                        target_layer.scale = scale
                    if len(target_layer.data.shape) < len(scale):
                        target_layer.scale = scale[-len(target_layer.data.shape):]
        if target_layer is not None:
            # update the workflow manager in case it's installed
            try:
                from napari_workflows import WorkflowManager
                workflow_manager = WorkflowManager.install(viewer)
                workflow_manager.update(target_layer, func, *iargs, **ikwargs)
            except ImportError:
                pass
            return None
        else:
            return data
    gui = magicgui(worker_func, *args, **kwargs)
    return gui

if __name__ == "__main__":
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)
    qapp.setStyleSheet(qdarktheme.load_stylesheet())
    app = MainWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()