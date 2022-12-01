import sys
import os
import napari

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QVBoxLayout, QWidget, QApplication
from PyQt5.QtCore import QSettings
import qdarktheme
from magicgui import magicgui

from enum import Enum
from typing import Callable
import ctypes

from Config import TempFile
import func_filters as ff

# set the application user mode id for windows
myappid = '2P-Analysis'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow, TempFile):
    def __init__(self):
        super().__init__()
        self._main = QWidget()

        self.settings = QSettings('2P-Analysis')
        self.get_settings()
        self.setWindowTitle("2P analysis")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "logo_light.png")))
        self.setCentralWidget(self._main)

        # create a vertical box layout widget
        self.layout = QVBoxLayout(self._main)

        # add an empty menuBar
        self.menu = self.menuBar()

        # add a napari viewer
        self.show_image_viewer()
        # populate the menuBar
        self.create_menue_bar()

        # set temp dir
        self.tempconfig = TempFile()
        self.tmppath = self.tempconfig.get_tmp_path(self)

        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

        self.ToolsMenu = {}

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
        self.viewer = napari.Viewer()
        self._qt_viewer = self.viewer.window._qt_viewer

        self.viewer.window.main_menu.hide()
        self.viewer.window._status_bar.hide()

        self.viewer.window.add_dock_widget(self.segmenting_widget, area="right", name="Segmentation")

        qt_viewer = self.viewer.window._qt_window
        self.layout.addWidget(qt_viewer)
    
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
        #plugin_menu = self.menu.addMenu(self.viewer.window.plugins_menu)
        
    def closeEvent(self, event):
        try:
            self.set_settings() # set the settings
            self.tempconfig.del_tmp_images() # delete temp images
        except: 
            pass

    class Functions(Enum):
        """Enum for the different fuctions"""
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
                self.ToolsMenu[func.__code__] = [func, "function", args, kwargs]
                return func
            
    def open_func_gui(self, func: Callable):
        self.register_function(func)
        action, type_, args, kwargs = self.ToolsMenu[func.__code__]
        self.viewer.window.add_dock_widget(make_gui(action, self.viewer, *args, **kwargs), area='right', name=func.__name__)
    
    @magicgui(call_button="Use function")
    def segmenting_widget(self, Function=Functions.gaussian_blur, label="TEST"):

        # call the relevent function
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
        except Exception as e:
            print(e)

    @magicgui(call_button="Polt")
    def plot_widget(self):
        print("PLOTTING")


def make_sub_sub_menu(self, action, title, window, action_type_tuple):
    import inspect
    def func(whatever=None):
        sub_sub_menu = action
        # ugh
        napari_viewer = self.viewer
        action, type_, args, kwargs = action_type_tuple
        dw = None
        if type_ == "action":
            action(napari_viewer)
        elif type_ == "function":
            dw = napari_viewer.window.add_dock_widget(self.make_gui(action, napari_viewer, *args, **kwargs), area='right', name=title)
        elif type_ == "dock_widget":
            # Source: https://github.com/napari/napari/blob/1287e618469e765a6db0e80d11e736b738e62823/napari/_qt/qt_main_window.py#L669
            # if the signature is looking a for a napari viewer, pass it.
            kwargs = {}
            for param in inspect.signature(action.__init__).parameters.values():
                if param.name == 'napari_viewer':
                    kwargs['napari_viewer'] = napari_viewer
                    break
                if param.annotation in ('napari.viewer.Viewer', napari.Viewer):
                    kwargs[param.name] = napari_viewer
                    break
                # cannot look for param.kind == param.VAR_KEYWORD because
                # QWidget allows **kwargs but errs on unknown keyword arguments
            # instantiate the widget
            wdg = action(**kwargs)
            dw = napari_viewer.window.add_dock_widget(wdg, name=title)
        if dw is not None:
            # workaround for https://github.com/napari/napari/issues/4348
            dw._close_btn = False
        return sub_sub_menu

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