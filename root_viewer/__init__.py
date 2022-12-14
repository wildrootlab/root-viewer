import os

_true = set(("y", "yes", "t", "true", "on", "1"))
DEBUG = os.environ.get("DEBUG", "").lower() in _true
NOPERSIST = os.environ.get("NOPERSIST", "").lower() in _true
NOTHREADS = os.environ.get("NOTHREADS", "").lower() in _true

del os, _true