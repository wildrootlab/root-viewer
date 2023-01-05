import warnings
from typing import ClassVar
from weakref import WeakSet

from napari._qt.containers import QtLayerList
from napari._qt.layer_controls import QtLayerControlsContainer
from napari._qt.widgets.qt_viewer_buttons import QtLayerButtons, QtViewerButtons
from napari.components import ViewerModel
from napari.utils.action_manager import action_manager
from napari.utils.translations import trans
from qtpy.QtCore import QCoreApplication, Qt
from qtpy.QtWidgets import QSplitter, QVBoxLayout, QWidget

from root_viewer.backend._qt.widgets.dock_widgets import QtViewerDockWidget


class Napari(ViewerModel):
    """The Napari application."""

    _window: "Window" = None  # type: ignore
    _instances: ClassVar[WeakSet["Napari"]] = WeakSet()

    def __init__(self):
        super().__init__(
            title="Root Viewer",
            ndisplay=2,
            order=(),
            axis_labels=(),
        )
        # we delay initialization of plugin system to the first instantiation
        # of a viewer... rather than just on import of plugins module
        from napari.plugins import _initialize_plugins

        # having this import here makes all of Qt imported lazily, upon
        # instantiating the first Viewer.
        from napari.window import Window as NapariWindow

        _initialize_plugins()

        self._window = NapariWindow(self, show=False)
        self._instances.add(self)

    # Expose private window publically. This is needed to keep window off pydantic model
    @property
    def window(self) -> "NapariWindow":  # type: ignore
        return self._window

    def update_console(self, variables):
        """Update console's namespace with desired variables.

        Parameters
        ----------
        variables : dict, str or list/tuple of str
            The variables to inject into the console's namespace.  If a dict, a
            simple update is done.  If a str, the string is assumed to have
            variable names separated by spaces.  A list/tuple of str can also
            be used to give the variable names.  If just the variable names are
            give (list/tuple/str) then the variable values looked up in the
            callers frame.
        """
        if self.window._qt_viewer._console is None:
            return
        else:
            self.window._qt_viewer.console.push(variables)

    def show(self, *, block=False):
        """Resize, show, and raise the viewer window."""
        self.window.show(block=block)

    def close(self):
        """Close the viewer window."""
        # Remove all the layers from the viewer
        self.layers.clear()
        # Close the main window
        self.window.close()

        self._instances.discard(self)

    @classmethod
    def close_all(cls) -> int:
        """
        Class metod, Close all existing viewer instances.

        This is mostly exposed to avoid leaking of viewers when running tests.
        As having many non-closed viewer can adversely affect performances.

        It will return the number of viewer closed.

        Returns
        -------
        int
            number of viewer closed.

        """
        # copy to not iterate while changing.
        viewers = [v for v in cls._instances]
        ret = len(viewers)
        for viewer in viewers:
            viewer.close()
        return ret


class NapariWidgets(QSplitter):
    """Qt widgets for the napari Viewer model using custom QtViewerDockWidget.

    Attributes
    ----------
    console : QtConsole
        IPython console terminal integrated into the napari GUI.
    controls : QtLayerControlsContainer
        Qt view for GUI controls.
    dims : napari.qt_dims.QtDims
        Dimension sliders; Qt View for Dims model.
    dockConsole : QtViewerDockWidget
        QWidget wrapped in a QDockWidget with forwarded viewer events.
    dockLayerControls : QtViewerDockWidget
        QWidget wrapped in a QDockWidget with forwarded viewer events.
    dockLayerList : QtViewerDockWidget
        QWidget wrapped in a QDockWidget with forwarded viewer events.
    layerButtons : QtLayerButtons
        Button controls for napari layers.
    layers : QtLayerList
        Qt view for LayerList controls.
    """

    _instances = WeakSet()

    def __init__(
        self,
        viewer: ViewerModel,
    ):

        super().__init__()
        self._instances.add(self)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        QCoreApplication.setAttribute(
            Qt.AA_UseStyleSheetPropagationInWidgetStyles, True
        )

        self.viewer = viewer
        self._controls = None
        self._layers = None
        self._layersButtons = None
        self._viewerButtons = None
        self._console = None

        self._dockLayerList = None
        self._dockLayerControls = None
        self._dockConsole = None
        self._dockPerformance = None

    def _ensure_connect(self):
        # lazy load console
        id(self.console)

    @property
    def controls(self) -> QtLayerControlsContainer:
        if self._controls is None:
            # Avoid circular import.
            from napari._qt.layer_controls import QtLayerControlsContainer

            self._controls = QtLayerControlsContainer(self.viewer)
        return self._controls

    @property
    def layers(self) -> QtLayerList:
        if self._layers is None:
            self._layers = QtLayerList(self.viewer.layers)
        return self._layers

    @property
    def layerButtons(self) -> QtLayerButtons:
        if self._layersButtons is None:
            self._layersButtons = QtLayerButtons(self.viewer)
        return self._layersButtons

    @property
    def viewerButtons(self) -> QtViewerButtons:
        if self._viewerButtons is None:
            self._viewerButtons = QtViewerButtons(self.viewer)
        return self._viewerButtons

    @property
    def dockLayerList(self) -> QtViewerDockWidget:
        if self._dockLayerList is None:
            layerList = QWidget()
            layerList.setObjectName("layerList")
            layerListLayout = QVBoxLayout()
            layerListLayout.addWidget(self.layerButtons)
            layerListLayout.addWidget(self.layers)
            layerListLayout.addWidget(self.viewerButtons)
            layerListLayout.setContentsMargins(8, 4, 8, 6)
            layerList.setLayout(layerListLayout)
            self._dockLayerList = QtViewerDockWidget(
                self,
                layerList,
                name=trans._("layer list"),
                area="left",
                allowed_areas=["left", "right"],
                object_name="layer list",
                close_btn=False,
            )
        return self._dockLayerList

    @property
    def dockLayerControls(self) -> QtViewerDockWidget:
        if self._dockLayerControls is None:
            self._dockLayerControls = QtViewerDockWidget(
                self,
                self.controls,
                name=trans._("layer controls"),
                area="left",
                allowed_areas=["left", "right"],
                object_name="layer controls",
                close_btn=False,
            )
        return self._dockLayerControls

    @property
    def dockConsole(self) -> QtViewerDockWidget:
        if self._dockConsole is None:
            self._dockConsole = QtViewerDockWidget(
                self,
                QWidget(),
                name=trans._("console"),
                area="bottom",
                allowed_areas=["top", "bottom"],
                object_name="console",
                close_btn=False,
            )
            self._dockConsole.setVisible(False)
            self._dockConsole.visibilityChanged.connect(self._ensure_connect)
        return self._dockConsole

    @property
    def console(self):
        """QtConsole: iPython console terminal integrated into the napari GUI."""
        if self._console is None:
            try:
                import napari
                from napari_console import QtConsole

                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    self.console = QtConsole(self.viewer)
                    self.console.push(
                        {"napari": napari, "action_manager": action_manager}
                    )
            except ModuleNotFoundError:
                warnings.warn(
                    trans._(
                        "napari-console not found. It can be installed with"
                        ' "pip install napari_console"'
                    )
                )
                self._console = None
            except ImportError:
                import traceback

                traceback.print_exc()
                warnings.warn(
                    trans._(
                        "error importing napari-console. See console for full error."
                    )
                )
                self._console = None
        return self._console

    @console.setter
    def console(self, console):
        self._console = console
        if console is not None:
            self.dockConsole.setWidget(console)
            console.setParent(self.dockConsole)
