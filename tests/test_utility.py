"""Tests utility functions.
"""
import pytest
def test_reporoot():
    """Tests the absolute path to the reporoot.
    """
    from os import path
    tests = path.abspath(__file__)
    repo = path.dirname(path.dirname(tests))
    
    from aflow.utility import reporoot
    assert reporoot == repo
