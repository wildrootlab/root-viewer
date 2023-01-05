import json
import os
import sys
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)
from uuid import UUID, uuid4

from pydantic import BaseModel, BaseSettings, Field
from pydantic.env_settings import SettingsError

from root_viewer.settings.utils import UUIDEncoder, get_user_data_dir

try:
    from root_viewer._version import __version__
except ImportError:
    __version__ = "UNKNOWN"


if TYPE_CHECKING:
    IntStr = Union[int, str]
    AbstractSetIntStr = AbstractSet[IntStr]
    DictStrAny = Dict[str, Any]
    MappingIntStrAny = Mapping[IntStr, Any]


class Layout(BaseModel):
    """Layout is a pydantic model that represents the application layout.
    Each layout is a dictionary of widgets and their positions. The keys are
    the widget names and the values are the widget positions.

    NOTE: Allowed areas is handeled by the widget placer, not the Layout settings.
    """

    widgets: Dict[str, Dict[str, Any]] = {}

    def __getitem__(self, key: str) -> Dict[str, Any]:
        return self.widgets[key]

    def __setitem__(self, key: str, value: Dict[str, Any]) -> None:
        self.widgets[key] = value

    def __delitem__(self, key: str) -> None:
        del self.widgets[key]

    def __iter__(self) -> Iterable[str]:
        return iter(self.widgets)

    def __len__(self) -> int:
        return len(self.widgets)

    def __contains__(self, key: str) -> bool:
        return key in self.widgets

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.widgets})"


class ApplicationConfig(BaseSettings):
    """ApplicationConfig is a pydantic model that represents the application settings."""

    window_size: Tuple[int, int] = (800, 600)
    window_position: Tuple[int, int] = (0, 0)
    window_maximized: bool = False
    window_fullscreen: bool = False
    window_icon_type: str = "light"
    window_theme: str = "dark"
    window_layout: Layout = Layout()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "forbid"
        allow_mutation = False
        validate_assignment = True
        arbitrary_types_allowed = True
        use_enum_values = True
        json_loads = json.loads
        encoders = {UUID: UUIDEncoder}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.dict()})"

    def update(self, **data: Any) -> None:
        """Update the settings with new data."""
        for key, value in data.items():
            setattr(self, key, value)


class ApplicationInstance(BaseModel):
    """ApplicationInstance is a pydantic model that represents the application instance.
    It is a singleton created when the application is launched. It contains all information
    about the application, such as the name, version, author, and settings.

    """

    id: UUID = Field(default_factory=uuid4)
    name: str = "Root Viewer"
    version: str = __version__
    description: str = "A mutli-dimensional image viewer for neuronal analysis"
    author: str = "Daniel Alas"
    author_email: str = "daniel.alas@colorado.edu"
    url: str = "https://wildrootlab.github.io/root-viewer/intro.html"
    config: ApplicationConfig = None


class ConfigFileSettings(ApplicationInstance):
    """This adds config read/write and yaml support to ApplicationInstance settings."""

    config_file: Optional[Path] = None
    user_data_path: Optional[Path] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        self.user_data_path = get_user_data_dir()
        self.config_file = Path(self.user_data_path, self.name, "config.json")
        self.config = ApplicationConfig()

    def read_config(self):
        """Read the config file and update the settings if it exists."""
        if self.config_file.exists():
            try:
                self.config.__dict__.update(json.load(open(self.config_file)))
            except json.JSONDecodeError:
                # If the config file is corrupted, overwrite it with the default settings.
                self.save_config()
                self.config.__dict__.update(json.load(open(self.config_file)))
        else:
            self.save_config()

    def save_config(self):
        if not self.config_file.parent.exists():
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, "w") as f:
            json.dump(self.config.dict(), f, indent=4)
