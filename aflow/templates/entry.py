"""Provides class and methods for abstracting the data from AFLOW into
python.
"""
from aflow.caster import cast
import aflow.keywords as kw

def _val_from_str(attr, value):
    """Retrieves the specified attribute's value, cast to an
    appropriate python type where possible.
    """
    clsname = "_{}".format(attr)
    if hasattr(kw, clsname):
        cls = getattr(kw, clsname)
        atype = getattr(cls, "atype")
        if attr == "kpoints":
            print(atype, attr, value)
        return cast(atype, attr, value)
    else:
        return value

class AflowFile(object):
    """Represents a single file for an entry in AFLOW and allows easy
    access to download it.

    Args:
        aurl (str): URL for the entry in AFLOW.
        filename (str): name of the file.
    """
    def __init__(self, aurl, filename):
        self.aurl = aurl
        self.filename = filename

    def __repr__(self):
        return "AflowFile({0}/{1})".format(self.aurl, self.filename)

    def __call__(self, target=None):
        """Download the file.

        Args:
            target (str): path to the location to save the file. If None, the
              contents of the file are returned as a string.
        """       
        from six.moves import urllib
        urlopen = urllib.request.urlopen
        url = "http://{}/{}".format(self.aurl.replace(':', '/'), self.filename)
        rawresp = urlopen(url).read().decode("utf-8")

        if target is not None:
            from os import path
            tpath = path.abspath(path.expanduser(target))
            with open(tpath, 'w') as f:
                f.write(rawresp)
            return tpath
        else:
            return rawresp
    
class AflowFiles(list):
    """Represents a collection of files for an entry in AFLOW and allows easy
    access to download them.

    Args:
        entry (Entry): database entry object that has a list of the files and
          remote URL for accessing them.
    """
    def __init__(self, entry):
        files = entry._lazy_load("files")
        if files is not None:
            super(AflowFiles, self).extend(files)
        self.aurl = entry._lazy_load("aurl")

    def __getitem__(self, key):
        from six import string_types
        from fnmatch import fnmatch
        if isinstance(key, string_types):
            matches = [f for f in self if fnmatch(f, key)]
            if len(matches) == 1:
                return AflowFile(self.aurl, matches[0])
            else:
                raise KeyError("Pattern matches more than one file.")
        else:
            match = super(AflowFiles, self).__getitem__(key).strip()
            return AflowFile(self.aurl, match)
            
    
class Entry(object):
    """Encapsulates the result of a single material entry in the AFLOW
    database.

    .. note:: Additional keyword values will be loaded lazily as
      requested (using additional HTTP requests). For optimization, it
      is recommended to request *all* known keywords up front.

    Args:
        kwargs (dict): of key-value pairs obtained from the initial
          AFLUX request.

    Attributes:
        attributes (dict): of key-value pairs requested for the given
          material. This will only be identical to the passed in the
          keyword arguments if no additional property requests have been
          made.
        raw (dict): original response dictionary (without any cast
          values).
    """
    def __init__(self, **kwargs):
        self.attributes = {a: _val_from_str(a, v) for a, v in kwargs.items()}
        self.raw = kwargs
        self._atoms = None
        """ase.atoms.Atoms: atoms object for the configuration in the
        database.
        """
        self._files = None
        

    def __str__(self):
        aurl = self.attributes["aurl"].replace(".edu:", ".edu/")
        return "http://" + aurl
    def __eq__(self, other):
        return self.auid == other.auid
    def __hash__(self):
        return hash(self.auid)

    def _lazy_load(self, keyword):
        """Loads the value of the specified keyword via HTTP request against the
        AFLUX API, if it isn't already present on the object.

        Args:
            keyword (str): name of the keyword to retrieve for this entry.
        """
        if keyword in self.attributes:
            return self.attributes[keyword]
        else:
            import requests
            import json
            aurl = self.attributes["aurl"].replace(".edu:", ".edu/")
            url = "http://{0}?{1}".format(aurl, keyword)
            r = requests.get(url)

            if len(r.text) == 0:
                return

            #We need to coerce the string returned from aflow into the
            #appropriate python format.
            result = _val_from_str(keyword, r.text)
            self.attributes[keyword] = result
            return result

    def atoms(self, pattern="CONTCAR.relax*", quippy=False, keywords=None,
              calculator=None):
        """Creates a :class:`ase.atoms.Atoms` or a :class:`quippy.atoms.Atoms`
        object for this database entry.

        Args:
            pattern (str): pattern for choosing the file to generate the atomic
              lattice and positions from. The pattern is passed to
              :func:`~fnmatch.fnmatch` and the *last* entry in the list is
              returned (so that `CONTCAR.relax2` would be returned
              preferentially over `CONTCAR.relax1` or `CONTCAR.relax`).
            quippy (bool): when True, return a :class:`quippy.atoms.Atoms`
              object.
            keywords (dict): keys are keyword obects accessible from `aflow.K`;
              values are desired `str` names in the parameters dictionary of the
              atoms object.
            calculator (ase.calculators.Calculator): calculator to set for the
              newly created atoms object.

        Examples:
            Generate a :class:`quippy.atoms.Atoms` object and include the total
            energy and forces. Assume that `result` is a valid
            :func:`aflow.search` object.

            >>> entry = result[0] #Get the first result in the set.
            >>> keywords = {K.energy_cell: "dft_energy", K.forces: "dft_force"}
            >>> entry.atoms(quippy=True, keywords=keywords)
        """
        if self._atoms is not None:
            return self._atoms
        
        from fnmatch import fnmatch
        target = [f for f in self.files if fnmatch(f, pattern)][-1]
        aurl = self.attributes["aurl"].replace(".edu:", ".edu/")
        url = "http://{0}/{1}".format(aurl, target)

        import requests
        lines = requests.get(url).text.split('\n')
        preline = ' '.join(self.species).strip() + ' !'
        lines[0] = preline + lines[0]
        contcar = '\n'.join(lines)

        if quippy:# pragma: no cover
            import quippy
            reader = quippy.io.read
        else:
            from ase.io import read
            reader = read

        from six import StringIO
        cfile = StringIO(contcar)
        try:
            self._atoms = reader(cfile, format="vasp")
        finally:
            cfile.close()

        if calculator is not None:
            self._atoms.set_calculator(calculator)
        if keywords is None:
            return self._atoms

        self._atoms.results = {}
        for kw, pname in keywords.items():
            value = getattr(self, kw.name)
            if quippy: # pragma: no cover
                self._atoms.params.set_value(pname, value)
            else:
                #ASE only cares about certain values, but we'll save
                #them all anyway.
                self._atoms.results[pname] = value

        return self._atoms

    @property
    def files(self):
        if self._files is None:
            self._files = AflowFiles(self)
        return self._files
    
    {% for keyword, metadata in keywords.items() %}
    {%- if keyword != "files" %}
    @property
    def {{keyword}}(self):
        """{{metadata.title}} (`{{metadata.inclusion}}`). Units: `{{metadata.units}}`.
        
        {% if metadata.status != "production" -%}
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.

        {%- endif %}
        {% if "verification" in metadata -%}
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          {% for verify in metadata.verification %}
          - :meth:`{{verify}}`
          {%- endfor %}

        {%- endif %}

        Returns:
            {{metadata.ptype}}: {{metadata.description|indent(12, False)}}
        {% if "example" in metadata %}
        Examples:
            You can expect the *content* of the result to be something like:

            `{{metadata.example}}`
        {% endif -%}
        """
        return self._lazy_load("{{keyword}}")
    {%- endif %}
    {% endfor %}
