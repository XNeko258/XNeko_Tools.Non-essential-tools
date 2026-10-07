"""Bundled dependency loader for the music player module."""

import os
import sys
import importlib


_LIBS_DIR = os.path.join(os.path.dirname(__file__), '_libs')

_REQUIRED_LIBS = ('mutagen',)


def ensure_dependencies():
    if not os.path.isdir(_LIBS_DIR):
        print(f"[Music Player] Bundled libs folder not found: {_LIBS_DIR}")
        return False

    if _LIBS_DIR not in sys.path:
        sys.path.insert(0, _LIBS_DIR)

    return True


def get_install_status():
    status = {}
    for name in _REQUIRED_LIBS:
        try:
            importlib.import_module(name)
            status[name] = True
        except ImportError:
            status[name] = False
    return status