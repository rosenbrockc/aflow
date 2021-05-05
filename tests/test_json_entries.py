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


def _read(filename):
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
    return

def test_all():
    for fname in sample_dir.glob("*.json"):
        print(fname)
        _read(fname)


# def test_query_files(batch=10):
#     """ test on randomly sampled entries
#     """
#     shuffle(raw_entries)
#     for entry in raw_entries[:batch]:
#         aurl = entry["aurl"]
#         print(aurl)
#         # Read the CONTCAR.relax, which should always present
#         afile = AflowFile(aurl, "CONTCAR.relax")
#         assert "CONTCAR.relax" in afile.filename
#         # read the content, watch for HTTP404 error
#         content = afile()
#         print(aurl, content)
    
# def test_aurl_with_colon():
#     """ Test if aurl with colon can be read.
#     """
#     # Series with aurl that contain 0 ~ 3 colons after the edu domain name
#     for ncolon in range(4):
#         shuffle(raw_entries)
#         for entry in raw_entries:
#             aurl = entry["aurl"]
#             # edu:xx --> 2
#             if len(aurl.split(":")) == ncolon + 2:
#                 afile = AflowFile(aurl, "CONTCAR.relax")
#                 assert "CONTCAR.relax" in afile.filename
#                 content = afile()
#                 print(aurl, content)
#                 break
