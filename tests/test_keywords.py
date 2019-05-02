"""Tests the behavior of the keywords with each of the different
operators supported by the AFLUX standard.
"""
from aflow.keywords import load
import pytest

def test_reset():
    """Tests the test resetting.
    """
    from aflow.keywords import reset
    load(globals())
    reset()
    k = (Egap > 6) & (species % 'Ba')

    assert len(Egap.cache) > 0
    assert len(species.cache) > 0
    assert len(k.state) > 0

    reset()
    assert len(Egap.cache) == 0
    assert len(species.cache) == 0

def test_operators():
    """Tests operators and combinations of operators and the query
    strings that they produce relative to the AFLUX standard.
    """
    from aflow.keywords import reset
    reset()

    k0 = (Egap > 6) & (PV_cell < 13)
    assert str(k0) == 'Egap(!*6),PV_cell(!13*)'
    assert str(Egap) == 'Egap(!*6)'
    assert str(PV_cell) == 'PV_cell(!13*)'

    reset()

    from aflow.keywords import reset
    k1 = (Egap >= 6) & (PV_cell <= 13)
    assert str(k1) == 'Egap(6*),PV_cell(*13)'
    assert str(Egap) == 'Egap(6*)'
    assert str(PV_cell) == 'PV_cell(*13)'

    reset()

    from aflow.keywords import reset
    k2 = (Egap == 6) & (PV_cell == 13)
    assert str(k2) == 'Egap(6),PV_cell(13)'
    assert str(Egap) == 'Egap(6)'
    assert str(PV_cell) == 'PV_cell(13)'

    reset()

    from aflow.keywords import reset
    k3 = (Egap == 6) & (PV_cell != 13)
    assert str(k3) == 'Egap(6),PV_cell(!13)'
    assert str(Egap) == 'Egap(6)'
    assert str(PV_cell) == 'PV_cell(!13)'

    k4 = (data_source == 'aflow') | (species % 'Si')
    assert str(k4) == "data_source('aflow'):species(*'Si'*)"
    assert str(data_source) == "data_source('aflow')"
    assert str(species) == "species(*'Si'*)"

    reset()

    k5 = (data_source > 'aflow') & (species < 'Ag')
    assert str(k5) == "data_source('aflow'*),species(*'Ag')"
    assert str(data_source) == "data_source('aflow'*)"
    assert str(species) == "species(*'Ag')"

def test_invert():
    """Tests inversion (i.e., negation) of an operator.
    """
    from aflow.keywords import reset
    reset()

    k0 = (Egap > 6) & (PV_cell < 13)
    kn0 = ~k0
    assert str(kn0) == 'Egap(*6),PV_cell(13*)'
    assert str(~Egap) == 'Egap(*6)'
    assert str(~PV_cell) == 'PV_cell(13*)'

    #Now invert everybody back again and see if it is good.
    assert str(~kn0) == 'Egap(!*6),PV_cell(!13*)'
    assert str(~Egap) == 'Egap(!*6)'
    assert str(~PV_cell) == 'PV_cell(!13*)'

    reset()

    k1 = (Egap >= 6) & (PV_cell <= 13)
    kn1 = ~k1
    assert str(kn1) == 'Egap(!6*),PV_cell(!*13)'
    assert str(~Egap) == 'Egap(!6*)'
    assert str(~PV_cell) == 'PV_cell(!*13)'

    # Now invert everybody back again and see if it is good.
    assert str(~kn1) == 'Egap(6*),PV_cell(*13)'
    assert str(~Egap) == 'Egap(6*)'
    assert str(~PV_cell) == 'PV_cell(*13)'

    reset()

    k2 = (Egap == 6) & (PV_cell != 13)
    kn2 = ~k2
    assert str(kn2) == 'Egap(!6),PV_cell(13)'
    assert str(~Egap) == 'Egap(!6)'
    assert str(~PV_cell) == 'PV_cell(13)'

    # Now invert everybody back again and see if it is good.
    assert str(~kn2) == 'Egap(6),PV_cell(!13)'
    assert str(~Egap) == 'Egap(6)'
    assert str(~PV_cell) == 'PV_cell(!13)'
    
def test_self():
    """Tests combinations of multiple conditions against the same
    keyword.
    """
    from aflow.keywords import reset
    reset()
    k0 = ((Egap > 6) | (Egap < 21)) & (PV_cell < 13)
    assert str(k0) == 'Egap(!*6:!21*),PV_cell(!13*)'

    reset()
    k1 = ((Egap > 6) | (Egap < 21)) & ((PV_cell < 13) | (PV_cell > 2))
    assert str(k1) == 'Egap(!*6:!21*),PV_cell(!13*:!*2)'
    assert str(Egap) == 'Egap(!*6:!21*)'
    assert str(PV_cell) == 'PV_cell(!13*:!*2)'

    reset()
    k2 = ((Egap > 0) & (Egap < 2)) | ((Egap > 5) | (Egap < 7))
    assert str(k2) == 'Egap((!*0,!2*):(!*5:!7*))'
    assert len(Egap.cache) == 0
    assert len(Egap.state) == 1

    reset()
    k3 = ((Egap > 0) & (Egap < 2)) | (Egap == 5)
    assert str(k2) == 'Egap(5:(!*0,!2*))'

    reset()
    k4 = ((Egap >= 6) | (Egap <= 21)) & (PV_cell <= 13)
    assert str(k4) == 'Egap(6*:*21),PV_cell(*13)'

    reset()
    k5 = ((Egap >= 6) | (Egap <= 21)) & ((PV_cell <= 13) | (PV_cell >= 2))
    assert str(k5) == 'Egap(6*:*21),PV_cell(*13:2*)'
    assert str(Egap) == 'Egap(6*:*21)'
    assert str(PV_cell) == 'PV_cell(*13:2*)'

    reset()
    k6 = ((Egap >= 0) & (Egap <= 2)) | ((Egap >= 5) | (Egap <= 7))
    assert str(k6) == 'Egap((0*,*2):(5*:*7))'
    assert len(Egap.cache) == 0
    assert len(Egap.state) == 1

    reset()
    k7 = ((Egap >= 0) & (Egap <= 2)) | (Egap != 5)
    assert str(k7) == 'Egap(!5:(0*,*2))'
    
def test_corner():
    """Tests corner cases that aren't part of the previous tests.
    """
    from aflow.keywords import reset
    assert str(geometry) == "geometry"
    reset()
    k = (Egap > 0)
    with pytest.raises(ValueError):
        k3 = ((Egap < 2) | (Egap == 5))
