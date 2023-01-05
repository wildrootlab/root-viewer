from __future__ import annotations

import os
import sys
from warnings import warn

from qtpy import PYQT5
from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication

try:
    from root_viewer import __version__
except ImportError:
    __version__ = "unknown"
from napari import Viewer
from napari.utils.translations import trans

from root_viewer.backend._qt.qt_event_filters import QtToolTipEventFilter
from root_viewer.backend._qt.utils import _maybe_allow_interrupt
from root_viewer.backend.utils.notifications import notification_manager

ICON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "icons", "logo_light.png"
)
APP_ID = f"Root Viewer.{__version__}"
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

_defaults = {
    "app_name": "Root Viewer",
    "app_version": __version__,
    "icon": ICON_PATH,
    "org_name": "Root Lab",
    "org_domain": "https://www.root-lab.org/",
    "app_id": APP_ID,
}


# store reference to QApplication to prevent garbage collection
_app_ref = None
_IPYTHON_WAS_HERE_FIRST = "IPython" in sys.modules


def get_app(
    *,
    app_name: str = None,
    app_version: str = None,
    icon: str = None,
    org_name: str = None,
    org_domain: str = None,
    app_id: str = None,
    ipy_interactive: bool = None,
) -> QApplication:
    """Get or create the Qt QApplication.

    There is only one global QApplication instance, which can be retrieved by
    calling get_app again, (or by using QApplication.instance())

    Parameters
    ----------
    app_name : str, optional
        Set app name (if creating for the first time), by default 'Root Viewer'
    app_version : str, optional
        Set app version (if creating for the first time), by default __version__
    icon : str, optional
        Set app icon (if creating for the first time), by default
        ICON_PATH
    org_name : str, optional
        Set organization name (if creating for the first time), by default
        'Root-'
    org_domain : str, optional
        Set organization domain (if creating for the first time), by default
        'https://www.root-lab.org/'
    app_id : str, optional
        Set organization domain (if creating for the first time).  Will be
        passed to set_app_id (which may also be called independently), by
        default APP_ID
    ipy_interactive : bool, optional
        Use the IPython Qt event loop ('%gui qt' magic) if running in an
        interactive IPython terminal.

    Returns
    -------
    QApplication
        [description]

    """
    # Root Viewer defaults are all-or nothing.  If any of the keywords are used
    # then they are all used.
    set_values = {k for k, v in locals().items() if v}
    kwargs = locals() if set_values else _defaults
    global _app_ref

    app = QApplication(sys.argv)

    if app:
        set_values.discard("ipy_interactive")
        if set_values:

            warn(
                trans._(
                    "QApplication already existed, these arguments to to 'get_app' were ignored: {args}",
                    deferred=True,
                    args=set_values,
                )
            )
    else:
        # automatically determine monitor DPI.
        # Note: this MUST be set before the QApplication is instantiated
        if PYQT5:
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

        argv = sys.argv.copy()
        if sys.platform == "darwin" and not argv[0].endswith("Root Viewer"):
            # Make sure the app name in the Application menu is `Root Viewer`
            # which is taken from the basename of sys.argv[0]; we use
            # a copy so the original value is still available at sys.argv
            argv[0] = "Root Viewer"

        app = QApplication(argv)

        # if this is the first time the Qt app is being instantiated, we set
        # the name and metadata
        app.setApplicationName(kwargs.get("app_name"))
        app.setApplicationVersion(kwargs.get("app_version"))
        app.setOrganizationName(kwargs.get("org_name"))
        app.setOrganizationDomain(kwargs.get("org_domain"))

        # Intercept tooltip events in order to convert all text to rich text
        # to allow for text wrapping of tooltips
        app.installEventFilter(QtToolTipEventFilter())

    if app.windowIcon().isNull():
        app.setWindowIcon(QIcon(kwargs.get("icon")))

    if _IPYTHON_WAS_HERE_FIRST:
        _try_enable_ipython_gui("qt" if ipy_interactive else None)

    _app_ref = app  # prevent garbage collection

    # Add the dispatcher attribute to the application to be able to dispatch
    # notifications coming from threads

    return app


def quit_app():
    """Close all windows and quit the QApplication if Root Viewer started it."""
    for v in list(Viewer._instances):
        v.close()
    QApplication.closeAllWindows()
    # if we started the application then the app will be named 'Root Viewer'.
    if QApplication.applicationName() == "Root Viewer" and not _ipython_has_eventloop():
        QApplication.quit()

    # otherwise, something else created the QApp before us (such as
    # %gui qt IPython magic).  If we quit the app in this case, then
    # *later* attempts to instantiate a Root Viewer viewer won't work until
    # the event loop is restarted with app.exec_().  So rather than
    # quit just close all the windows (and clear our app icon).
    else:
        QApplication.setWindowIcon(QIcon())


def _ipython_has_eventloop() -> bool:
    """Return True if IPython %gui qt is active.

    Using this is better than checking ``QApp.thread().loopLevel() > 0``,
    because IPython starts and stops the event loop continuously to accept code
    at the prompt.  So it will likely "appear" like there is no event loop
    running, but we still don't need to start one.
    """
    ipy_module = sys.modules.get("IPython")
    if not ipy_module:
        return False

    shell: InteractiveShell = ipy_module.get_ipython()  # type: ignore
    if not shell:
        return False

    return shell.active_eventloop == "qt"


def _pycharm_has_eventloop(app: QApplication) -> bool:
    """Return true if running in PyCharm and eventloop is active.

    Explicit checking is necessary because PyCharm runs a custom interactive
    shell which overrides `InteractiveShell.enable_gui()`, breaking some
    superclass behaviour.
    """
    in_pycharm = "PYCHARM_HOSTED" in os.environ
    in_event_loop = getattr(app, "_in_event_loop", False)
    return in_pycharm and in_event_loop


def _try_enable_ipython_gui(gui="qt"):
    """Start %gui qt the eventloop."""
    ipy_module = sys.modules.get("IPython")
    if not ipy_module:
        return

    shell: InteractiveShell = ipy_module.get_ipython()  # type: ignore
    if not shell:
        return
    if shell.active_eventloop != gui:
        shell.enable_gui(gui)


def run(*, force=False, gui_exceptions=False, max_loop_level=1, _func_name="run"):
    """Start the Qt Event Loop

    Parameters
    ----------
    force : bool, optional
        Force the application event_loop to start, even if there are no top
        level widgets to show.
    gui_exceptions : bool, optional
        Whether to show uncaught exceptions in the GUI. By default they will be
        shown in the console that launched the event loop.
    max_loop_level : int, optional
        The maximum allowable "loop level" for the execution thread.  Every
        time `QApplication.exec_()` is called, Qt enters the event loop,
        increments app.thread().loopLevel(), and waits until exit() is called.
        This function will prevent calling `exec_()` if the application already
        has at least ``max_loop_level`` event loops running.  By default, 1.
    _func_name : str, optional
        name of calling function, by default 'run'.  This is only here to
        provide functions like `gui_qt` a way to inject their name into the
        warning message.

    Raises
    ------
    RuntimeError
        (To avoid confusion) if no widgets would be shown upon starting the
        event loop.
    """
    if _ipython_has_eventloop():
        # If %gui qt is active, we don't need to block again.
        return

    app = QApplication.instance()

    if _pycharm_has_eventloop(app):
        # explicit check for PyCharm pydev console
        return

    if not app:
        raise RuntimeError(
            trans._(
                "No Qt app has been created. One can be created by calling `get_app()` or `qtpy.QtWidgets.QApplication([])`",
                deferred=True,
            )
        )
    if not app.topLevelWidgets() and not force:
        warn(
            trans._(
                "Refusing to run a QApplication with no topLevelWidgets. To run the app anyway, use `{_func_name}(force=True)`",
                deferred=True,
                _func_name=_func_name,
            )
        )
        return

    if app.thread().loopLevel() >= max_loop_level:
        loops = app.thread().loopLevel()
        warn(
            trans._n(
                "A QApplication is already running with 1 event loop. To enter *another* event loop, use `{_func_name}(max_loop_level={max_loop_level})`",
                "A QApplication is already running with {n} event loops. To enter *another* event loop, use `{_func_name}(max_loop_level={max_loop_level})`",
                n=loops,
                deferred=True,
                _func_name=_func_name,
                max_loop_level=loops + 1,
            )
        )
        return
    with notification_manager, _maybe_allow_interrupt(app):
        app.exec_()
