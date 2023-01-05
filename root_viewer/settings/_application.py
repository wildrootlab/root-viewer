from typing import Dict, Optional

from root_viewer.settings._base import ConfigFileSettings


class RootViewerSettings(ConfigFileSettings):
    """The BaseSettings for the application."""

    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.dict()})"

    def set_value(self, data: Dict, config: Optional[bool] = False) -> None:
        """Set the settings.
        Parameters
        ----------
        data : Dict
            The data to set.
        config : bool, optional
            If True, set the config data rather then the application data, by default False
        """

        if config:
            self.config.__dict__.update(data)
        else:
            self.__dict__.update(data)
