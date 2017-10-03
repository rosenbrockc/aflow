[![Build Status](https://travis-ci.org/rosenbrockc/aflow.svg?branch=master)](https://travis-ci.org/rosenbrockc/aflow) [![Coverage Status](https://coveralls.io/repos/github/rosenbrockc/aflow/badge.svg?branch=master)](https://coveralls.io/github/rosenbrockc/aflow?branch=master)

# `AFLOW` Python API

Python API wrapping the AFLUX API language for AFLOW library. _Note:_ This is not an official repo of the AFLOW consortium and is not maintained by them. [API Documentation](https://rosenbrockc.github.io/aflow/).

If you use this package, please cite it:

```
@ARTICLE{2017arXiv171000813R,
   author = {{Rosenbrock}, C.~W.},
    title = "{A Practical Python API for Querying AFLOWLIB}",
  journal = {ArXiv e-prints},
archivePrefix = "arXiv",
   eprint = {1710.00813},
 primaryClass = "cs.DB",
 keywords = {Computer Science - Databases},
     year = 2017,
    month = sep,
   adsurl = {http://adsabs.harvard.edu/abs/2017arXiv171000813R},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}
```

## Quickstart

Install `aflow` from the python package index:

```
pip install aflow
```

Open an ipython notebook or terminal and execute the query from the paper:

```python
from aflow import *

result = search(batch_size=20
        ).select(K.agl_thermal_conductivity_300K
        ).filter(K.Egap > 6).orderby(K.agl_thermal_conductivity_300K, True)

# Now, you can just iterate over the results.
for entry in result:
    print(entry.Egap)
```

`aflow` supports lazy evaluation. This means that if you didn't ask for a particular property during the initial query, you can just ask for it later and the request will happen transparently in the background.


