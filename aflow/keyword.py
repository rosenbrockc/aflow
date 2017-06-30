"""Implements classes to represent each keyword with overloaded
operators to make querying with AFLUX intuitive.
"""
from six import string_types

class Keyword(object):
    """Represents an abstract keyword that can be sub-classed for a
    specific material attribute. This class also represents logical
    operators that define search queries. The combination of two
    keywords with a logical operator produces one more keyword, but
    which has its :attr:`state` altered.

    Args:
        state (str): current query state of this keyword (combination).

    Attributes:
        state (str): current query state of this keyword (combination).
        ptype (type): python type that values for this keyword will have.
        name (str): keyword name to use in the AFLUX request.
    """
    name = None
    ptype = None
    
    def __init__(self, state=None):
        self.state = state
        self.ptype = ptype
        self.name = name

    def __str__(self):
        return self.state
        
    def __getattr__(self, attr):
        if attr in self.attributes:
            return self.attributes[attr]
        
    def __lt__(self, other):
        assert self.state is None
        if isinstance(other, string_types):
            self.state = "{0}(*'{1}')".format(self.name, other)
        else:
            self.state = "{0}(*{1})".format(self.name, other)
        return self
            
    def __gt__(self, other):
        assert self.state is None
        if isinstance(other, string_types):
            self.state = "{0}('{1}'*)".format(self.name, other)
        else:
            self.state = "{0}({1}*)".format(self.name, other)
        return self

    def __contains__(self, other):
        assert isinstance(other, string_types)
        assert self.state is None
        self.state = "{0}(*'{1}'*)".format(self.name, other)
    
    def __eq__(self, other):
        assert self.state is None
        if isinstance(other, string_types):
            self.state = "{0}('{1}')".format(self.name, other)
        else:
            self.state = "{0}({1})".format(self.name, other)
        return self

    def __and__(self, other):
        assert isinstance(other, Keyword)
        print(str(self), str(other))
        assert self.state is not None
        assert other.state is not None
        return Keyword("{0},{1}".format(self.state, other.state))

    def __or__(self, other):
        assert isinstance(other, Keyword)
        assert self.state is not None
        assert other.state is not None
        return Keyword("{0}:{1}".format(self.state, other.state))

    def __not__(self):
        if self.state is not None:
            if '!' in self.state:
                self.state = self.state.replace('!', '')
            else:
                self.state = self.state.replace('(', "(!")
        return self

    
class data_source(Keyword):
    """data source (`optional`). Units: ``.
    
    

    Returns:
        list: Gives the source of the data in AFLOWLIB.
    """
    name = data_source
    ptype = list
    
    
class spinf(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = spinf
    ptype = None
    
    
class node_cpu_cores(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = node_cpu_cores
    ptype = None
    
    
class ael_elastic_anistropy(Keyword):
    """AEL elastic anistropy (`optional`). Units: ``.
    
    

    Returns:
        float or int: Returns the elastic anistropy as calculated with AEL.
    """
    name = ael_elastic_anistropy
    ptype = float or int
    
    
class volume_atom(Keyword):
    """atomic volume (`mandatory`). Units: `&Aring;<sup>3</sup>/atom`.
    
    

    Returns:
        float or int: Returns the volume per atom in the unit cell.
    """
    name = volume_atom
    ptype = float or int
    
    
class lattice_variation_relax(Keyword):
    """relaxed lattice variation (`mandatory`). Units: ``.
    
    

    Returns:
        str: Return the lattice system and lattice variation (Brillouin zone) of the relaxed structure after the calculation.
    """
    name = lattice_variation_relax
    ptype = str
    
    
class stoichiometry(Keyword):
    """unit cell stoichiometry (`mandatory`). Units: ``.
    
    

    Returns:
        list: Similar to composition, returns a comma delimited stoichiometry description of the structure entry in the calculated cell.
    """
    name = stoichiometry
    ptype = list
    
    
class bader_atomic_volumes(Keyword):
    """atomic volume per atom (`optional`). Units: `&Aring;<sup>3</sup>`.
    
    

    Returns:
        list: Returns the volume of each atom of the primitive cell as calculated by the Bader Atoms in Molecules Analysis. This volume encapsulates the electron density associated with each atom above a threshold of 0.0001 electrons.
    """
    name = bader_atomic_volumes
    ptype = list
    
    
class node_cpu_mhz(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = node_cpu_mhz
    ptype = None
    
    
class pearson_symbol_relax(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = pearson_symbol_relax
    ptype = None
    
    
class pressure(Keyword):
    """external pressure (`mandatory`). Units: `kbar`.
    
    

    Returns:
        float or int: Returns the target pressure selected for the simulation.
    """
    name = pressure
    ptype = float or int
    
    
class energy_cutoff(Keyword):
    """energy cutoff (`optional`). Units: `eV`.
    
    

    Returns:
        list: Set of energy cut-offs used during the various steps of the calculations.
    """
    name = energy_cutoff
    ptype = list
    
    
class data_language(Keyword):
    """data language (`optional`). Units: ``.
    
    

    Returns:
        list: Gives the language of the data in AFLOWLIB.
    """
    name = data_language
    ptype = list
    
    
class spin_atom(Keyword):
    """atomic spin polarization (`mandatory`). Units: `&mu;<sub>B</sub>/atom`.
    
    

    Returns:
        float or int: For spin polarized calculations, the magnetization per atom.
    """
    name = spin_atom
    ptype = float or int
    
    
class egap_type(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = egap_type
    ptype = None
    
    
class eentropy_atom(Keyword):
    """atomistic electronic entropy (`optional`). Units: `eV/atom`.
    
    

    Returns:
        float or int: Returns the electronic entropy of the atom used to converge the ab initio calculation (smearing).
    """
    name = eentropy_atom
    ptype = float or int
    
    
class agl_bulk_modulus_isothermal_300k(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = agl_bulk_modulus_isothermal_300k
    ptype = None
    
    
class node_cpu_model(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = node_cpu_model
    ptype = None
    
    
class ael_shear_modulus_vrh(Keyword):
    """AEL VRH shear modulus (`optional`). Units: `GPa`.
    
    

    Returns:
        float or int: Returns the shear modulus as calculated using the Voigt-Reuss-Hill average with AEL.
    """
    name = ael_shear_modulus_vrh
    ptype = float or int
    
    
class spind_magmom_orig(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = spind_magmom_orig
    ptype = None
    
    
class valence_cell_std(Keyword):
    """unit cell standard valence (`mandatory`). Units: ``.
    
    

    Returns:
        float or int: Returns standard valence, the maximum number of univalent atoms that may combine with the atoms.
    """
    name = valence_cell_std
    ptype = float or int
    
    
class kpoints(Keyword):
    """K-point mesh (`optional`). Units: ``.
    
    

    Returns:
        tuple: Set of k-point meshes uniquely identifying the various steps of the calculations, e.g. relaxation, static and electronic band structure (specifying the k-space symmetry points of the structure).
    """
    name = kpoints
    ptype = tuple
    
    
class enthalpy_cell(Keyword):
    """unit cell enthalpy (`mandatory`). Units: `eV`.
    
    

    Returns:
        float or int: Returns the enthalpy of the system of the unit cell, H = E + PV.
    """
    name = enthalpy_cell
    ptype = float or int
    
    
class spin_cell(Keyword):
    """unit cell spin polarization (`mandatory`). Units: `&mu;<sub>B</sub>`.
    
    

    Returns:
        float or int: For spin polarized calculations, the total magnetization of the cell.
    """
    name = spin_cell
    ptype = float or int
    
    
class species_pp_version(Keyword):
    """pseudopotential species/version (`mandatory`). Units: ``.
    
    

    Returns:
        list: Species of the atoms, pseudopotentials species, and pseudopotential versions.
    """
    name = species_pp_version
    ptype = list
    
    
class composition(Keyword):
    """composition (`optional`). Units: ``.
    
    

    Returns:
        list: Returns a comma delimited composition description of the structure entry in the calculated cell.
    """
    name = composition
    ptype = list
    
    
class spacegroup_orig(Keyword):
    """original space group number (`mandatory`). Units: ``.
    
    

    Returns:
        float or int: Returns the spacegroup number of the original-unrelaxed structure before the calculation.
    """
    name = spacegroup_orig
    ptype = float or int
    
    
class enthalpy_atom(Keyword):
    """atomic enthalpy (`mandatory`). Units: `eV/atom`.
    
    

    Returns:
        float or int: Returns the enthalpy per atom- the value of enthalpy_cell/N).
    """
    name = enthalpy_atom
    ptype = float or int
    
    
class ael_bulk_modulus_vrh(Keyword):
    """AEL VRH bulk modulus (`optional`). Units: `GPa`.
    
    

    Returns:
        float or int: Returns the bulk modulus as calculated using the Voigt-Reuss-Hill average with AEL.
    """
    name = ael_bulk_modulus_vrh
    ptype = float or int
    
    
class auid(Keyword):
    """AFLOWLIB Unique Identifier (`mandatory`). Units: ``.
    
    

    Returns:
        str: AFLOWLIB Unique Identifier for the entry, AUID, which can be used as a publishable object identifier.
    """
    name = auid
    ptype = str
    
    
class ael_shear_modulus_voigt(Keyword):
    """AEL Voigt shear modulus (`optional`). Units: `GPa`.
    
    

    Returns:
        float or int: Returns the shear modulus as calculated using the Voigt method with AEL.
    """
    name = ael_shear_modulus_voigt
    ptype = float or int
    
    
class bader_net_charges(Keyword):
    """partial charge per atom (`optional`). Units: `electrons`.
    
    

    Returns:
        list: Returns a comma delimited set of partial charges per atom of the primitive cell as calculated by the Bader Atoms in Molecules Analysis.
    """
    name = bader_net_charges
    ptype = list
    
    
class sg(Keyword):
    """compound space group (`mandatory`). Units: ``.
    
    

    Returns:
        list: Evolution of the space group of the compound.  The first, second and third string represent space group name/number before the first, after the first, and after the last relaxation of the calculation.
    """
    name = sg
    ptype = list
    
    
class compound(Keyword):
    """chemical formula (`mandatory`). Units: ``.
    
    

    Returns:
        str: Returns the composition description of the compound in the calculated cell.
    """
    name = compound
    ptype = str
    
    
class species_pp(Keyword):
    """species pseudopotential(s) (`mandatory`). Units: ``.
    
    

    Returns:
        list: Pseudopotentials of the atomic species.
    """
    name = species_pp
    ptype = list
    
    
class aflow_version(Keyword):
    """aflow version (`optional`). Units: ``.
    
    

    Returns:
        str: Returns the version number of AFLOW used to perform the calculation.
    """
    name = aflow_version
    ptype = str
    
    
class forces(Keyword):
    """Quantum Forces (`optional`). Units: `eV/&Aring;`.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        numpy.ndarray: Final quantum mechanical forces (Fi,Fj,Fk) in the notation of the code.
    """
    name = forces
    ptype = numpy.ndarray
    
    
class energy_atom(Keyword):
    """atomic energy (`mandatory`). Units: `eV/atom`.
    
    

    Returns:
        float or int: Returns the total ab initio energy per atom- the value of energy_cell/$N$).
    """
    name = energy_atom
    ptype = float or int
    
    
class spacegroup_relax(Keyword):
    """relaxed space group number (`mandatory`). Units: ``.
    
    

    Returns:
        float or int: Returns the spacegroup number of the relaxed structure after the calculation.
    """
    name = spacegroup_relax
    ptype = float or int
    
    
class ldau_tluj(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = ldau_tluj
    ptype = None
    
    
class energy_cell(Keyword):
    """unit cell energy (`mandatory`). Units: `eV`.
    
    

    Returns:
        float or int: Returns the total ab initio energy of the unit cell, E. At T=0K and p=0, this is the internal energy of the system (per unit cell).
    """
    name = energy_cell
    ptype = float or int
    
    
class positions_cartesian(Keyword):
    """relaxed absolute positions (`mandatory`). Units: `&Aring;`.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        numpy.ndarray: Final Cartesian positions (xi,xj,xk) in the notation of the code.
    """
    name = positions_cartesian
    ptype = numpy.ndarray
    
    
class aurl(Keyword):
    """AFLOWLIB Uniform Resource Locator (`mandatory`). Units: ``.
    
    

    Returns:
        str: AFLOWLIB Uniform Resource Locator returns the AURL of the entry.
    """
    name = aurl
    ptype = str
    
    
class enthalpy_formation_atom(Keyword):
    """atomic formation enthalpy (`mandatory`). Units: `eV/atom`.
    
    

    Returns:
        float or int: Returns the formation enthalpy DeltaHFatomic per atom).
    """
    name = enthalpy_formation_atom
    ptype = float or int
    
    
class pv_cell(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = pv_cell
    ptype = None
    
    
class bravais_lattice_relax(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = bravais_lattice_relax
    ptype = None
    
    
class agl_thermal_expansion_300k(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = agl_thermal_expansion_300k
    ptype = None
    
    
class aflowlib_entries(Keyword):
    """aflowlib entries (`conditional`). Units: ``.
    
    

    Returns:
        list: For projects and set-layer entries, aflowlib_entries lists the available sub-entries which are associated with the $aurl of the subdirectories.  By parsing $aurl/?aflowlib_entries (containing $aurl/aflowlib_entries_number entries) the user finds further locations to interrogate.
    """
    name = aflowlib_entries
    ptype = list
    
    
class pv_atom(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = pv_atom
    ptype = None
    
    
class loop(Keyword):
    """process category (`optional`). Units: ``.
    
    

    Returns:
        list: Informs the user of the type of post-processing that was performed.
    """
    name = loop
    ptype = list
    
    
class spind(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        list: No description was returned from AFLUX.
    """
    name = spind
    ptype = list
    
    
class agl_gruneisen(Keyword):
    """AGL Gruneisen parameter (`optional`). Units: ``.
    
    

    Returns:
        float or int: Returns the Gruneisen parameter as calculated with AGL.
    """
    name = agl_gruneisen
    ptype = float or int
    
    
class valence_cell_iupac(Keyword):
    """unit cell IUPAC valence (`mandatory`). Units: ``.
    
    

    Returns:
        float or int: Returns IUPAC valence, the maximum number of univalent atoms that may combine with the atoms.
    """
    name = valence_cell_iupac
    ptype = float or int
    
    
class density(Keyword):
    """mass density (`optional`). Units: `grams/cm<sup>3</sup>`.
    
    

    Returns:
        float or int: Returns the mass density in grams/cm3.
    """
    name = density
    ptype = float or int
    
    
class natoms(Keyword):
    """unit cell atom count (`mandatory`). Units: ``.
    
    

    Returns:
        float or int: Returns the number of atoms in the unit cell of the structure entry. The number can be non integer if partial occupation is considered within appropriate approximations.
    """
    name = natoms
    ptype = float or int
    
    
class sponsor(Keyword):
    """sponsor (`optional`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        list: Returns information about funding agencies and other sponsors for the data.
    """
    name = sponsor
    ptype = list
    
    
class node_ram_gb(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = node_ram_gb
    ptype = None
    
    
class agl_bulk_modulus_static_300k(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = agl_bulk_modulus_static_300k
    ptype = None
    
    
class author(Keyword):
    """author (`optional`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        list: Returns the name (not necessarily an individual) and affiliation associated with authorship of the data.
    """
    name = author
    ptype = list
    
    
class calculation_cores(Keyword):
    """used CPU cores (`optional`). Units: ``.
    
    

    Returns:
        float or int: Number of processors/cores used for the calculation.
    """
    name = calculation_cores
    ptype = float or int
    
    
class corresponding(Keyword):
    """coresponding (`optional`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        list: Returns the name (not necessarily an individual) and affiliation associated with the data origin concerning correspondence about data.
    """
    name = corresponding
    ptype = list
    
    
class volume_cell(Keyword):
    """unit cell volume (`mandatory`). Units: `&Aring;<sup>3</sup>`.
    
    

    Returns:
        float or int: Returns the volume of the unit cell.
    """
    name = volume_cell
    ptype = float or int
    
    
class files(Keyword):
    """I/O files (`conditional`). Units: ``.
    
    

    Returns:
        list: Provides access to the input and output files used in the simulation (provenance data).
    """
    name = files
    ptype = list
    
    
class agl_debye(Keyword):
    """AGL Debye temperature (`optional`). Units: `K`.
    
    

    Returns:
        float or int: Returns the Debye temperature as calculated with AGL.
    """
    name = agl_debye
    ptype = float or int
    
    
class agl_heat_capacity_cv_300k(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = agl_heat_capacity_cv_300k
    ptype = None
    
    
class aflowlib_date(Keyword):
    """material generation date (`optional`). Units: ``.
    
    

    Returns:
        str: Returns the date of the AFLOW post-processor which generated the entry for the library.
    """
    name = aflowlib_date
    ptype = str
    
    
class lattice_system_orig(Keyword):
    """original lattice system (`mandatory`). Units: ``.
    
    

    Returns:
        str: Return the lattice system and lattice variation (Brillouin zone) of the original-unrelaxed structure before the calculation.
    """
    name = lattice_system_orig
    ptype = str
    
    
class ael_shear_modulus_reuss(Keyword):
    """AEL Reuss shear modulus (`optional`). Units: `GPa`.
    
    

    Returns:
        float or int: Returns the shear modulus as calculated using the Reuss method with AEL.
    """
    name = ael_shear_modulus_reuss
    ptype = float or int
    
    
class ael_poisson_ratio(Keyword):
    """AEL Poisson ratio (`optional`). Units: ``.
    
    

    Returns:
        float or int: Returns the istropic Poisson ratio as calculated with AEL.
    """
    name = ael_poisson_ratio
    ptype = float or int
    
    
class lattice_system_relax(Keyword):
    """relaxed lattice system (`mandatory`). Units: ``.
    
    

    Returns:
        str: Return the lattice system and lattice variation (Brillouin zone) of the relaxed structure after the calculation.
    """
    name = lattice_system_relax
    ptype = str
    
    
class keywords(Keyword):
    """Title (`mandatory`). Units: ``.
    
    

    Returns:
        list: This includes the list of keywords available in the entry, separated by commas.
    """
    name = keywords
    ptype = list
    
    
class sg2(Keyword):
    """refined compound space group (`mandatory`). Units: ``.
    
    

    Returns:
        list: Evolution of the space group of the compound.  The first, second and third string represent space group name/number before the first, after the first, and after the last relaxation of the calculation.
    """
    name = sg2
    ptype = list
    
    
class species(Keyword):
    """atomic species (`mandatory`). Units: ``.
    
    

    Returns:
        list: Species of the atoms in this material.
    """
    name = species
    ptype = list
    
    
class dft_type(Keyword):
    """DFT type (`optional`). Units: ``.
    
    

    Returns:
        list: Returns information about the pseudopotential type, the exchange correlation functional used (normal or hybrid) and use of GW.
    """
    name = dft_type
    ptype = list
    
    
class entropic_temperature(Keyword):
    """entropic temperature (`mandatory`). Units: `Kelvin`.
    
    

    Returns:
        float or int: Returns the entropic temperature for the structure.
    """
    name = entropic_temperature
    ptype = float or int
    
    
class eentropy_cell(Keyword):
    """unit cell electronic entropy (`optional`). Units: `eV/atom`.
    
    

    Returns:
        float or int: Returns the electronic entropy of the unit cell used to converge the ab initio calculation (smearing).
    """
    name = eentropy_cell
    ptype = float or int
    
    
class code(Keyword):
    """ab initio code (`optional`). Units: ``.
    
    

    Returns:
        str: Returns the software name and version used to perform the simulation.
    """
    name = code
    ptype = str
    
    
class geometry(Keyword):
    """unit cell basis (`mandatory`). Units: `&Aring;`.
    
    

    Returns:
        list: Returns geometrical data describing the unit cell in the usual a,b,c,alpha,beta,gamma notation.
    """
    name = geometry
    ptype = list
    
    
class enthalpy_formation_cell(Keyword):
    """unit cell formation enthalpy (`mandatory`). Units: `eV`.
    
    

    Returns:
        float or int: Returns the formation enthalpy DeltaHF per unit cell.
    """
    name = enthalpy_formation_cell
    ptype = float or int
    
    
class lattice_variation_orig(Keyword):
    """original lattice variation (`mandatory`). Units: ``.
    
    

    Returns:
        str: Return the lattice system and lattice variation (Brillouin zone) of the original-unrelaxed structure before the calculation.
    """
    name = lattice_variation_orig
    ptype = str
    
    
class agl_thermal_conductivity_300k(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = agl_thermal_conductivity_300k
    ptype = None
    
    
class ael_bulk_modulus_voigt(Keyword):
    """AEL Voigt bulk modulus (`optional`). Units: `GPa`.
    
    

    Returns:
        float or int: Returns the bulk modulus as calculated using the Voigt method with AEL.
    """
    name = ael_bulk_modulus_voigt
    ptype = float or int
    
    
class prototype(Keyword):
    """original prototype (`mandatory`). Units: ``.
    
    

    Returns:
        str: Returns the AFLOW unrelaxed prototype which was used for the calculation.
    """
    name = prototype
    ptype = str
    
    
class calculation_memory(Keyword):
    """used RAM (`optional`). Units: `Megabytes`.
    
    

    Returns:
        float or int: The maximum memory used for the calculation.
    """
    name = calculation_memory
    ptype = float or int
    
    
class calculation_time(Keyword):
    """used time (`optional`). Units: `seconds`.
    
    

    Returns:
        float or int: Total time taken for the calculation.
    """
    name = calculation_time
    ptype = float or int
    
    
class scintillation_attenuation_length(Keyword):
    """attenuation length (`mandatory`). Units: `cm`.
    
    

    Returns:
        float or int: Returns the scintillation attenuation length of the compound in cm.
    """
    name = scintillation_attenuation_length
    ptype = float or int
    
    
class nbondxx(Keyword):
    """Nearest neighbors bond lengths (`optional`). Units: `&Aring;`.
    
    

    Returns:
        list: Nearest neighbors bond lengths of the relaxed structure per ordered set of species Ai,Aj greater than or equal to i.
    """
    name = nbondxx
    ptype = list
    
    
class bravais_lattice_orig(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = bravais_lattice_orig
    ptype = None
    
    
class data_api(Keyword):
    """REST API version (`mandatory`). Units: ``.
    
    

    Returns:
        str: AFLOWLIB version of the entry, API.}
    """
    name = data_api
    ptype = str
    
    
class ael_bulk_modulus_reuss(Keyword):
    """AEL Reuss bulk modulus (`optional`). Units: `GPa`.
    
    

    Returns:
        float or int: Returns the bulk modulus as calculated using the Reuss method with AEL.
    """
    name = ael_bulk_modulus_reuss
    ptype = float or int
    
    
class agl_acoustic_debye(Keyword):
    """AGL acoustic Debye temperature (`optional`). Units: `K`.
    
    

    Returns:
        float or int: Returns the acoustic Debye temperature as calculated with AGL.
    """
    name = agl_acoustic_debye
    ptype = float or int
    
    
class pearson_symbol_orig(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = pearson_symbol_orig
    ptype = None
    
    
class egap(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = egap
    ptype = None
    
    
class agl_heat_capacity_cp_300k(Keyword):
    """No schema information available. (`unknown`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        None: No description was returned from AFLUX.
    """
    name = agl_heat_capacity_cp_300k
    ptype = None
    
    
class aflowlib_entries_number(Keyword):
    """aflowlib entry count (`conditional`). Units: ``.
    
    

    Returns:
        float or int: For projects and set-layer entries, aflowlib_entrieslists the available sub-entries which are associated with the $aurl of the subdirectories.  By parsing $aurl/?aflowlib_entries (containing $aurl/aflowlib_entries_number entries) the user finds further locations to interrogate.
    """
    name = aflowlib_entries_number
    ptype = float or int
    
    
class nspecies(Keyword):
    """species count (`mandatory`). Units: ``.
    
    

    Returns:
        float or int: Returns the number of species in the system (e.g., binary = 2, ternary = 3, etc.).
    """
    name = nspecies
    ptype = float or int
    
    
class positions_fractional(Keyword):
    """relaxed relative positions (`mandatory`). Units: ``.
    
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    Returns:
        numpy.ndarray: Final fractional positions (xi,xj,xk) with respect to the unit cell as specified in $geometry.
    """
    name = positions_fractional
    ptype = numpy.ndarray
    

