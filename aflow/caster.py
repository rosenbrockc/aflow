"""Functions for casting AFLOW type names to valid python objects. This also
creates :class:`numpy.ndarray` for vector or tensor-valued properties.
"""
import re
_rx_int = re.compile(r"^\d+$")

def _strings(value):
    return list(value.split(','))

def _number(value):
    if _rx_int.match(value):
        return int(value)
    else:
        return float(value)

def _numbers(value):
    svals = list(value.split(','))
    dtype = type(_number(svals[0]))
    vals = list(map(dtype, svals))
    return np.array(vals)

def _forces(value):
    atoms = value.split(';')
    forces = [list(map(float, a.split(','))) for a in atoms]
    return np.array(forces)

def _kpoints(value):
    parts = value.split(';')
    kpts = [np.array(list(map(_number, p.split(','))))
            for p in parts[0:-1]]
    return kpts + [parts[-1]]

exceptions = ["forces", "kpoints", "positions_cartesian",
              "positions_fractional", "spind"]
"""list: of AFLOW keywords for which the casting has to be handled in a special
way.
"""

def ptype(atype, keyword):
    """Returns a `str` representing the *python* type for the
    specified AFLOW type and keyword.
    
    Args:
        atype (str): name of the AFLOW type.
        keyword (str): name of the keyword that the value is associated with.
    """
    castmap = {
        "string": "str",
        "strings": "list",
        "number": "float",
        "numbers": "list",
        "forces": "numpy.ndarray",
        "kpoints": "tuple",
        "positions_cartesian": "numpy.ndarray",
        "positions_fractional": "numpy.ndarray",
        "spind": "list",
        None: None
    }
    
    if keyword not in exceptions:
        return castmap[atype]
    else:
        return castmap[keyword]

def cast(atype, keyword, value):
    """Casts the specified value to a python type, using the AFLOW type as a
    reference.

    .. note:: Unfortunately, some of the AFLOW type names are not descriptive or
      unique enough to make general rule casting possible. Instead, we have to
      encode some exceptions directly in this module.
    
    Args:
        atype (str): name of the AFLOW type.
        keyword (str): name of the keyword that the value is associated with.
        value: object (usually a string) to cast into python types.
    """
    castmap = {
        "string": str,
        "strings": _strings,
        "number": _number,
        "numbers": _numbers,
        "forces": _forces,
        "kpoints": _kpoints,
        "positions_cartesian": _forces,
        "positions_fractional": _forces,
        "spind": _numbers,
        None: lambda v: v
    }

    if keyword not in exceptions:
        return castmap[atype](value)
    else:
        return castmap[keyword](value)
