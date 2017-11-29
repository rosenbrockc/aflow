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
    
    @property
    def Bravais_lattice_orig(self):
        """original bravais lattice (`optional`). Units: ``.
        
        
        

        Returns:
            str: Returns the Bravais lattice of the original unrelaxed structure before the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `Bravais_lattice_orig=MCLC`
        """
        return self._lazy_load("Bravais_lattice_orig")
    
    @property
    def Bravais_lattice_relax(self):
        """relaxed bravais lattice (`optional`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`stress_tensor`

        Returns:
            str: Returns the Bravais lattice of the original relaxed structure after the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `Bravais_lattice_relax=MCLC`
        """
        return self._lazy_load("Bravais_lattice_relax")
    
    @property
    def Egap(self):
        """electronic energy band gap (`mandatory`). Units: `eV`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Band gap calculated with the approximations and pseudopotentials described by other keywords.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `Egap=2.5`
        """
        return self._lazy_load("Egap")
    
    @property
    def Egap_fit(self):
        """fitted band gap (`mandatory`). Units: `eV`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Simple cross-validated correction (fit) of Egap.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `Egap_fit=3.5`
        """
        return self._lazy_load("Egap_fit")
    
    @property
    def Egap_type(self):
        """band gap type (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            str: Given a band gap, this keyword describes if the system is a metal, a semi-metal, an insulator with direct or indirect band gap.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `Egap_type=insulator_direct`
        """
        return self._lazy_load("Egap_type")
    
    @property
    def PV_atom(self):
        """atomic pressure*volume (`mandatory`). Units: `eV/atom`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Pressure multiplied by volume of the atom.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `PV_atom=12.13`
        """
        return self._lazy_load("PV_atom")
    
    @property
    def PV_cell(self):
        """unit cell pressure*volume (`mandatory`). Units: `eV`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Pressure multiplied by volume of the unit cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `PV_cell=12.13`
        """
        return self._lazy_load("PV_cell")
    
    @property
    def Pearson_symbol_orig(self):
        """original Pearson symbol (`mandatory`). Units: ``.
        
        
        

        Returns:
            str: Returns the Pearson symbol of the original-unrelaxed structure before the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `Pearson_symbol_orig=mS32`
        """
        return self._lazy_load("Pearson_symbol_orig")
    
    @property
    def Pearson_symbol_relax(self):
        """relaxed Pearson symbol (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`stress_tensor`

        Returns:
            str: Returns the Pearson symbol of the relaxed structure after the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `Pearson_symbol_relax=mS32`
        """
        return self._lazy_load("Pearson_symbol_relax")
    
    @property
    def Pulay_stress(self):
        """Pulay Stress (`mandatory`). Units: `kbar`.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            float: Returns a metric of the basis set inconsistency for the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `pulay_stress=10.0`
        """
        return self._lazy_load("Pulay_stress")
    
    @property
    def Pullay_stress(self):
        """Pulay Stress (`mandatory`). Units: `kbar`.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            float: Returns a metric of the basis set inconsistency for the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `Pullay_stress=10.0`
        """
        return self._lazy_load("Pullay_stress")
    
    @property
    def ael_bulk_modulus_reuss(self):
        """AEL Reuss bulk modulus (`optional`). Units: `GPa`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the bulk modulus as calculated using the Reuss method with AEL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ael_bulk_modulus_reuss=105.315`
        """
        return self._lazy_load("ael_bulk_modulus_reuss")
    
    @property
    def ael_bulk_modulus_voigt(self):
        """AEL Voigt bulk modulus (`optional`). Units: `GPa`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the bulk modulus as calculated using the Voigt method with AEL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ael_bulk_modulus_voiht=105.315`
        """
        return self._lazy_load("ael_bulk_modulus_voigt")
    
    @property
    def ael_bulk_modulus_vrh(self):
        """AEL VRH bulk modulus (`optional`). Units: `GPa`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the bulk modulus as calculated using the Voigt-Reuss-Hill average with AEL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ael_bulk_modulus_vrh=105.315`
        """
        return self._lazy_load("ael_bulk_modulus_vrh")
    
    @property
    def ael_elastic_anistropy(self):
        """AEL elastic anistropy (`optional`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the elastic anistropy as calculated with AEL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ael_elastic_anistropy=0.0008165`
        """
        return self._lazy_load("ael_elastic_anistropy")
    
    @property
    def ael_poisson_ratio(self):
        """AEL Poisson ratio (`optional`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the istropic Poisson ratio as calculated with AEL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ael_poisson_ratio=0.216`
        """
        return self._lazy_load("ael_poisson_ratio")
    
    @property
    def ael_shear_modulus_reuss(self):
        """AEL Reuss shear modulus (`optional`). Units: `GPa`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the shear modulus as calculated using the Reuss method with AEL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ael_shear_modulus_reuss=73.787`
        """
        return self._lazy_load("ael_shear_modulus_reuss")
    
    @property
    def ael_shear_modulus_voigt(self):
        """AEL Voigt shear modulus (`optional`). Units: `GPa`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the shear modulus as calculated using the Voigt method with AEL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ael_shear_modulus_voigt=73.799`
        """
        return self._lazy_load("ael_shear_modulus_voigt")
    
    @property
    def ael_shear_modulus_vrh(self):
        """AEL VRH shear modulus (`optional`). Units: `GPa`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the shear modulus as calculated using the Voigt-Reuss-Hill average with AEL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ael_shear_modulus_vrh=73.793`
        """
        return self._lazy_load("ael_shear_modulus_vrh")
    
    @property
    def aflow_version(self):
        """aflow version (`optional`). Units: ``.
        
        
        

        Returns:
            str: Returns the version number of AFLOW used to perform the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `aflow_version=aflow30641`
        """
        return self._lazy_load("aflow_version")
    
    @property
    def aflowlib_date(self):
        """material generation date (`optional`). Units: ``.
        
        
        

        Returns:
            str: Returns the date of the AFLOW post-processor which generated the entry for the library.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `aflowlib_date=20140204_13:10:39_GMT-5`
        """
        return self._lazy_load("aflowlib_date")
    
    @property
    def aflowlib_entries(self):
        """aflowlib entries (`conditional`). Units: ``.
        
        
        

        Returns:
            list: For projects and set-layer entries, aflowlib_entries lists the available sub-entries which are associated with the $aurl of the subdirectories.  By parsing $aurl/?aflowlib_entries (containing $aurl/aflowlib_entries_number entries) the user finds further locations to interrogate.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `aflowlib_entries=AgAl,AgAs,AgAu,AgB_h,AgBa_sv,AgBe_sv,AgBi_d,AgBr,AgCa_sv,...`
        """
        return self._lazy_load("aflowlib_entries")
    
    @property
    def aflowlib_entries_number(self):
        """aflowlib entry count (`conditional`). Units: ``.
        
        
        

        Returns:
            float: For projects and set-layer entries, aflowlib_entrieslists the available sub-entries which are associated with the $aurl of the subdirectories.  By parsing $aurl/?aflowlib_entries (containing $aurl/aflowlib_entries_number entries) the user finds further locations to interrogate.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `aflowlib_entries_number=654`
        """
        return self._lazy_load("aflowlib_entries_number")
    
    @property
    def aflowlib_version(self):
        """aflowlib version (`optional`). Units: ``.
        
        
        

        Returns:
            str: Returns the version of the AFLOW post-processor which generated the entry for the library.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `aflowlib_version=3.1.103`
        """
        return self._lazy_load("aflowlib_version")
    
    @property
    def agl_acoustic_debye(self):
        """AGL acoustic Debye temperature (`optional`). Units: `K`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the acoustic Debye temperature as calculated with AGL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_acoustic_debye=492`
        """
        return self._lazy_load("agl_acoustic_debye")
    
    @property
    def agl_bulk_modulus_isothermal_300K(self):
        """AGL isothermal bulk modulus 300K (`optional`). Units: `GPa`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the isothermal bulk modulus at 300K as calculated with AGL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_bulk_modulus_isothermal_300K=96.6`
        """
        return self._lazy_load("agl_bulk_modulus_isothermal_300K")
    
    @property
    def agl_bulk_modulus_static_300K(self):
        """AGL static bulk modulus 300K (`optional`). Units: `GPa`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the static bulk modulus at 300K as calculated with AGL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_bulk_modulus_static_300K=99.6`
        """
        return self._lazy_load("agl_bulk_modulus_static_300K")
    
    @property
    def agl_debye(self):
        """AGL Debye temperature (`optional`). Units: `K`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the Debye temperature as calculated with AGL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_debye=620`
        """
        return self._lazy_load("agl_debye")
    
    @property
    def agl_gruneisen(self):
        """AGL Gruneisen parameter (`optional`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the Gruneisen parameter as calculated with AGL.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_gruneisen=2.06`
        """
        return self._lazy_load("agl_gruneisen")
    
    @property
    def agl_heat_capacity_Cp_300K(self):
        """AGL heat capacity Cp (`optional`). Units: `kB/cell`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the heat capacity at constant pressure as calculated with AGL at 300K.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_heat_capacity_Cp_300K=5.502`
        """
        return self._lazy_load("agl_heat_capacity_Cp_300K")
    
    @property
    def agl_heat_capacity_Cv_300K(self):
        """AGL heat capacity Cv (`optional`). Units: `kB/cell`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the heat capacity at constant volume as calculated with AGL at 300K.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_heat_capacity_Cv_300K=4.901`
        """
        return self._lazy_load("agl_heat_capacity_Cv_300K")
    
    @property
    def agl_thermal_conductivity_300K(self):
        """AGL thermal conductivity (`optional`). Units: `W/m*K`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the thermal conductivity as calculated with AGL at 300K.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_thermal_conductivity_300K=24.41`
        """
        return self._lazy_load("agl_thermal_conductivity_300K")
    
    @property
    def agl_thermal_expansion_300K(self):
        """AGL thermal expansion (`optional`). Units: `1/K`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the thermal expansion as calculated with AGL at 300K.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `agl_thermal_expansion_300K=4.997e-05`
        """
        return self._lazy_load("agl_thermal_expansion_300K")
    
    @property
    def auid(self):
        """AFLOWLIB Unique Identifier (`mandatory`). Units: ``.
        
        
        

        Returns:
            str: AFLOWLIB Unique Identifier for the entry, AUID, which can be used as a publishable object identifier.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `auid=aflow:e9c6d914c4b8d9ca`
        """
        return self._lazy_load("auid")
    
    @property
    def aurl(self):
        """AFLOWLIB Uniform Resource Locator (`mandatory`). Units: ``.
        
        
        

        Returns:
            str: AFLOWLIB Uniform Resource Locator returns the AURL of the entry.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `aurl=aflowlib.duke.edu:AFLOWDATA/LIB3_RAW/Bi_dRh_pvTi_sv/T0003.ABC:LDAU2`
        """
        return self._lazy_load("aurl")
    
    @property
    def author(self):
        """author (`optional`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            list: Returns the name (not necessarily an individual) and affiliation associated with authorship of the data.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `author=Marco_Buongiorno_Nardelli,Ohad_Levy,Jesus_Carrete`
        """
        return self._lazy_load("author")
    
    @property
    def bader_atomic_volumes(self):
        """atomic volume per atom (`optional`). Units: `&Aring;<sup>3</sup>`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            list: Returns the volume of each atom of the primitive cell as calculated by the Bader Atoms in Molecules Analysis. This volume encapsulates the electron density associated with each atom above a threshold of 0.0001 electrons.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `bader_atomic_volumes=15.235,12.581,13.009`
        """
        return self._lazy_load("bader_atomic_volumes")
    
    @property
    def bader_net_charges(self):
        """partial charge per atom (`optional`). Units: `electrons`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            list: Returns a comma delimited set of partial charges per atom of the primitive cell as calculated by the Bader Atoms in Molecules Analysis.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `bader_net_charges=0.125,0.125,-0.25`
        """
        return self._lazy_load("bader_net_charges")
    
    @property
    def calculation_cores(self):
        """used CPU cores (`optional`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Number of processors/cores used for the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `calculation_cores=32`
        """
        return self._lazy_load("calculation_cores")
    
    @property
    def calculation_memory(self):
        """used RAM (`optional`). Units: `Megabytes`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: The maximum memory used for the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `calculation_memory=32`
        """
        return self._lazy_load("calculation_memory")
    
    @property
    def calculation_time(self):
        """used time (`optional`). Units: `seconds`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Total time taken for the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `calculation_time=32`
        """
        return self._lazy_load("calculation_time")
    
    @property
    def catalog(self):
        """catalog (`optional`). Units: ``.
        
        
        

        Returns:
            str: Returns the context set for the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `catalog=icsd`
        """
        return self._lazy_load("catalog")
    
    @property
    def code(self):
        """ab initio code (`optional`). Units: ``.
        
        
        

        Returns:
            str: Returns the software name and version used to perform the simulation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `code=vasp.4.6.35`
        """
        return self._lazy_load("code")
    
    @property
    def composition(self):
        """composition (`optional`). Units: ``.
        
        
        

        Returns:
            list: Returns a comma delimited composition description of the structure entry in the calculated cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `composition=2,6,6`
        """
        return self._lazy_load("composition")
    
    @property
    def compound(self):
        """chemical formula (`mandatory`). Units: ``.
        
        
        

        Returns:
            str: Returns the composition description of the compound in the calculated cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `compound=Co2Er6Si6`
        """
        return self._lazy_load("compound")
    
    @property
    def corresponding(self):
        """coresponding (`optional`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            list: Returns the name (not necessarily an individual) and affiliation associated with the data origin concerning correspondence about data.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `corresponding=M_Buongiorno_Nardelli_mbn@unt.edu`
        """
        return self._lazy_load("corresponding")
    
    @property
    def data_api(self):
        """REST API version (`mandatory`). Units: ``.
        
        
        

        Returns:
            str: AFLOWLIB version of the entry, API.}
        
        Examples:
            You can expect the *content* of the result to be something like:

            `data_api=aapi1.0`
        """
        return self._lazy_load("data_api")
    
    @property
    def data_language(self):
        """data language (`optional`). Units: ``.
        
        
        

        Returns:
            list: Gives the language of the data in AFLOWLIB.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `data_language=aflowlib`
        """
        return self._lazy_load("data_language")
    
    @property
    def data_source(self):
        """data source (`optional`). Units: ``.
        
        
        

        Returns:
            list: Gives the source of the data in AFLOWLIB.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `data_source=aflowlib`
        """
        return self._lazy_load("data_source")
    
    @property
    def delta_electronic_energy_convergence(self):
        """Electronic Energy of Convergence Step (`optional`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            float: Returns the change in energy from the last step of the convergence iteration.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `delta_electronic_energy_convergence=6.09588e-05`
        """
        return self._lazy_load("delta_electronic_energy_convergence")
    
    @property
    def delta_electronic_energy_threshold(self):
        """Electronic Energy of Convergence Threshold (`optional`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            float: Returns the maximimum change in energy required for the convergence iteration.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `delta_electronic_energy_threshold=0.0001`
        """
        return self._lazy_load("delta_electronic_energy_threshold")
    
    @property
    def density(self):
        """mass density (`optional`). Units: `grams/cm<sup>3</sup>`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            float: Returns the mass density in grams/cm3.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `density=7.76665`
        """
        return self._lazy_load("density")
    
    @property
    def dft_type(self):
        """DFT type (`optional`). Units: ``.
        
        
        

        Returns:
            list: Returns information about the pseudopotential type, the exchange correlation functional used (normal or hybrid) and use of GW.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `dft_type=PAW_PBE,HSE06`
        """
        return self._lazy_load("dft_type")
    
    @property
    def eentropy_atom(self):
        """atomistic electronic entropy (`optional`). Units: `eV/atom`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the electronic entropy of the atom used to converge the ab initio calculation (smearing).
        
        Examples:
            You can expect the *content* of the result to be something like:

            `eentropy_atom=0.0011`
        """
        return self._lazy_load("eentropy_atom")
    
    @property
    def eentropy_cell(self):
        """unit cell electronic entropy (`optional`). Units: `eV/atom`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the electronic entropy of the unit cell used to converge the ab initio calculation (smearing).
        
        Examples:
            You can expect the *content* of the result to be something like:

            `eentropy_cell=0.0011`
        """
        return self._lazy_load("eentropy_cell")
    
    @property
    def energy_atom(self):
        """atomic energy (`mandatory`). Units: `eV/atom`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            float: Returns the total ab initio energy per atom- the value of energy_cell/$N$).
        
        Examples:
            You can expect the *content* of the result to be something like:

            `energy_atom=-82.1656`
        """
        return self._lazy_load("energy_atom")
    
    @property
    def energy_cell(self):
        """unit cell energy (`mandatory`). Units: `eV`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            float: Returns the total ab initio energy of the unit cell, E. At T=0K and p=0, this is the internal energy of the system (per unit cell).
        
        Examples:
            You can expect the *content* of the result to be something like:

            `energy_cell=-82.1656`
        """
        return self._lazy_load("energy_cell")
    
    @property
    def energy_cutoff(self):
        """energy cutoff (`optional`). Units: `eV`.
        
        
        

        Returns:
            list: Set of energy cut-offs used during the various steps of the calculations.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `energy_cutoff=384.1,384.1,384.1`
        """
        return self._lazy_load("energy_cutoff")
    
    @property
    def enthalpy_atom(self):
        """atomic enthalpy (`mandatory`). Units: `eV/atom`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            float: Returns the enthalpy per atom- the value of enthalpy_cell/N).
        
        Examples:
            You can expect the *content* of the result to be something like:

            `enthalpy_atom=-82.1656`
        """
        return self._lazy_load("enthalpy_atom")
    
    @property
    def enthalpy_cell(self):
        """unit cell enthalpy (`mandatory`). Units: `eV`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            float: Returns the enthalpy of the system of the unit cell, H = E + PV.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `enthalpy_cell=-82.1656`
        """
        return self._lazy_load("enthalpy_cell")
    
    @property
    def enthalpy_formation_atom(self):
        """atomic formation enthalpy (`mandatory`). Units: `eV/atom`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the formation enthalpy DeltaHFatomic per atom).
        
        Examples:
            You can expect the *content* of the result to be something like:

            `enthalpy_formation_atom=-33.1587`
        """
        return self._lazy_load("enthalpy_formation_atom")
    
    @property
    def enthalpy_formation_cell(self):
        """unit cell formation enthalpy (`mandatory`). Units: `eV`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the formation enthalpy DeltaHF per unit cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `enthalpy_formation_cell=-33.1587`
        """
        return self._lazy_load("enthalpy_formation_cell")
    
    @property
    def entropic_temperature(self):
        """entropic temperature (`mandatory`). Units: `Kelvin`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the entropic temperature for the structure.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `entropic_temperature=1072.1`
        """
        return self._lazy_load("entropic_temperature")
    
    
    @property
    def forces(self):
        """Quantum Forces (`optional`). Units: `eV/&Aring;`.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            numpy.ndarray: Final quantum mechanical forces (Fi,Fj,Fk) in the notation of the code.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `forces=0,-0.023928,0.000197;0,0.023928,-0.000197;...`
        """
        return self._lazy_load("forces")
    
    @property
    def geometry(self):
        """unit cell basis (`mandatory`). Units: `&Aring;`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            list: Returns geometrical data describing the unit cell in the usual a,b,c,alpha,beta,gamma notation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `geometry=18.82,18.82,18.82,32.41,32.41,32.41`
        """
        return self._lazy_load("geometry")
    
    @property
    def keywords(self):
        """Title (`mandatory`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            list: This includes the list of keywords available in the entry, separated by commas.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `keywords=aurl,auid,loop,code,compound,prototype,nspecies,natoms,...`
        """
        return self._lazy_load("keywords")
    
    @property
    def kpoints(self):
        """K-point mesh (`optional`). Units: ``.
        
        
        

        Returns:
            dict: Set of k-point meshes uniquely identifying the various steps of the calculations, e.g. relaxation, static and electronic band structure (specifying the k-space symmetry points of the structure).
        
        Examples:
            You can expect the *content* of the result to be something like:

            `kpoints=10,10,10;16,16,16;G-X-W-K-G-L-U-W-L-K+U-X`
        """
        return self._lazy_load("kpoints")
    
    @property
    def lattice_system_orig(self):
        """original lattice system (`mandatory`). Units: ``.
        
        
        

        Returns:
            str: Return the lattice system and lattice variation (Brillouin zone) of the original-unrelaxed structure before the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `lattice_system_orig=rhombohedral`
        """
        return self._lazy_load("lattice_system_orig")
    
    @property
    def lattice_system_relax(self):
        """relaxed lattice system (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`stress_tensor`

        Returns:
            str: Return the lattice system and lattice variation (Brillouin zone) of the relaxed structure after the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `lattice_system_relax=rhombohedral`
        """
        return self._lazy_load("lattice_system_relax")
    
    @property
    def lattice_variation_orig(self):
        """original lattice variation (`mandatory`). Units: ``.
        
        
        

        Returns:
            str: Return the lattice system and lattice variation (Brillouin zone) of the original-unrelaxed structure before the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `lattice_variation_orig=rhombohedral`
        """
        return self._lazy_load("lattice_variation_orig")
    
    @property
    def lattice_variation_relax(self):
        """relaxed lattice variation (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`stress_tensor`

        Returns:
            str: Return the lattice system and lattice variation (Brillouin zone) of the relaxed structure after the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `lattice_variation_relax=rhombohedral`
        """
        return self._lazy_load("lattice_variation_relax")
    
    @property
    def ldau_TLUJ(self):
        """on site coulomb interaction (`mandatory`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            list: This vector of numbers contains the parameters of the DFT+U calculations, based on a corrective functional inspired by the Hubbard model.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `ldau_TLUJ=2;2,0,0;5,0,0;0,0,0`
        """
        return self._lazy_load("ldau_TLUJ")
    
    @property
    def loop(self):
        """process category (`optional`). Units: ``.
        
        
        

        Returns:
            list: Informs the user of the type of post-processing that was performed.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `loop=thermodynamics,bands,magnetic`
        """
        return self._lazy_load("loop")
    
    @property
    def natoms(self):
        """number of atoms in unit cell (`mandatory`). Units: ``.
        
        
        

        Returns:
            float: Returns the number of atoms in the unit cell of the structure entry. The number can be non integer if partial occupation is considered within appropriate approximations.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `natoms=12`
        """
        return self._lazy_load("natoms")
    
    @property
    def nbondxx(self):
        """nearest neighbor bond lengths (`optional`). Units: `&Aring;`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            list: Nearest neighbors bond lengths of the relaxed structure per ordered set of species Ai,Aj greater than or equal to i.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `nbondxx=1.2599,1.0911,1.0911,1.7818,1.2599,1.7818`
        """
        return self._lazy_load("nbondxx")
    
    @property
    def node_CPU_Cores(self):
        """available CPU cores (`optional`). Units: ``.
        
        
        

        Returns:
            float: Information about the number of cores in the node/cluster where the calculation was performed.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `node_CPU_Cores=12`
        """
        return self._lazy_load("node_CPU_Cores")
    
    @property
    def node_CPU_MHz(self):
        """CPU rate (`optional`). Units: `Megahertz`.
        
        
        

        Returns:
            float: Information about the CPU speed in the node/cluster where the calculation was performed.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `node_CPU_MHz=12`
        """
        return self._lazy_load("node_CPU_MHz")
    
    @property
    def node_CPU_Model(self):
        """CPU model (`optional`). Units: ``.
        
        
        

        Returns:
            str: Information about the CPU model in the node/cluster where the calculation was performed.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `node_CPU_Model=12`
        """
        return self._lazy_load("node_CPU_Model")
    
    @property
    def node_RAM_GB(self):
        """available RAM (`optional`). Units: `Gigabytes`.
        
        
        

        Returns:
            float: Information about the RAM in the node/cluster where the calculation was performed.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `node_RAM_GB=12`
        """
        return self._lazy_load("node_RAM_GB")
    
    @property
    def nspecies(self):
        """species count (`mandatory`). Units: ``.
        
        
        

        Returns:
            float: Returns the number of species in the system (e.g., binary = 2, ternary = 3, etc.).
        
        Examples:
            You can expect the *content* of the result to be something like:

            `nspecies=3`
        """
        return self._lazy_load("nspecies")
    
    @property
    def positions_cartesian(self):
        """relaxed absolute positions (`mandatory`). Units: `&Aring;`.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            numpy.ndarray: Final Cartesian positions (xi,xj,xk) in the notation of the code.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `positions_cartesian=0,0,0;18.18438,0,2.85027;...`
        """
        return self._lazy_load("positions_cartesian")
    
    @property
    def positions_fractional(self):
        """relaxed relative positions (`mandatory`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            numpy.ndarray: Final fractional positions (xi,xj,xk) with respect to the unit cell as specified in $geometry.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `positions_fractional=0,0,0;0.25,0.25,0.25;...`
        """
        return self._lazy_load("positions_fractional")
    
    @property
    def pressure(self):
        """external pressure (`mandatory`). Units: `kbar`.
        
        
        

        Returns:
            float: Returns the target pressure selected for the simulation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `pressure=10.0`
        """
        return self._lazy_load("pressure")
    
    @property
    def pressure_final(self):
        """resulting pressure (`mandatory`). Units: `kbar`.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            float: Returns the external pressure achieved by the simulation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `pressure_final=10.0`
        """
        return self._lazy_load("pressure_final")
    
    @property
    def pressure_residual(self):
        """residual pressure (`mandatory`). Units: `kbar`.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            float: Returns the external pressure achieved by the simulation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `pressure_residual=10.0`
        """
        return self._lazy_load("pressure_residual")
    
    @property
    def prototype(self):
        """original prototype (`mandatory`). Units: ``.
        
        
        

        Returns:
            str: Returns the AFLOW unrelaxed prototype which was used for the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `prototype=T0001.A2BC`
        """
        return self._lazy_load("prototype")
    
    @property
    def scintillation_attenuation_length(self):
        """attenuation length (`mandatory`). Units: `cm`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns the scintillation attenuation length of the compound in cm.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `scintillation_attenuation_length=2.21895`
        """
        return self._lazy_load("scintillation_attenuation_length")
    
    @property
    def sg(self):
        """space group of compound (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`stress_tensor`

        Returns:
            list: Evolution of the space group of the compound.  The first, second and third string represent space group name/number before the first, after the first, and after the last relaxation of the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `sg=Fm-3m#225,Fm-3m#225,Fm-3m#225`
        """
        return self._lazy_load("sg")
    
    @property
    def sg2(self):
        """refined space group of compound  (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`stress_tensor`

        Returns:
            list: Evolution of the space group of the compound.  The first, second and third string represent space group name/number before the first, after the first, and after the last relaxation of the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `sg2=Fm-3m#225,Fm-3m#225,Fm-3m#225`
        """
        return self._lazy_load("sg2")
    
    @property
    def spacegroup_orig(self):
        """original space group number (`mandatory`). Units: ``.
        
        
        

        Returns:
            float: Returns the spacegroup number of the original-unrelaxed structure before the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `spacegroup_orig=225`
        """
        return self._lazy_load("spacegroup_orig")
    
    @property
    def spacegroup_relax(self):
        """relaxed space group number (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`stress_tensor`

        Returns:
            float: Returns the spacegroup number of the relaxed structure after the calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `spacegroup_relax=225`
        """
        return self._lazy_load("spacegroup_relax")
    
    @property
    def species(self):
        """atomic species (`mandatory`). Units: ``.
        
        
        

        Returns:
            list: Species of the atoms in this material.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `species=Y,Zn,Zr`
        """
        return self._lazy_load("species")
    
    @property
    def species_pp(self):
        """pseudopotential of chemical speciess (`mandatory`). Units: ``.
        
        
        

        Returns:
            list: Pseudopotentials of the atomic species.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `species_pp=Y,Zn,Zr`
        """
        return self._lazy_load("species_pp")
    
    @property
    def species_pp_ZVAL(self):
        """valence atoms per species (`optional`). Units: `electrons`.
        
        
        

        Returns:
            list: Returns the number of valence electrons of the atomic species.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `species_pp_ZVAL=3`
        """
        return self._lazy_load("species_pp_ZVAL")
    
    @property
    def species_pp_version(self):
        """pseudopotential version and species (`mandatory`). Units: ``.
        
        
        

        Returns:
            list: Species of the atoms, pseudopotentials species, and pseudopotential versions.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `species_pp_version=Y,Zn,Zr`
        """
        return self._lazy_load("species_pp_version")
    
    @property
    def spinD(self):
        """spin decomposition over unit cell (`mandatory`). Units: `&mu;<sub>B</sub>`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            list: For spin polarized calculations, the spin decomposition over the atoms of the cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `spinD=0.236,0.236,-0.023,1.005`
        """
        return self._lazy_load("spinD")
    
    @property
    def spinF(self):
        """magnetization of unit cell at Fermi level (`mandatory`). Units: `&mu;<sub>B</sub>`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: For spin polarized calculations, the magnetization of the cell at the Fermi level.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `spinF=0.410879`
        """
        return self._lazy_load("spinF")
    
    @property
    def spin_atom(self):
        """atomic spin polarization (`mandatory`). Units: `&mu;<sub>B</sub>/atom`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: For spin polarized calculations, the magnetization per atom.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `spin_atom=2.16419`
        """
        return self._lazy_load("spin_atom")
    
    @property
    def spin_cell(self):
        """unit cell spin polarization (`mandatory`). Units: `&mu;<sub>B</sub>`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: For spin polarized calculations, the total magnetization of the cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `spin_cell=2.16419`
        """
        return self._lazy_load("spin_cell")
    
    @property
    def sponsor(self):
        """sponsor (`optional`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            list: Returns information about funding agencies and other sponsors for the data.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `sponsor=DOD_N000141310635,NIST_70NANB12H163`
        """
        return self._lazy_load("sponsor")
    
    @property
    def stoich(self):
        """unit cell stoichiometry (`optional`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            list: Similar to composition, returns a comma delimited stoichiometry description of the structure entry in the calculated cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `stoichiometry=0.5,0.25,0.25`
        """
        return self._lazy_load("stoich")
    
    @property
    def stoichiometry(self):
        """unit cell stoichiometry (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            list: Similar to composition, returns a comma delimited stoichiometry description of the structure entry in the calculated cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `stoichiometry=0.5,0.25,0.25`
        """
        return self._lazy_load("stoichiometry")
    
    @property
    def stress_tensor(self):
        """Stress Tensor (`mandatory`). Units: ``.
        
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.
        

        Returns:
            list: Returns the stress tensor of the completed calculation.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `stress_tensor=-0.96,-0,-0,-0,-0.96,-0,-0,-0,-0.96`
        """
        return self._lazy_load("stress_tensor")
    
    @property
    def valence_cell_iupac(self):
        """unit cell IUPAC valence (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns IUPAC valence, the maximum number of univalent atoms that may combine with the atoms.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `valence_cell_iupac=22`
        """
        return self._lazy_load("valence_cell_iupac")
    
    @property
    def valence_cell_std(self):
        """unit cell standard valence (`mandatory`). Units: ``.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`kpoints`

        Returns:
            float: Returns standard valence, the maximum number of univalent atoms that may combine with the atoms.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `valence_cell_std=22`
        """
        return self._lazy_load("valence_cell_std")
    
    @property
    def volume_atom(self):
        """atomic volume (`mandatory`). Units: `&Aring;<sup>3</sup>/atom`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            float: Returns the volume per atom in the unit cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `volume_atom=100.984`
        """
        return self._lazy_load("volume_atom")
    
    @property
    def volume_cell(self):
        """unit cell volume (`mandatory`). Units: `&Aring;<sup>3</sup>`.
        
        
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          
          - :meth:`energy_cutoff`
          - :meth:`forces`
          - :meth:`kpoints`
          - :meth:`pressure_residual`
          - :meth:`stress_tensor`

        Returns:
            float: Returns the volume of the unit cell.
        
        Examples:
            You can expect the *content* of the result to be something like:

            `volume_cell=100.984`
        """
        return self._lazy_load("volume_cell")
    
