import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import List, Tuple, Union
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


def deep_update(d, u):
    """Recursively update a dictionary."""
    for k, v in u.items():
        if isinstance(v, Mapping):
            try:
                d[k] = deep_update(d.get(k, {}), v)
            except AttributeError:
                try:
                    d[k] = deep_update(d.__dict__.get(k, {}), v)
                except AttributeError:
                    raise AttributeError(f"Cannot update {k} with {v}")
        else:
            d[k] = v
    return d


def get_user_data_dir(
    appending_paths: Union[str, List[str], Tuple[str, ...]] = None
) -> Path:
    """
    Returns a parent directory path where persistent application data can be stored.
    Can also append additional paths to the return value automatically.
    """
    home = Path.home()
    system_paths = {
        "win32": home / "AppData/Roaming",
        "linux": home / ".local/share",
        "darwin": home / "Library/Application Support",
    }

    if sys.platform not in system_paths:
        raise SystemError(
            f'Unknown System Platform: {sys.platform}. Only supports {", ".join(list(system_paths.keys()))}'
        )
    data_path = system_paths[sys.platform]

    if appending_paths:
        if isinstance(appending_paths, str):
            appending_paths = [appending_paths]
        for path in appending_paths:
            data_path = data_path / path

    return data_path
