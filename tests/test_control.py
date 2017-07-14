"""Tests execution of the search API to retrieve results.
"""
import pytest

def test_len(paper):
    """Tests the code to get the length of a query.
    """
    assert len(paper) > 900

def test_iter(paper):
    """Tests the iterator over individual results in the search
    response. Includes testing the slicing behavior.
    """
    for i, entry in enumerate(paper):
        key = "{} of {}".format(i+1, paper.N)
        if i < 20:
            assert entry.raw == paper.responses[-1][key]
        else:
            assert entry.raw == paper.responses[-2][key]
