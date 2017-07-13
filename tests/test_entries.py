"""Tests that :class:`aflow.entries.Entry` objects have the correct
attributes and that lazy fetching works correctly.
"""
def test_corner():
    """Tests corner cases in the module that aren't raised during
    normal use.
    """
    from aflow.entries import _val_from_str
    assert _val_from_str("dummy", 22) == 22
    
def test_fetched(paper):
    """Makes sure that the attributes included in the original query
    are returned correctly.
    """
    paper.reset_iter()
    for i, entry in enumerate(paper):
        assert isinstance(entry.Egap, float)
        assert isinstance(entry.agl_thermal_conductivity_300K, float)
    
def test_lazy():
    """Tests lazy retrieval of entry attributes.
    """
    a = {
        "compound": "Be2O2",
        "auid":"aflow:ed51b7b3938f117f",
        "aurl":"aflowlib.duke.edu:AFLOWDATA/ICSD_WEB/HEX/Be1O1_ICSD_15620",
        "agl_thermal_conductivity_300K":"53.361",
        "Egap":"7.4494"
    }
    b = {
        "compound":"B1H4Na1",
        "auid":"aflow:3a531e5b3aa9205e",
        "aurl":"aflowlib.duke.edu:AFLOWDATA/ICSD_WEB/FCC/B1H4Na1_ICSD_165835",
        "agl_thermal_conductivity_300K":"7.45279",
        "Egap":"6.6252"
    }
    from aflow.entries import Entry
    A = Entry(**a)
    B = Entry(**b)

    assert A.Egap == 7.4494
    assert A.agl_thermal_conductivity_300K == 53.361
    assert A.energy_atom == -7.10342

    assert B.Egap == 6.6252
    assert B.agl_thermal_conductivity_300K == 7.45279
    assert B.volume_cell == 56.9766

def test_all():
    """Tests all retrievals for a given entry, including those it
    doesn't have.
    """
    a = {
        "compound": "Be2O2",
        "auid":"aflow:ed51b7b3938f117f",
        "aurl":"aflowlib.duke.edu:AFLOWDATA/ICSD_WEB/HEX/Be1O1_ICSD_15620",
        "agl_thermal_conductivity_300K":"53.361",
        "Egap":"7.4494"
    }
    from aflow.entries import Entry
    A = Entry(**a)

    from aflow import list_keywords
    kws = list_keywords()
    haskw = A.keywords
    
    for kw in kws:
        if kw in haskw:
            assert getattr(A, kw) is not None
        else:
            assert getattr(A, kw) is None
