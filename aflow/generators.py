"""Documentation and format builders for the latest AFLUX
specification. Since AFLUX is in constant flux, we generate the
documentation and keyword lists dynamically at development time
whenever a new version is released. This happens by parsing the HTML
page that lists all available keywords and then querying the `help`
feature of the AFLOW API for additional information. This is then used
to generate the API documentation automatically.
"""
from six.moves import urllib
def _get_keywords():
    """Returns a list of the currently valid keywords for the AFLUX API.
    """
    from six.moves import urllib
    import json
    urlopen = urllib.request.urlopen
    url = "http://aflowlib.duke.edu/search/API/?schema"
    r = urlopen(url).read().decode("utf-8")
    return json.loads(r)

def _get_kw_help(keyword, metadata):
    """Gets the documentation string and type information, etc. from
    the AFLUX API.

    Args:
        keyword (str): name of the keyword to get help for.
        metadata (dict): key-value pairs describing the keyword's
          metadata in the AFLOW database.

    Returns:
        dict: with key-value pairs returned by AFLUX (if the entry
        exists); otherwise `None`.
    """
    _set_defaults(metadata)

    from aflow.caster import ptype, docstrings
    metadata["ptype"] = ptype(metadata["type"], keyword)
    if keyword in docstrings:
        metadata["customdoc"] = docstrings[keyword]
    
    return metadata

def _set_defaults(d):
    """Adds the default values to the specified dictionary if they don't already
    exist. This includes all the parameters necessary to construct the templates
    for the classes.

    .. note:: This mutates the given dictionary if some of the keys are missing.
    """
    d.setdefault("title", "No schema information available.")
    d.setdefault("inclusion", "unknown")
    d.setdefault("status", "unknown")
    d.setdefault("description", "No description was returned from AFLUX.")
    d.setdefault("type")

def keywords(root=None):
    """Generates a python module file for the :class:`~aflow.entries.Entry` that
    has documented methods for lazy loading of properties from AFLOW database.

    Args:
        root (str): path in which to generate the module files.
    """
    from os import path
    from aflow.utility import reporoot
    if root is None: # pragma: no cover
        entries = path.join(reporoot, "aflow", "entries.py")
        keyword = path.join(reporoot, "aflow", "keywords.py")
    else:
        entries = path.join(root, "entries.py")
        keyword = path.join(root, "keywords.py")

    #Compile a dictionary of all the keywords and their corresponding
    #dictionaries.
    from collections import OrderedDict
    kws = _get_keywords()
    kwdata = OrderedDict()
    for kw in sorted(kws.keys()):
        metadata = kws[kw]
        if kw[0:2] != "__":
            kwdata[kw] = _get_kw_help(kw, metadata)
        
    settings = {
        "keywords": kwdata
    }

    from jinja2 import Environment, PackageLoader
    env = Environment(loader=PackageLoader('aflow', 'templates'),
                      keep_trailing_newline=True)
    
    tentry = env.get_template("entry.py")
    with open(entries, 'w') as f:
        f.write(tentry.render(**settings))

    tkeyword = env.get_template("keywords.py")
    with open(keyword, 'w') as f:
        f.write(tkeyword.render(**settings))
