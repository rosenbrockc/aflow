Example Queries with `aflow`
============================

Although the API is well-documented, we choose to demonstrate how to
use `aflow` with some examples. The homepage of the github repo also
has some short examples.

Downloading the CIF Files
-------------------------

Suppose I am looking for `Si` structures and I want to get the `.cif`
files.

.. code-block:: python

   result = search(
        ).filter(K.species == "Si"
        ).orderby(K.energy_atom)
   a0 = result[0]
   # <aflow.entries.Entry at 0x1132b0c50>
   a0.files
   # [u'CONTCAR.relax', u'CONTCAR.relax.abinit', ...]
   
   #The files object accepts a pattern for selecting a single file
   #from the list. It will raise an error if more than one (or no)
   #file matches the pattern.
   a0.files["\*.312.cif"]
   # AflowFile(aflowlib.duke.edu:AFLOWDATA/LIB2_RAW/SiW_pv/312/SiW_pv.312.cif)

   #The AflowFile object can be called to get the file contents as a
   #string
   a0.files["\*.312.cif"]()
   #u"data_SiW_pv/312 - (312) - NbNi8 [AB8] (312)...

   #Or, you can specify the path to where you want the file saved.
   a0.files["\*.312.cif"]("/temp/si0.cif")
   assert path.isfile("/temp/si0.cif")

Filtering by Multiple Space Groups
----------------------------------

Suppose I want to find Heusler alloys in `aflowlib`:

.. code-block:: python

   heus_result = search(batch_size=100
       ).filter( (K.spacegroup_relax==216) |
       		 (K.spacegroup_relax==225) |
       		 (K.spacegroup_relax==139) |
       		 (K.spacegroup_relax==119) 
       ).select(
       	   K.enthalpy_formation_atom,
       	   K.aurl,
       	   K.species,
       	   K.species_pp
       )
   len(heus_result)
   # 541244

This selects multiple keywords and grabs any of the structures that
have space group numbers of 216, 225, 139 or 119.
