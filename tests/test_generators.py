"""Tests the generators to make sure that they produce valid code and
have all the relevant keywords in them.
"""
import pytest
def test_keywords_entries(tmpdir):
    """Makes sure the generated files have all the relevant contents
    from the keyword templates.
    """
    from aflow.generators import keywords
    keywords(str(tmpdir))

    from aflow.utility import load_module
    modname = "aflow.keywords"
    modpath = str(tmpdir.join("keywords.py"))
    modobj = load_module(modname, modpath)
    
    #If we get here, the module was produced correctly. Grab a list of
    #the keywords and make sure that they are all present.
    from aflow.generators import _get_keywords
    kws = _get_keywords()

    for kw in kws:
        if kw[0:2] == "__":
            continue
        
        assert hasattr(modobj, kw)
        assert issubclass(getattr(modobj, kw).__class__, modobj.Keyword)
        
    modname = "aflow.entries"
    modpath = str(tmpdir.join("entries.py"))
    modobj = load_module(modname, modpath)

    for kw in kws:
        if kw[0:2] == "__":
            continue

        assert hasattr(modobj.Entry, kw)
