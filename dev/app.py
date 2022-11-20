import sys
import os
import time
import napari
from PyQt5.QtGui import QIcon, QPixmap

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction, QVBoxLayout, QWidget, QApplication, QSplashScreen, QProgressBar
from PyQt5.QtCore import QSettings, QThread, pyqtSignal, QObject, pyqtSlot
import qdarktheme
from functools import wraps
from magicgui import magicgui
from enum import Enum

import inspect
from Config import TempFile
from skimage.io import imread
from enum import Enum
import func_filters as ff

from typing import Callable
import ctypes

# set the application user mode id for windows
myappid = '2P-Analysis'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow, TempFile):
    def __init__(self):
        super().__init__()
        self._main = QWidget()
        self.show_splash()
        self.settings = QSettings('2P-Analysis')
        self.get_settings()
        self.setWindowTitle("Danny's very special 2P analysis")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "logo_light.png")))
        self.setCentralWidget(self._main)
        # create a vertical box layout widget
        self.layout = QVBoxLayout(self._main)
        # add a menuBar
        self.menu = self.menuBar()
        self._create_menue_bar()
        # add a napari viewer
        self.show_image_viewer()
        # set progress bar
        self.popup = PopUpProgressB()
        self.popup.show
        # set temp dir
        self.tempconfig = TempFile()
        self.tmppath = self.tempconfig.get_tmp_path(self)

        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

        self.ToolsMenu = {}
    
    def show_splash(self):
        try:
            self.splash = QSplashScreen(QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "logo_dark.png")))
            self.splash.show()
        except: 
            pass
    
    def close_splash(self):
        self.splash.close


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
        self.viewer = napari.Viewer(show=False)
        #self.viewer.window.qt_viewer.dockLayerList.hide()
        #self.viewer.window.qt_viewer.dockConsole.hide()
        #self.viewer.window.qt_viewer.dockLayerControls.hide()
        self.viewer.window.main_menu.clear()
        self.viewer.window._status_bar.hide()
        self.viewer.window.add_dock_widget(self.segmenting_widget, area="right", name="Segmentation")
        qt_viewer = self.viewer.window._qt_window
        self.layout.addWidget(qt_viewer)
    
    def _create_menue_bar(self):
        file_menu = self.menu.addMenu("&File")
        file_menu.addAction("Open File", self._open_file)
        file_menu.addAction("Open Folder", self._open_dir)

    def _open_dir(self):
        """Select a directory and copy files in directory to temp dir"""
        try:
            dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            self.tempconfig.dir_images_to_tmp(dir)
            self._view_images(os.path.join(self.tmppath, "images", "*.tif"))
        except Exception as e:
            print(e)
        
    def closeEvent(self, event):
        try:
            self.set_settings() # set the settings
            self.tempconfig.del_tmp_images() # delete temp images
        except: 
            pass

    def _open_file(self):
        print(str(QFileDialog.getOpenFileName(self, "Select File")))
    
    def _view_images(self, images):
        self.img = imread(images, plugin="tifffile")
        self.viewer.dims.ndisplay = 3
        self.viewer.add_image(self.img, scale=[1, 1, 1])

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
        Manually_split_labels = "Manually_split_labels"
        extract_slic = "extract_slic"

    def register_function(self, func: Callable, *args, **kwargs) -> Callable:
                self.ToolsMenu[func.__code__] = [func, "function", args, kwargs]
                print("Registered function: ", func.__name__)
                return func
            
    def open_func_gui(self, func: Callable):
        self.register_function(func)
        action, type_, args, kwargs = self.ToolsMenu[func.__code__]
        print("Opening function: ", func.__name__)
        self.viewer.window.add_dock_widget(make_gui(action, self.viewer, *args, **kwargs), area='right', name=func.__name__)
    
    @magicgui(call_button="Use function")
    def segmenting_widget(self, Function=Functions.gaussian_blur):

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
    from functools import wraps
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
        print("woooooooooooooooooooooork")
        app.popup.show
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

class ProgressBarWorker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)

    @pyqtSlot()
    def proc_counter(self):  # A slot takes no params
        for i in range(1, 100):
            print(i)
            time.sleep(1)
            self.intReady.emit(i)

        self.finished.emit()

class PopUpProgressB(QWidget):

    def __init__(self):
        super().__init__()
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 500, 75)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pbar)
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 550, 100)
        self.setWindowTitle('Progress Bar')


        self.obj = ProgressBarWorker()
        self.thread = QThread()
        self.obj.intReady.connect(self.on_count_changed)
        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)
        self.thread.started.connect(self.obj.proc_counter)
        self.thread.start()

    def on_count_changed(self, value):
        self.pbar.setValue(value)


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