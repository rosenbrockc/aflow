"""Tests execution of the search API to retrieve results.
"""
import pytest

def test_len(paper):
    """Tests the code to get the length of a query.
    """
    assert len(paper) > 900

def test_iter(paper):
    """Tests the iterator over individual results in the search response.
    """
    for i, entry in enumerate(paper):
        if i < 20:
            key = "{} of {}".format(i+1, paper.N)
            assert entry.raw == paper.responses[-1][key]
        else:
            key = "{} of {}".format(i+1-20, paper.N)
            assert entry.raw == paper.responses[-2][key]
