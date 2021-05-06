"""Unified value casting from AFLOW query entries to results
   There are 3 scenarios:
   1. direct data returned from AFLOW API --> json-like entries
   2. use format $aurl/?<field> for lazy-query --> string entries
   3. fetch all properties of one entry by $aurl/aflowlib.json --> json-like entries

   In case 1 and 3 most values can be directly used without conversion.
   In case 2, the string from aflowlib is converted to desired values
"""
from aflow import msg
import numpy as np

def _str2vec(string, delimiter=";,", format=float, flat=True):
    """Parse a string and return numpy vector or matrix
    """
    # In some cases the keyword is listed but without value
    if string == "":
        return None
    # Force using comma as delimiter
    if len(delimiter) == 0:
        delimter = ","
    if len(delimiter) == 1:
        array = string.strip().split(delimiter)
    elif len(delimiter) == 2:
        # First delimiter may be ";"
        array = string.strip().split(delimiter[0])
        # Second delimiter may be ",", the inner loop
        array = [s.strip().split(delimiter[1]) for s in array]
    else:
        raise ValueError("Length of delimiter should not exceed 2")

    # Use numpy to convert string array to array
    try:
        array = np.array(array, dtype=format)
    except Exception:
        # the exception will happen on Wyckoff_* keywords, currently not using ndarray
        # force conversion for each item
        # At most 2 layers, hardcoding should be fine
        new_array = []
        for l in array:
            if isinstance(l, (list, tuple)):
                new_array.append([format(c) for c in l])
            else:
                new_array.append(format(l))
        return new_array
    
    # Keyword flat makes the array into 1d vec if shape == (1, N) or (N, 1)
    if (flat is True) and (1 in array.shape):
        array = array.ravel()

    # If format is str then return normal list
    if format == str:
        array = array.tolist()
    return array


def _list2vec(lst, format=float, flat=False):
    """Convert list to np.array with desired format
       TODO: test whether conversion fails
    """
    # No error checking for now
    array = np.array(lst, dtype=format)
    if flat:
        array = array.ravel()
    return array
    

def cast(cls, value):
    """ Cast value to desired format based on the `atype`, `ptype` and `delimiter` in class
    Algorithm:
    0. If the keyword is deprecated, return as is
    1. If the value is already in ptype --> return value
    2. If the value is string, then use delimiter and ptype to determine returned value
    3. Else, try to convert value in ptype. If failed, return value and warn        
    """
    # Does the class has all attributes?
    if any([hasattr(cls, attr) is False\
            for attr in ("atype", "ptype", "delimiter", "status")]):
        warn(f"The input class {cls} has incomplete attributes, will use direct value")
        return value

    # deprecated keyword
    if cls.status == "deprecated":
        return value

    # test if value same as ptype
    ptype = cls.ptype
    atype = cls.atype
    # if ptype == (list, float) then main_ptype is list
    if isinstance(ptype, (tuple, list)):
        main_ptype = ptype[0]
    else:
        main_ptype = ptype
    # if isinstance(value, str):

    # print(cls, atype, ptype, value)
    if isinstance(value, main_ptype):
        # Convert numbers to array
        if (main_ptype == list) and (atype == "numbers"):
            try:
                value = _list2vec(value, format=ptype[1])
            except Exception:   # Can happen if the list is not-consistent
                pass
        return value
        # return value
    elif isinstance(value, str):
        if cls.delimiter is None:
            pass                # Use direct conversion
        else:
            # if delimiter is not None then it should have 2 ptypes
            print(cls, value)
            value = _str2vec(value, delimiter=cls.delimiter, format=ptype[1])
            return value

    # Try enforce type conversion, if fails return the value directly
    try:
        value = main_ptype(value)
    except Exception:
        pass

    return value
