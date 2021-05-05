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
                new_lst = list(itertools.chain(*[t if isinstance(t, (tuple, list)) \
                                                    else [t] \
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
    # species
    assert cast(KJ.species, ["Ca", "O", "Si"]) == ["Ca", "O", "Si"]
    # print(cast(KJ.species, "Ca,O,Si"), type(cast(KJ.species, "Ca,O,Si")))
    assert cast(KJ.species, "Ca,O,Si") == ["Ca", "O", "Si"]

    assert _all_types_in_list(cast(KJ.species_pp_ZVAL, "11,5,9,6"), int)
    assert _all_types_in_list(cast(KJ.species_pp_ZVAL, [11,5,9,6]), int)
    # print(cast(KJ.species_pp_ZVAL, [11,5,9,6]))
    # assert cast("numbers", "spinD", None) is None
    # assert cast("numbers", "spinD", "garbage") is None
    # assert cast("numbers", "ldau_TLUJ", "garbage") == {'ldau_params': 'garbage'}
