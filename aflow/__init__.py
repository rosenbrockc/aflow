from aflow.control import search

_keywords = []
"""list of `str` keyword names available in AFLOW.
"""
def list_keywords():
    """Returns a list of all possible keywords available in the AFLOW
    lib.
    """
    global _keywords
    if len(_keywords) == 0:
        from aflow.keywords import Keyword
        import aflow.keywords as kw
        from inspect import getmembers
        
        for name, o in getmembers(kw):
            if isinstance(o, Keyword):
                _keywords.append(name)

    return _keywords

import aflow.keywords as K
