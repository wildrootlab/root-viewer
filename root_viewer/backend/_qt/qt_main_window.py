"""
Backend Qt Window classes
This module is currently a bit of a mess...
TODO: load qt_viewer_dock_widgets with proper styling and clean up
"""

import contextlib
import warnings
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from weakref import WeakValueDictionary

from qtpy.QtCore import Qt, QSettings
from qtpy.QtGui import QIcon, QImage
from qtpy.QtWidgets import (
    QApplication,
    QDockWidget,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QShortcut,
    QWidget,
)

from root_viewer.backend._qt.qt_event_loop import ICON_PATH, get_app, _defaults
from root_viewer.backend._qt.qt_napari_viewer import Napari, NapariWidgets
from root_viewer.backend._qt.widgets.dock_widgets import QtViewerDockWidget

from napari._qt.widgets.qt_viewer_dock_widget import _SHORTCUT_DEPRECATION_STRING
from napari._qt.qt_resources import get_stylesheet
from napari._qt.utils import QImg2array
from napari.utils.io import imsave
from napari.utils.misc import in_jupyter
from napari.utils.theme import _themes, get_system_theme
from napari.utils.translations import trans
from napari.settings import get_settings
from napari._qt.qt_resources import get_stylesheet
_sentinel = object()

from magicgui.widgets import Widget


class NapariQtApp(Napari):
    """An abstraction of the Napari application. This is the only calss that may call
    the Napari application and Qt event loop. This class is a subclass of the NapariViewer.
    """
    def __init__(self):
        super().__init__()
        self.qt_viewer()

    def qt_viewer(self):
        """This instanciates an of the entire Naprari application"""
        return self.window._qt_window

    @property
    def viewer_widget(self):
        """Qt widget for the napari Viewer model."""
        return self.window._qt_viewer
    
    @property
    def _qt_viewer(self):
        return self.window._qt_viewer
    
    @property
    def file_menu(self):
        return self.window.file_menu
    
    @property
    def view_menu(self):
        return self.window.view_menu
    
    @property
    def window_menu(self):
        return self.window.window_menu


class _QtMainWindow(QMainWindow):
    """The root Qt window for the application.
    Contains the napari viewer and any other top-level widgets.
    
    Parameters
    ----------
    window : Window
        The application window.
    parent : QWidget, optional
        The parent widget, by default None
    
    Attributes
    ----------
    main_widow : Window
        The application window.
    viewer_widget : QtViewer
        The napari viewer.
    _qt_viewer_dock_widgets : List[QtViewerDockWidget]
        The list of dock widgets for the viewer.
    """
    _window_icon = ICON_PATH
    _window_name = _defaults['app_name']

    # To track window instances and facilitate getting the "active" viewer...
    # We use this instead of QApplication.activeWindow for compatibility with
    # IPython usage. When you activate IPython, it will appear that there are
    # *no* active windows, so we want to track the most recently active windows
    _instances: ClassVar[List['_QtMainWindow']] = []

    def __init__(
        self, window: 'Window', parent=None, theme: str = 'dark'
    ) -> None:
        super().__init__(parent)
        # create QApplication if it doesn't already exist
        get_app()
        
        self.main_widow = window
        self.setStyleSheet(get_stylesheet(theme))
        
        # temporary method for settings until we have a settings manager
        self.settings = QSettings('Root Viewer')
        self.get_settings()

        self.setWindowTitle("Root Viewer")
        self.setWindowIcon(QIcon(self._window_icon))

        self.napari = NapariQtApp()

        self._qt_viewer = self.napari._qt_viewer

        self.viewer_widget = self.napari.viewer_widget

        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setUnifiedTitleAndToolBarOnMac(True)
        
        # set the viewer as the central widget
        center = QWidget(self)
        center.setLayout(QHBoxLayout())
        center.layout().addWidget(self.viewer_widget)
        #center.layout().addWidget(self.ndim_btn)
        center.layout().setContentsMargins(4, 0, 4, 0)
        self.setCentralWidget(center)
        
        _QtMainWindow._instances.append(self)
    
    def get_settings(self):
        """Load Settings"""
        try:
            self.resize(self.settings.value("window_size"))
            self.move(self.settings.value("window_pos"))
        except:
            pass
    
    def set_settings(self):
        try:
            self.settings.setValue("window_size", self.size())
            self.settings.setValue("window_pos", self.pos())
        except: pass
    
    def closeEvent(self, event):
        """Cleanup when window is closed."""
        self.set_settings()
        self.napari.close_all()
        _QtMainWindow._instances.remove(self)
        super().closeEvent(event)


class Window:
    """Application window that contains the menu bar and viewer.

    Parameters
    ----------
    viewer : napari.components.ViewerModel
        Contained viewer widget.

    Attributes
    ----------
    file_menu : qtpy.QtWidgets.QMenu
        File menu.
    help_menu : qtpy.QtWidgets.QMenu
        Help menu.
    main_menu : qtpy.QtWidgets.QMainWindow.menuBar
        Main menubar.
    view_menu : qtpy.QtWidgets.QMenu
        View menu.
    window_menu : qtpy.QtWidgets.QMenu
        Window menu.
    """

    def __init__(self, *, show: bool = True) -> None:
        # create an instance of the napari viewer
        #self.viewer = Viewer(show=False)

        # Dictionary holding dock widgets
        self._dock_widgets: Dict[
            str, QtViewerDockWidget
        ] = WeakValueDictionary()
        # track unnamed dock widgets, so we can give them unique names
        self._unnamed_dockwidget_count = 1


        # connect the Viewer and create the Main Window
        self.main_widow = _QtMainWindow(self)
        self.viewer_widget = self.main_widow.napari.viewer_widget

        self.napari_widgets = NapariWidgets(self.main_widow.napari)
        self._add_menus()

        #self._update_theme()

        #get_settings().appearance.events.theme.connect(self._update_theme)

        self._add_viewer_dock_widget(
            self.napari_widgets.dockConsole,
            tabify=False,
            #add_custom_title_bar=False,
        )
        self._add_viewer_dock_widget(
            self.napari_widgets.dockLayerControls,
            tabify=False,
            #add_custom_title_bar=False,
        )
        self._add_viewer_dock_widget(
            self.napari_widgets.dockLayerList,
            tabify=False,
            #add_custom_title_bar=False,
        )

        if show:
          self.show(block=False)
          # Ensure the controls dock uses the minimum height
          self.main_widow.resizeDocks(
              [
                  self.viewer_widget.dockLayerControls,
                  self.viewer_widget.dockLayerList,
              ],
              [self.viewer_widget.dockLayerControls.minimumHeight(), 10000],
              Qt.Orientation.Vertical,
          )

    def _setup_existing_themes(self, connect: bool = True):
        """This function is only executed once at the startup of napari
        to connect events to themes that have not been connected yet.

        Parameters
        ----------
        connect : bool
            Determines whether the `connect` or `disconnect` method should be used.
        """
        for theme in _themes.values():
            if connect:
                self._connect_theme(theme)
            else:
                self._disconnect_theme(theme)

    def _connect_theme(self, theme):
        # connect events to update theme. Here, we don't want to pass the event
        # since it won't have the right `value` attribute.
        theme.events.background.connect(self._update_theme_no_event)
        theme.events.foreground.connect(self._update_theme_no_event)
        theme.events.primary.connect(self._update_theme_no_event)
        theme.events.secondary.connect(self._update_theme_no_event)
        theme.events.highlight.connect(self._update_theme_no_event)
        theme.events.text.connect(self._update_theme_no_event)
        theme.events.warning.connect(self._update_theme_no_event)
        theme.events.current.connect(self._update_theme_no_event)
        theme.events.icon.connect(self._update_theme_no_event)
        theme.events.canvas.connect(
            lambda _: self.viewer_widget.canvas._set_theme_change(
                get_settings().appearance.theme
            )
        )
        # connect console-specific attributes only if QtConsole
        # is present. The `console` is called which might slow
        # things down a little.
        if self.viewer_widget._console:
            theme.events.console.connect(self.viewer_widget.console._update_theme)
            theme.events.syntax_style.connect(
                self.viewer_widget.console._update_theme
            )

    def _disconnect_theme(self, theme):
        theme.events.background.disconnect(self._update_theme_no_event)
        theme.events.foreground.disconnect(self._update_theme_no_event)
        theme.events.primary.disconnect(self._update_theme_no_event)
        theme.events.secondary.disconnect(self._update_theme_no_event)
        theme.events.highlight.disconnect(self._update_theme_no_event)
        theme.events.text.disconnect(self._update_theme_no_event)
        theme.events.warning.disconnect(self._update_theme_no_event)
        theme.events.current.disconnect(self._update_theme_no_event)
        theme.events.icon.disconnect(self._update_theme_no_event)
        theme.events.canvas.disconnect(
            lambda _: self.viewer_widget.canvas._set_theme_change(
                get_settings().appearance.theme
            )
        )
        # disconnect console-specific attributes only if QtConsole
        # is present and they were previously connected
        if self.viewer_widget._console:
            theme.events.console.disconnect(
                self.viewer_widget.console._update_theme
            )
            theme.events.syntax_style.disconnect(
                self.viewer_widget.console._update_theme
            )

    def _add_theme(self, event):
        """Add new theme and connect events."""
        theme = event.value
        self._connect_theme(theme)

    def _remove_theme(self, event):
        """Remove theme and disconnect events."""
        theme = event.value
        self._disconnect_theme(theme)

    def _add_menus(self):
        """Add menus to the menubar."""
        self.main_menu = self.main_widow.menuBar()
        self.file_menu = self.main_menu.addMenu('&File')
        self.view_menu = self.main_menu.addMenu('&View')
        self.window_menu = self.main_menu.addMenu('&Window')

        for action in self.main_widow.napari.file_menu.actions():
            data = action.data()
            try:
                name = data.get('text')
                if name not in ['Save Screenshot...', 'Save Screenshot with Viewer...','Copy Screenshot to Clipboard','Copy Screenshot with Viewer to Clipboard', 'Close Window']:
                    self.file_menu.addAction(action)
            except: pass
        for action in self.main_widow.napari.view_menu.actions():
            data = action.data()
            try:
                name = data.get('text')
                if name not in ['Toggle Full Screen', 'Toggle Menubar Visibility']:
                    self.view_menu.addAction(action)
            except: pass
        for action in self.main_widow.napari.window_menu.actions():
            data = action.data()
            try:
                self.window_menu.addAction(action)
            except: pass


    def _toggle_menubar_visible(self):
        """Toggle visibility of app menubar.

        This function also disables or enables a global keyboard shortcut to
        show the menubar, since menubar shortcuts are only available while the
        menubar is visible.
        """
        self.main_menu.setVisible(not self.main_menu.isVisible())
        self._main_menu_shortcut.setEnabled(not self.main_menu.isVisible())

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.main_widow.isFullScreen():
            self.main_widow.showNormal()
        else:
            self.main_widow.showFullScreen()

    def _toggle_play(self):
        """Toggle play."""
        if self.viewer_widget.dims.is_playing:
            self.viewer_widget.dims.stop()
        else:
            axis = self.viewer_widget.viewer.dims.last_used or 0
            self.viewer_widget.dims.play(axis)

    def add_dock_widget(
        self,
        widget: Union[QWidget, 'Widget'],
        *,
        name: str = '',
        area: str = 'right',
        allowed_areas: Optional[Sequence[str]] = None,
        shortcut=_sentinel,
        add_vertical_stretch=True,
        add_custom_title_bar=True,
        tabify: bool = False,
        menu: Optional[QMenu] = None,
    ):
        """Convenience method to add a QDockWidget to the main window.

        If name is not provided a generic name will be addded to avoid
        `saveState` warnings on close.

        Parameters
        ----------
        widget : QWidget
            `widget` will be added as QDockWidget's main widget.
        name : str, optional
            Name of dock widget to appear in window menu.
        area : str
            Side of the main window to which the new dock widget will be added.
            Must be in {'left', 'right', 'top', 'bottom'}
        allowed_areas : list[str], optional
            Areas, relative to main window, that the widget is allowed dock.
            Each item in list must be in {'left', 'right', 'top', 'bottom'}
            By default, all areas are allowed.
        shortcut : str, optional
            Keyboard shortcut to appear in dropdown menu.
        add_vertical_stretch : bool, optional
            Whether to add stretch to the bottom of vertical widgets (pushing
            widgets up towards the top of the allotted area, instead of letting
            them distribute across the vertical space).  By default, True.

            .. deprecated:: 0.4.8

                The shortcut parameter is deprecated since version 0.4.8, please use
                the action and shortcut manager APIs. The new action manager and
                shortcut API allow user configuration and localisation.
        add_custom_title_bar : bool, optional
            Whether to add a custom title bar with buttons for closing, hiding, and floating the dock widget. By default, True.
        tabify : bool
            Flag to tabify dockwidget or not.
        menu : QMenu, optional
            Menu bar to add toggle action to. If `None` nothing added to menu.

        Returns
        -------
        dock_widget : QtViewerDockWidget
            `dock_widget` that can pass viewer events.
        """
        if not name:
            with contextlib.suppress(AttributeError):
                name = widget.objectName()
            name = name or trans._(
                "Dock widget {number}",
                number=self._unnamed_dockwidget_count,
            )

            self._unnamed_dockwidget_count += 1

        if shortcut is not _sentinel:
            warnings.warn(
                _SHORTCUT_DEPRECATION_STRING.format(shortcut=shortcut),
                FutureWarning,
                stacklevel=2,
            )
            dock_widget = QtViewerDockWidget(
                self.viewer_widget,
                widget,
                name=name,
                area=area,
                allowed_areas=allowed_areas,
                shortcut=shortcut,
                add_vertical_stretch=add_vertical_stretch,
                add_custom_title_bar=add_custom_title_bar,
            )
        else:
            dock_widget = QtViewerDockWidget(
                self.viewer_widget,
                widget,
                name=name,
                area=area,
                allowed_areas=allowed_areas,
                add_vertical_stretch=add_vertical_stretch,
                add_custom_title_bar=add_custom_title_bar,
            )

        self._add_viewer_dock_widget(dock_widget, tabify=tabify, menu=menu)

        if hasattr(widget, 'reset_choices'):
            # Keep the dropdown menus in the widget in sync with the layer model
            # if widget has a `reset_choices`, which is true for all magicgui
            # `CategoricalWidget`s
            layers_events = self.viewer_widget.viewer.layers.events
            layers_events.inserted.connect(widget.reset_choices)
            layers_events.removed.connect(widget.reset_choices)
            layers_events.reordered.connect(widget.reset_choices)

        # Add dock widget to dictionary
        self._dock_widgets[dock_widget.name] = dock_widget

        return dock_widget

    def _add_viewer_dock_widget(
        self,
        dock_widget: QtViewerDockWidget,
        tabify: bool = False,
        menu: Optional[QMenu] = None,
    ):
        """Add a QtViewerDockWidget to the main window

        If other widgets already present in area then will tabify.

        Parameters
        ----------
        dock_widget : QtViewerDockWidget
            `dock_widget` will be added to the main window.
        tabify : bool
            Flag to tabify dockwidget or not.
        menu : QMenu, optional
            Menu bar to add toggle action to. If `None` nothing added to menu.
        """
        # Find if any othe dock widgets are currently in area
        current_dws_in_area = [
            dw
            for dw in self.main_widow.findChildren(QDockWidget)
            if self.main_widow.dockWidgetArea(dw) == dock_widget.qt_area
        ]
        self.main_widow.addDockWidget(dock_widget.qt_area, dock_widget)

        # If another dock widget present in area then tabify
        if current_dws_in_area:
            if tabify:
                self.main_widow.tabifyDockWidget(
                    current_dws_in_area[-1], dock_widget
                )
                dock_widget.show()
                dock_widget.raise_()
            elif dock_widget.area in ('right', 'left'):
                _wdg = current_dws_in_area + [dock_widget]
                # add sizes to push lower widgets up
                sizes = list(range(1, len(_wdg) * 4, 4))
                self.main_widow.resizeDocks(
                    _wdg, sizes, Qt.Orientation.Vertical
                )

        if menu:
            action = dock_widget.toggleViewAction()
            action.setStatusTip(dock_widget.name)
            action.setText(dock_widget.name)
            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                # deprecating with 0.4.8, but let's try to keep compatibility.
                shortcut = dock_widget.shortcut
            if shortcut is not None:
                action.setShortcut(shortcut)

            menu.addAction(action)

        # see #3663, to fix #3624 more generally
        dock_widget.setFloating(False)

    def _remove_dock_widget(self, event=None):
        names = list(self._dock_widgets.keys())
        for widget_name in names:
            if event.value in widget_name:
                # remove this widget
                widget = self._dock_widgets[widget_name]
                self.remove_dock_widget(widget)

    def remove_dock_widget(self, widget: QWidget, menu=None):
        """Removes specified dock widget.

        If a QDockWidget is not provided, the existing QDockWidgets will be
        searched for one whose inner widget (``.widget()``) is the provided
        ``widget``.

        Parameters
        ----------
        widget : QWidget | str
            If widget == 'all', all docked widgets will be removed.
        """
        if widget == 'all':
            for dw in list(self._dock_widgets.values()):
                self.remove_dock_widget(dw)
            return

        if not isinstance(widget, QDockWidget):
            dw: QDockWidget
            for dw in self.main_widow.findChildren(QDockWidget):
                if dw.widget() is widget:
                    _dw: QDockWidget = dw
                    break
            else:
                raise LookupError(
                    trans._(
                        "Could not find a dock widget containing: {widget}",
                        deferred=True,
                        widget=widget,
                    )
                )
        else:
            _dw = widget

        if _dw.widget():
            _dw.widget().setParent(None)
        self.main_widow.removeDockWidget(_dw)
        if menu is not None:
            menu.removeAction(_dw.toggleViewAction())

        # Remove dock widget from dictionary
        self._dock_widgets.pop(_dw.name, None)

        # Deleting the dock widget means any references to it will no longer
        # work but it's not really useful anyway, since the inner widget has
        # been removed. and anyway: people should be using add_dock_widget
        # rather than directly using _add_viewer_dock_widget
        _dw.deleteLater()

    def add_function_widget(
        self,
        function,
        *,
        magic_kwargs=None,
        name: str = '',
        area=None,
        allowed_areas=None,
        shortcut=_sentinel,
    ):
        """Turn a function into a dock widget via magicgui.

        Parameters
        ----------
        function : callable
            Function that you want to add.
        magic_kwargs : dict, optional
            Keyword arguments to :func:`magicgui.magicgui` that
            can be used to specify widget.
        name : str, optional
            Name of dock widget to appear in window menu.
        area : str, optional
            Side of the main window to which the new dock widget will be added.
            Must be in {'left', 'right', 'top', 'bottom'}. If not provided the
            default will be determined by the widget.layout, with 'vertical'
            layouts appearing on the right, otherwise on the bottom.
        allowed_areas : list[str], optional
            Areas, relative to main window, that the widget is allowed dock.
            Each item in list must be in {'left', 'right', 'top', 'bottom'}
            By default, only provided areas is allowed.
        shortcut : str, optional
            Keyboard shortcut to appear in dropdown menu.

        Returns
        -------
        dock_widget : QtViewerDockWidget
            `dock_widget` that can pass viewer events.
        """
        from magicgui import magicgui

        if magic_kwargs is None:
            magic_kwargs = {
                'auto_call': False,
                'call_button': "run",
                'layout': 'vertical',
            }

        widget = magicgui(function, **magic_kwargs or {})

        if area is None:
            area = 'right' if str(widget.layout) == 'vertical' else 'bottom'
        if allowed_areas is None:
            allowed_areas = [area]
        if shortcut is not _sentinel:
            return self.add_dock_widget(
                widget,
                name=name or function.__name__.replace('_', ' '),
                area=area,
                allowed_areas=allowed_areas,
                shortcut=shortcut,
            )
        else:
            return self.add_dock_widget(
                widget,
                name=name or function.__name__.replace('_', ' '),
                area=area,
                allowed_areas=allowed_areas,
            )

    def resize(self, width, height):
        """Resize the window.

        Parameters
        ----------
        width : int
            Width in logical pixels.
        height : int
            Height in logical pixels.
        """
        self.main_widow.resize(width, height)

    def set_geometry(self, left, top, width, height):
        """Set the geometry of the widget

        Parameters
        ----------
        left : int
            X coordinate of the upper left border.
        top : int
            Y coordinate of the upper left border.
        width : int
            Width of the rectangle shape of the window.
        height : int
            Height of the rectangle shape of the window.
        """
        self.main_widow.setGeometry(left, top, width, height)

    def geometry(self) -> Tuple[int, int, int, int]:
        """Get the geometry of the widget

        Returns
        -------
        left : int
            X coordinate of the upper left border.
        top : int
            Y coordinate of the upper left border.
        width : int
            Width of the rectangle shape of the window.
        height : int
            Height of the rectangle shape of the window.
        """
        rect = self.main_widow.geometry()
        return rect.left(), rect.top(), rect.width(), rect.height()

    def show(self, *, block=False):
        """Resize, show, and bring forward the window.

        Raises
        ------
        RuntimeError
            If the viewer.window has already been closed and deleted.
        """
        settings = get_settings()
        try:
            self.main_widow.show()
        except (AttributeError, RuntimeError):
            raise RuntimeError(
                trans._(
                    "This viewer has already been closed and deleted. Please create a new one.",
                    deferred=True,
                )
            )

        if settings.application.first_time:
            settings.application.first_time = False
            try:
                self.main_widow.resize(self.main_widow.layout().sizeHint())
            except (AttributeError, RuntimeError):
                raise RuntimeError(
                    trans._(
                        "This viewer has already been closed and deleted. Please create a new one.",
                        deferred=True,
                    )
                )

        # Resize axis labels now that window is shown
        self.viewer_widget.dims._resize_axis_labels()

        # We want to bring the viewer to the front when
        # A) it is our own event loop OR we are running in jupyter
        # B) it is not the first time a QMainWindow is being created

        # `app_name` will be "Root Viewer" iff the application was instantiated in
        # get_app(). isActiveWindow() will be True if it is the second time a
        # main_widow has been created.
        # See #721, #732, #735, #795, #1594
        app_name = QApplication.instance().applicationName()
        if (
            app_name == 'Root Viewer' or in_jupyter()
        ) and self.main_widow.isActiveWindow():
            self.activate()

    def activate(self):
        """Make the viewer the currently active window."""
        self.main_widow.raise_()  # for macOS
        self.main_widow.activateWindow()  # for Windows

    def _update_theme_no_event(self):
        self._update_theme()

    def _update_theme(self, event=None):
        """Update widget color theme."""
        settings = get_settings()
        with contextlib.suppress(AttributeError, RuntimeError):
            if event:
                value = event.value
                self.viewer_widget.viewer.theme = value
                settings.appearance.theme = value
            else:
                value = (
                    get_system_theme()
                    if settings.appearance.theme == "system"
                    else self.viewer_widget.viewer.theme
                )

            self.main_widow.setStyleSheet(get_stylesheet(value))

    def _status_changed(self, event):
        """Update status bar.

        Parameters
        ----------
        event : napari.utils.event.Event
            The napari event that triggered this method.
        """
        if isinstance(event.value, str):
            self._status_bar.setStatusText(event.value)
        else:
            status_info = event.value
            self._status_bar.setStatusText(
                layer_base=status_info['layer_base'],
                source_type=status_info['source_type'],
                plugin=status_info['plugin'],
                coordinates=status_info['coordinates'],
            )

    def _title_changed(self, event):
        """Update window title.

        Parameters
        ----------
        event : napari.utils.event.Event
            The napari event that triggered this method.
        """
        self.main_widow.setWindowTitle(event.value)

    def _help_changed(self, event):
        """Update help message on status bar.

        Parameters
        ----------
        event : napari.utils.event.Event
            The napari event that triggered this method.
        """
        self._status_bar.setHelpText(event.value)

    def _restart(self):
        """Restart the napari application."""
        self.main_widow.restart()

    def _screenshot(
        self, size=None, scale=None, flash=True, canvas_only=False
    ) -> 'QImage':
        """Capture screenshot of the currently displayed viewer.

        Parameters
        ----------
        flash : bool
            Flag to indicate whether flash animation should be shown after
            the screenshot was captured.
        size : tuple (int, int)
            Size (resolution) of the screenshot. By default, the currently displayed size.
            Only used if `canvas_only` is True.
        scale : float
            Scale factor used to increase resolution of canvas for the screenshot. By default, the currently displayed resolution.
            Only used if `canvas_only` is True.
        canvas_only : bool
            If True, screenshot shows only the image display canvas, and
            if False include the napari viewer frame in the screenshot,
            By default, True.

        Returns
        -------
        img : QImage
        """
        from napari._qt.utils import add_flash_animation

        if canvas_only:
            canvas = self.viewer_widget.canvas
            prev_size = canvas.size
            if size is not None:
                if len(size) != 2:
                    raise ValueError(
                        trans._(
                            'screenshot size must be 2 values, got {len_size}',
                            len_size=len(size),
                        )
                    )
                # Scale the requested size to account for HiDPI
                size = tuple(
                    int(dim / self.main_widow.devicePixelRatio())
                    for dim in size
                )
                canvas.size = size[::-1]  # invert x ad y for vispy
            if scale is not None:
                # multiply canvas dimensions by the scale factor to get new size
                canvas.size = tuple(int(dim * scale) for dim in canvas.size)
            try:
                img = self.viewer_widget.canvas.native.grabFramebuffer()
                if flash:
                    add_flash_animation(self.viewer_widget._canvas_overlay)
            finally:
                # make sure we always go back to the right canvas size
                if size is not None or scale is not None:
                    canvas.size = prev_size
        else:
            img = self.main_widow.grab().toImage()
            if flash:
                add_flash_animation(self.main_widow)
        return img

    def screenshot(
        self, path=None, size=None, scale=None, flash=True, canvas_only=False
    ):
        """Take currently displayed viewer and convert to an image array.

        Parameters
        ----------
        path : str
            Filename for saving screenshot image.
        size : tuple (int, int)
            Size (resolution) of the screenshot. By default, the currently displayed size.
            Only used if `canvas_only` is True.
        scale : float
            Scale factor used to increase resolution of canvas for the screenshot. By default, the currently displayed resolution.
            Only used if `canvas_only` is True.
        flash : bool
            Flag to indicate whether flash animation should be shown after
            the screenshot was captured.
        canvas_only : bool
            If True, screenshot shows only the image display canvas, and
            if False include the napari viewer frame in the screenshot,
            By default, True.

        Returns
        -------
        image : array
            Numpy array of type ubyte and shape (h, w, 4). Index [0, 0] is the
            upper-left corner of the rendered region.
        """
        img = QImg2array(self._screenshot(size, scale, flash, canvas_only))
        if path is not None:
            imsave(path, img)  # scikit-image imsave method
        return img

    def clipboard(self, flash=True, canvas_only=False):
        """Copy screenshot of current viewer to the clipboard.

        Parameters
        ----------
        flash : bool
            Flag to indicate whether flash animation should be shown after
            the screenshot was captured.
        canvas_only : bool
            If True, screenshot shows only the image display canvas, and
            if False include the napari viewer frame in the screenshot,
            By default, True.
        """
        img = self._screenshot(flash=flash, canvas_only=canvas_only)
        QApplication.clipboard().setImage(img)

    def _teardown(self):
        """Carry out various teardown tasks such as event disconnection."""
        self._setup_existing_themes(False)
        _themes.events.added.disconnect(self._add_theme)
        _themes.events.removed.disconnect(self._remove_theme)
        self.viewer_widget.viewer.layers.events.disconnect(self.file_menu.update)
        self.main_widow.closeEvent
        for menu in self.file_menu._INSTANCES:
            with contextlib.suppress(RuntimeError):
                menu._destroy()

    def close(self):
        """Close the viewer window and cleanup sub-widgets."""
        # Someone is closing us twice? Only try to delete self.main_widow
        # if we still have one.
        if hasattr(self, 'main_widow'):
            self._teardown()
            self.viewer_widget.close()
            self.main_widow.close()
            del self.main_widow

