from typing import ClassVar, List
from weakref import WeakSet

from root_viewer.backend._qt.qt_main_window import Window


class Viewer:
    """The Root Viewer application."""

    _window: "Window" = None
    _instances: ClassVar[List["Viewer"]] = WeakSet()

    def __init__(self) -> None:
        self._instances.add(self)
        self._window = Window()
        self._window.show()

    @property
    def window(self) -> "Window":
        """Return the window."""
        return self._window
