""" Test if manual matchbook can work
"""
import pytest
import json
from pathlib import Path
from random import shuffle
from aflow.control import Query
import numpy as np

def _query_string(string):
    query = Query(batch_size=20).set_manual_matchbook(string)
    assert query.matchbook() == string
    assert len(query) > 0


def test_all():
    query_strings = ["nspecies(2),species('O','Si')",
                     "Egap(1.0*,*1.1)",]
    for string in query_strings:
        _query_string(string)
    # assert len(query) != 0

# sample_dir = Path(__file__).parent / "aflowlib_examples"


# def _read(filename):
#     with open(filename, "r") as fd:
#         raw_entries = json.load(fd)

#     entry = Entry(**raw_entries)
#     # test if Egap can be parsed from null --> None
#     if entry.Egap is not None:
#         assert isinstance(entry.Egap, float)
#     assert isinstance(entry.species, list)
#     # composition should be returned to nd array
#     assert isinstance(entry.composition, np.ndarray)
#     assert isinstance(entry.composition, list) is False

#     # int types
#     assert isinstance(entry.spacegroup_orig, int)

#     # string to plain list
#     assert isinstance(entry.species_pp_version, list)
#     assert isinstance(entry.species, list)
#     return

# def test_all():
#     for fname in sample_dir.glob("*.json"):
#         print(fname)
#         _read(fname)

