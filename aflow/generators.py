"""Documentation and format builders for the latest AFLUX
specification. Since AFLUX is in constant flux, we generate the
documentation and keyword lists dynamically at development time
whenever a new version is released. This happens by parsing the HTML
page that lists all available keywords and then querying the `help`
feature of the AFLOW API for additional information. This is then used
to generate the API documentation automatically.
"""
def _get_keywords():
    """Returns a list of the currently valid keywords for the AFLUX API.
    """
    from bs4 import BeautifulSoup
    import requests
    result = []
    url = "http://aflowlib.duke.edu/aflowwiki/doku.php?id=documentation:all_keywords"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html5lib")
    
    for heading in soup.find_all('h3'):
        if heading.get('id') is not None:
            result.append(heading.text)

    return result

async def _get_kw_help(keyword):
    """Gets the documentation string and type information, etc. from
    the AFLUX API.

    Args:
        keyword (str): name of the keyword to get help for.

    Returns:
        dict: with key-value pairs returned by AFLUX (if the entry
        exists); otherwise `None`.
    """
    import requests
    import json
    result = []
    url = "http://aflowlib.duke.edu/search/API/?schema({0})".format(keyword)
    r = requests.get(url)
    metadata = json.loads(r.text)

    #It is possible that the AFLUX schema request won't return anything for a
    #particular keyword. In this case, we need to supply some generic default
    #values.
    d = {}
    if len(metadata) > 0:
        d = metadata[0]
    _set_defaults(d)

    from aflow.caster import ptype, docstrings
    d["ptype"] = ptype(d["type"], keyword)
    if keyword in docstrings:
        d["customdoc"] = docstrings[keyword]
    
    return d

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

async def keywords():
    """Generates a python module file for the :class:`~aflow.entries.Entry` that
    has documented methods for lazy loading of properties from AFLOW database.
    """
    from os import path
    from aflow.utility import reporoot
    entries = path.join(reporoot, "aflow", "entries.py")
    keyword = path.join(reporoot, "aflow", "keywords.py")

    #Compile a dictionary of all the keywords and their corresponding
    #dictionaries.
    kws = _get_keywords()
    kwdata = {}
    for kw in kws:
        kwdata[kw] = await _get_kw_help(kw)
        
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
