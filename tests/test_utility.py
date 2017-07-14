"""Tests utility functions.
"""
import pytest
from os import path
def test_reporoot():
    """Tests the absolute path to the reporoot.
    """
    from os import path
    tests = path.abspath(__file__)
    repo = path.dirname(path.dirname(tests))
    
    from aflow.utility import reporoot
    assert reporoot == repo
    
def test_load_module():
    """Makes sure that an arbitrary code module can be loaded.
    """
    from aflow.utility import load_module, reporoot
    base = load_module("base", path.join(reporoot, "aflow", "base.py"))
    assert hasattr(base, "exhandler")
