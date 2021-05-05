"""All keywords from the AAPI-schema that comes with AFLOW engine
"""
import aflow
from aflow.msg import warn
import json
from pathlib import Path
import requests
import types
from copy import deepcopy

from aflow.keywords import Keyword

api_folder = Path(aflow.__file__).parent / "api"
schema_file = api_folder / "aapi-schema.json"

def download_schema():
    url = "http://aflow.org/API/aapi-schema"
    warn("AAPI-SCHEMA file not found. Download from {:s}".format(url))
    req = requests.get(url)
    req.encoding = "utf-8"
    # No error check for the moment
    json_dict = json.loads(req.text)
    return json_dict

# Parse the current schema file from aflow
# if it does not exist for some reason
# download from AFLOWLIB
if schema_file.is_file():
    try:
        with open(schema_file, "r") as fd:
            aapi_schema = json.load(fd)
    except Exception:
        aapi_schema = download_schema()
else:
    aapi_schema = download_schema()

def _construct_docstring(dic):
    """Construct a simple doc string from fields in the dictionary
    """
    dic = deepcopy(dic)         # avoid deletion in the original dictionary
    exclude_fields = ["__comment__", "status", "verification"]
    docstring = []
    docstring.append(dic.pop("title", "").capitalize())
    docstring.append(dic.pop("description", ""))
    docstring.append("")
    for key, value in dic.items():
        if key not in exclude_fields:
            docstring.append(f"{key}:\t{value}")

    return "\n".join(docstring) 

def dynamic_class_creation(name, base=object):
    """Dynamically create keyword classes using the 
       JSON schema provided by AFLOW
    """
    # Protected name in the schema
    if name in ["__schema^2__", ]:
        return None
    schema_entry = aapi_schema["AAPI_schema"][name]
    helper_string = _construct_docstring(schema_entry)
    new_class = type(name,
                     (base,),
                     dict(__doc__=helper_string)
                     )
    return new_class
    
# Dynamically create keywords classes based on the name
for name in aapi_schema["AAPI_schema"].keys():
    new_class = dynamic_class_creation(name)
    if new_class is not None:
        vars()[name] = new_class


