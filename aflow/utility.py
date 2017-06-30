"""Utility functions for interacting with file system, shell, etc.
"""
from os import path
from six import string_types
def _get_reporoot():
    """Returns the absolute path to the repo root directory on the current
    system.
    """
    from os import path
    import aflow
    apath = path.abspath(aflow.__file__)
    return path.dirname(path.dirname(apath))

reporoot = _get_reporoot()
"""The absolute path to the repo root on the local machine.
"""
