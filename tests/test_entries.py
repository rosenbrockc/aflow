"""Tests that :class:`aflow.entries.Entry` objects have the correct
attributes and that lazy fetching works correctly.
"""
import pytest
def test_eq_hash(paper):
    """Tests equality and hashing of database entries.
    """
    paper.reset_iter()
    a = paper[0]
    assert a == a
    assert hash(a) == hash(a.auid)
    assert "http://aflowlib.duke.edu/AFLOWDATA" in str(a)

def test_files(paper, tmpdir):
    from aflow.entries import AflowFile
    from os import path, remove
    a = paper[2]
    assert isinstance(a.files, list)
    assert len(a.files) > 0
    assert isinstance(a.files[4], AflowFile)
    contents = a.files[4]()
    assert len(contents) > 20
    first = a.files[4].filename
    target = str(tmpdir.join("files_contcar"))
    a.files[first](target)
    assert path.isfile(target)

    with pytest.raises(KeyError):
        a.files["dummy"]

    a = AflowFile('aflowlib.duke.edu:AFLOWDATA/ICSD_WEB/HEX/Be1O1_ICSD_15620',
                  'EIGENVAL.bands.xz')
    a.__call__()

    target = path.abspath(path.expanduser('EIGENVAL.bands.xz'))
    assert path.isfile(target)
    remove(target)
    target = str(tmpdir.join("eigenval.bz2"))
    a.__call__(target)
    assert path.isfile(target)    
    
def test_atoms(paper):
    # from aflow import K
    import aflow.keywords_json as K
    paper.reset_iter()

    from ase.calculators.lj import LennardJones
    from ase.atoms import Atoms
    LJ = LennardJones()
    kw = {}
    kw[K.energy_cell] = "dft_energy"
    rawentry = paper[2]
    at = rawentry.atoms(keywords=kw, calculator=LJ)

    assert isinstance(at, Atoms)
    assert isinstance(at.get_total_energy(), float)
    assert "dft_energy" in at.results
    assert at.results["dft_energy"] == rawentry.energy_cell

    at0 = rawentry.atoms(keywords=kw, calculator=LJ)
    assert at0 == at

    at2 = paper[2].atoms(calculator=LJ)
    assert not hasattr(at2, "results")
    
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
    assert A.catalog == 'ICSD\n'

    assert B.Egap == 6.6252
    assert B.agl_thermal_conductivity_300K == 7.45279
    assert B.volume_cell == 56.9766
    assert B.catalog == 'ICSD\n'

def test_all():
    """Tests all retrievals for a given entry, including those it
    doesn't have.
    """
    entries = [
        {
            "compound": "Ag2I2",
            "auid": "aflow:008f8da25d4acde9",
            "aurl": "aflowlib.duke.edu:AFLOWDATA/ICSD_WEB/TET/Ag1I1_ICSD_28230",
            "agl_thermal_conductivity_300K": "0.562013",
            "Egap": "1.9774"
        },
        {
            "compound": "Mg1",
            "auid": "aflow:00528d06f69c7b55",
            "aurl": "aflowlib.duke.edu:AFLOWDATA/LIB2_RAW/CeMg_pv/304"
        }
    ]
    from aflow.entries import Entry
    from aflow import list_keywords

    for entry_vals in entries:
        A = Entry(**entry_vals)
        kws = list_keywords()
        kws.append('catalog')
        haskw = A.keywords

        for kw in kws:
            if kw in haskw:
                assert getattr(A, kw) is not None
            else:
                assert getattr(A, kw) is None
