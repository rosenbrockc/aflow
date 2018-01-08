"""Tests execution of the search API to retrieve results.
"""
import pytest

def test_len(paper):
    """Tests the code to get the length of a query.
    """
    assert paper.N > 900

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

def test_Si():
    """Tests a query for silicon prototypes from ICSD.
    """
    import aflow
    from aflow import K
    Si = aflow.search(catalog="icsd").filter(K.species == 'Si'
         ).select(K.positions_cartesian).exclude(K.Egap)

    #We purposefully request across a paging boundary to make sure
    #there is continuity.
    for i, entry in enumerate(Si[90:110]):
        assert "ICSD" in entry.aurl

    #Now, get a single item in a set that we haven't queried yet.
    assert "ICSD" in Si[220].aurl

    #Make sure that the finalization actually works.
    N = len(Si.filters)
    assert Si.filter(K.Egap > 3) is Si
    assert len(Si.filters) == N

def test_ordering():
    """Tests a live query with ordering.
    """
    import aflow
    import aflow.keywords as kw
    result = aflow.search(batch_size=20
        ).select(kw.agl_thermal_conductivity_300K
        ).filter(kw.Egap > 6).orderby(kw.agl_thermal_conductivity_300K, True)
    assert len(result[80].aurl) > 0
