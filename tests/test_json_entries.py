"""Read entries from AFLOW example json files 
"""
"""Test the fetching for AflowFile works
"""
import pytest
import json
from pathlib import Path
from random import shuffle
from aflow.entries import Entry
import numpy as np

sample_dir = Path(__file__).parent / "aflowlib_examples"


def _read_json(filename):
    with open(filename, "r") as fd:
        raw_entries = json.load(fd)

    entry = Entry(**raw_entries)
    # test if Egap can be parsed from null --> None
    if entry.Egap is not None:
        assert isinstance(entry.Egap, float)
    assert isinstance(entry.species, list)
    # composition should be returned to nd array
    assert isinstance(entry.composition, np.ndarray)
    assert isinstance(entry.composition, list) is False

    # int types
    assert isinstance(entry.spacegroup_orig, int)

    # string to plain list
    assert isinstance(entry.species_pp_version, list)
    assert isinstance(entry.species, list)
    return

def test_all():
    for fname in sample_dir.glob("*.json"):
        print(fname)
        _read_json(fname)

