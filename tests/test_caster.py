"""Additional tests for the caster to ensure full code coverage.
"""
import pytest
from aflow.caster_new import cast
import aflow.keywords_json as KJ
import numpy as np
import itertools


def _all_types_in_list(lst, type):
    """Is every item in the list with the requested type?
    """
    # If numpy array, just compare the dtype
    if isinstance(lst, np.ndarray):
        return lst.dtype == type
    else:
        # assuming lst
        while True:
            try:
                new_lst = list(itertools.chain(*[t if isinstance(t, (tuple, list))
                                                 else [t]
                                                 for t in lst]))
            except TypeError:
                break
            if new_lst == lst:
                break
            else:
                lst = new_lst
        return all([isinstance(l, type) for l in lst])


def test_caster_json():
    """Test the casting from query results to value.
    For each field, the json returned value and string API output are used
       only testing typical fields
    """
    # Return to int value
    assert cast(KJ.natoms, 12) == 12
    assert type(cast(KJ.natoms, "12")) == int

    # Return to float value
    assert type(cast(KJ.density, 4.45821)) == float
    assert type(cast(KJ.density, "4.45821")) == float

    # Should return float instead of int
    assert type(cast(KJ.spin_cell, -0)) == float
    assert type(cast(KJ.spin_cell, "-0")) == float

    # Test scientific notation
    assert cast(KJ.delta_electronic_energy_convergence,
                2.20696e-07) == 2.20696e-7
    assert cast(KJ.delta_electronic_energy_convergence,
                "2.20696e-07") == 2.20696e-7

    # species, should return list of strings
    assert cast(KJ.species, ["Ca", "O", "Si"]) == ["Ca", "O", "Si"]
    assert cast(KJ.species, "Ca,O,Si") == ["Ca", "O", "Si"]

    # Should return list of float instead of int
    assert _all_types_in_list(
        cast(KJ.spinD, [0, -0, -0, -0, -0, 0, 0, -0, 0, 0, 0, -0]), float)
    assert _all_types_in_list(
        cast(KJ.spinD, "0,-0,-0,-0,-0,0,0,-0,0,0,0,-0"), float)

    # species_pp_ZVAL, should return list of int
    assert _all_types_in_list(cast(KJ.species_pp_ZVAL, [11, 5, 9, 6]), int)
    assert _all_types_in_list(cast(KJ.species_pp_ZVAL, "11,5,9,6"), int)

    # some experimental setup
    assert cast(KJ.Wyckoff_letters, "a;c;b") == ["a", "c", "b"]

    pos = [[0, 0, 0],
           [0, 1.93491, 1.93491],
           [1.93491, 0, 1.93491],
           [1.93491, 1.93491, 0],
           [1.93491, 1.93491, 1.93491]]
    pos_string = "0,0,0;0,1.93491,1.93491;1.93491,0,1.93491;1.93491,1.93491,0;1.93491,1.93491,1.93491"

    assert _all_types_in_list(cast(KJ.positions_cartesian, pos), float)
    assert _all_types_in_list(cast(KJ.positions_cartesian, pos), float)
    assert cast(KJ.positions_cartesian, pos).shape == (5, 3)
    assert cast(KJ.positions_cartesian, pos).shape == (5, 3)

    # Fields with no default format or wrong format
    assert type(cast(KJ.ldau_type, 2)) == float
    assert type(cast(KJ.ldau_type, "2")) == float

    # Deprecated fields, no conversion
    assert type(cast(KJ.stoich, "0.2000 0.2000 0.6000")) == str
    assert type(cast(KJ.kpoints,
                     r"11,11,11;13,13,13;\Gamma-X,X-M,M-\Gamma,\Gamma-R,R-X,M-R;20")) == str
