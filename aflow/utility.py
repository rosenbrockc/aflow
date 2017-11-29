"""Utility functions for interacting with file system, shell, etc.
"""
from os import path
from six import string_types
import six

def _get_reporoot():
    """Returns the absolute path to the repo root directory on the current
    system.
    """
    from os import path
    import aflow
    apath = path.abspath(aflow.__file__)
    return path.dirname(path.dirname(apath))

def load_module(modname, modpath, search_locs=None):
    """Loads the module specification and returns it as a python object.

    Args:
        modname (str): name that the module should be loaded under.
        modpath (str): full path to the code file in which the module is
          defined.
        search_locs (str): path to search for additional submodules.
    """
    if six.PY2:# pragma: no cover
        import imp
        result = imp.load_source(modname, modpath)
        return result
    else:
        from importlib.util import spec_from_file_location as specff
        from importlib.util import module_from_spec as modfs
        from importlib.machinery import SourceFileLoader
        spec = specff(modname, modpath, submodule_search_locations=search_locs)
        result = modfs(spec)
        spec.loader.exec_module(result)
        return result

reporoot = _get_reporoot()
"""The absolute path to the repo root on the local machine.
"""
