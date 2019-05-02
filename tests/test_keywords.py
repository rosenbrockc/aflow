"""Tests the behavior of the keywords with each of the different
operators supported by the AFLUX standard.
"""
from aflow import K
import pytest

def test_reset():
    """Tests the test resetting.
    """
    from aflow.keywords import reset
    reset()
    k = (K.Egap > 6) & (K.species % 'Ba')

    assert len(K.Egap.cache) > 0
    assert len(K.species.cache) > 0
    assert len(k.state) > 0

    reset()
    assert len(K.Egap.cache) == 0
    assert len(K.species.cache) == 0

def test_load():
    """Tests keyword loading into dict
    """
    from aflow.keywords import load
    kws_from_module = K.__dict__
    loaded_kws = dict()
    load(loaded_kws)

    for kw, obj in loaded_kws.items():
        assert kw in kws_from_module
        assert obj is kws_from_module[kw]

def test_operators():
    """Tests operators and combinations of operators and the query
    strings that they produce relative to the AFLUX standard.
    """
    from aflow.keywords import reset
    reset()

    k0 = (K.Egap > 6) & (K.PV_cell < 13)
    assert str(k0) == 'Egap(!*6),PV_cell(!13*)'
    assert str(K.Egap) == 'Egap(!*6)'
    assert str(K.PV_cell) == 'PV_cell(!13*)'

    reset()

    from aflow.keywords import reset
    k1 = (K.Egap >= 6) & (K.PV_cell <= 13)
    assert str(k1) == 'Egap(6*),PV_cell(*13)'
    assert str(K.Egap) == 'Egap(6*)'
    assert str(K.PV_cell) == 'PV_cell(*13)'

    reset()

    from aflow.keywords import reset
    k2 = (K.Egap == 6) & (K.PV_cell == 13)
    assert str(k2) == 'Egap(6),PV_cell(13)'
    assert str(K.Egap) == 'Egap(6)'
    assert str(K.PV_cell) == 'PV_cell(13)'

    reset()

    from aflow.keywords import reset
    k3 = (K.Egap == 6) & (K.PV_cell != 13)
    assert str(k3) == 'Egap(6),PV_cell(!13)'
    assert str(K.Egap) == 'Egap(6)'
    assert str(K.PV_cell) == 'PV_cell(!13)'

    k4 = (K.data_source == 'aflowlib') | (K.species % 'Si')
    assert str(k4) == "data_source('aflow'):species(*'Si'*)"
    assert str(K.data_source) == "data_source('aflow')"
    assert str(K.species) == "species(*'Si'*)"

    reset()

    k5 = (K.data_source > 'aflow') & (K.species < 'Ag')
    assert str(k5) == "data_source('aflow'*),species(*'Ag')"
    assert str(K.data_source) == "data_source('aflow'*)"
    assert str(K.species) == "species(*'Ag')"

def test_invert():
    """Tests inversion (i.e., negation) of an operator.
    """
    from aflow.keywords import reset
    reset()

    k0 = (K.Egap > 6) & (K.PV_cell < 13)
    kn0 = ~k0
    assert str(kn0) == 'Egap(*6),PV_cell(13*)'
    assert str(~K.Egap) == 'Egap(*6)'
    assert str(~K.PV_cell) == 'PV_cell(13*)'

    #Now invert everybody back again and see if it is good.
    assert str(~kn0) == 'Egap(!*6),PV_cell(!13*)'
    assert str(~K.Egap) == 'Egap(!*6)'
    assert str(~K.PV_cell) == 'PV_cell(!13*)'

    reset()

    k1 = (K.Egap >= 6) & (K.PV_cell <= 13)
    kn1 = ~k1
    assert str(kn1) == 'Egap(!6*),PV_cell(!*13)'
    assert str(~K.Egap) == 'Egap(!6*)'
    assert str(~K.PV_cell) == 'PV_cell(!*13)'

    # Now invert everybody back again and see if it is good.
    assert str(~kn1) == 'Egap(6*),PV_cell(*13)'
    assert str(~K.Egap) == 'Egap(6*)'
    assert str(~K.PV_cell) == 'PV_cell(*13)'

    reset()

    k2 = (K.Egap == 6) & (K.PV_cell != 13)
    kn2 = ~k2
    assert str(kn2) == 'Egap(!6),PV_cell(13)'
    assert str(~K.Egap) == 'Egap(!6)'
    assert str(~K.PV_cell) == 'PV_cell(13)'

    # Now invert everybody back again and see if it is good.
    assert str(~kn2) == 'Egap(6),PV_cell(!13)'
    assert str(~K.Egap) == 'Egap(6)'
    assert str(~K.PV_cell) == 'PV_cell(!13)'

def test_self():
    """Tests combinations of multiple conditions against the same
    keyword.
    """
    from aflow.keywords import reset
    reset()
    k0 = ((K.Egap > 6) | (K.Egap < 21)) & (K.PV_cell < 13)
    assert str(k0) == 'Egap(!*6:!21*),PV_cell(!13*)'

    reset()
    k1 = ((K.Egap > 6) | (K.Egap < 21)) & ((K.PV_cell < 13) | (K.PV_cell > 2))
    assert str(k1) == 'Egap(!*6:!21*),PV_cell(!13*:!*2)'
    assert str(K.Egap) == 'Egap(!*6:!21*)'
    assert str(K.PV_cell) == 'PV_cell(!13*:!*2)'

    reset()
    k2 = ((K.Egap > 0) & (K.Egap < 2)) | ((K.Egap > 5) | (K.Egap < 7))
    assert str(k2) == 'Egap((!*0,!2*):(!*5:!7*))'
    assert len(K.Egap.cache) == 0
    assert len(K.Egap.state) == 1

    reset()
    k3 = ((K.Egap > 0) & (K.Egap < 2)) | (K.Egap == 5)
    assert str(k2) == 'Egap(5:(!*0,!2*))'

    reset()
    k4 = ((K.Egap >= 6) | (K.Egap <= 21)) & (K.PV_cell <= 13)
    assert str(k4) == 'Egap(6*:*21),PV_cell(*13)'

    reset()
    k5 = ((K.Egap >= 6) | (K.Egap <= 21)) & ((K.PV_cell <= 13) | (K.PV_cell >= 2))
    assert str(k5) == 'Egap(6*:*21),PV_cell(*13:2*)'
    assert str(K.Egap) == 'Egap(6*:*21)'
    assert str(K.PV_cell) == 'PV_cell(*13:2*)'

    reset()
    k6 = ((K.Egap >= 0) & (K.Egap <= 2)) | ((K.Egap >= 5) | (K.Egap <= 7))
    assert str(k6) == 'Egap((0*,*2):(5*:*7))'
    assert len(K.Egap.cache) == 0
    assert len(K.Egap.state) == 1

    reset()
    k7 = ((K.Egap >= 0) & (K.Egap <= 2)) | (K.Egap != 5)
    assert str(k7) == 'Egap(!5:(0*,*2))'

def test_corner():
    """Tests corner cases that aren't part of the previous tests.
    """
    from aflow.keywords import reset
    assert str(K.geometry) == "geometry"
    reset()
    k = (K.Egap > 0)
    with pytest.raises(ValueError):
        k3 = ((K.Egap < 2) | (K.Egap == 5))
