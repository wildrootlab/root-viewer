from typing import ClassVar
from weakref import WeakSet
from napari.components.viewer_model import ViewerModel


class Napari(ViewerModel):
    """The Napari application.
    """
    _window: 'Window' = None  # type: ignore
    _instances: ClassVar[WeakSet['Napari']] = WeakSet()
    def __init__(self):
        super().__init__(
            title='Root Viewer',
            ndisplay=2,
            order=(),
            axis_labels=(),
        )
        # we delay initialization of plugin system to the first instantiation
        # of a viewer... rather than just on import of plugins module
        from napari.plugins import _initialize_plugins

        # having this import here makes all of Qt imported lazily, upon
        # instantiating the first Viewer.
        from napari.window import Window

        _initialize_plugins()

        self._window = Window(self, show=False)
        self._instances.add(self)

    # Expose private window publically. This is needed to keep window off pydantic model
    @property
    def window(self) -> 'Window':
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
