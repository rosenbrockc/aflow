"""Test the fetching for AflowFile works
"""
import pytest
import json
from pathlib import Path
from random import shuffle
from aflow.entries import Entry, AflowFile, AflowFiles

curdir = Path(__file__).parent

# Load big json query 
with open(curdir / "data_big.json", "r") as fd:
    raw_entries = json.load(fd)
    # convert raw_entries to list and do a random shuffle
    raw_entries = list(raw_entries.values())

def test_query_files(batch=10):
    """ test on randomly sampled entries
    """
    shuffle(raw_entries)
    for entry in raw_entries[:batch]:
        aurl = entry["aurl"]
        print(aurl)
        # Read the CONTCAR.relax, which should always present
        afile = AflowFile(aurl, "CONTCAR.relax")
        assert "CONTCAR.relax" in afile.filename
        # read the content, watch for HTTP404 error
        content = afile()
        print(aurl, content)
    
def test_aurl_with_colon():
    """ Test if aurl with colon can be read.
    """
    # Series with aurl that contain 0 ~ 3 colons after the edu domain name
    for ncolon in range(4):
        shuffle(raw_entries)
        for entry in raw_entries:
            aurl = entry["aurl"]
            # edu:xx --> 2
            if len(aurl.split(":")) == ncolon + 2:
                afile = AflowFile(aurl, "CONTCAR.relax")
                assert "CONTCAR.relax" in afile.filename
                content = afile()
                print(aurl, content)
                break
