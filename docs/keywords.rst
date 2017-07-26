`AFLOW` Database Keywords
=========================

The `AFLOW` database supports a fixed number of keywords related to
the calculated physical properties. The generators create a
sub-classed :class:`~aflow.keywords.Keyword` object that supports
logical operations supported by the AFLUX standard.

.. note:: Because of the way the operators are overloaded, each
   comparison needs to be placed in its own set of parenthesis to
   ensure that the order of operators is respected correctly. See
   :doc:`examples`.
   
The :class:`~aflow.keywords.Keyword` class provides the following
operators:

1. `>` and `<` behave as expected. However, these are overloaded for
   string comparisons in the spirit of the AFLUX endpoint. For example
   `author < "curtarolo"` will match `*curtarolo` and `author >
   "curtarolo" will match `curtarolo*`.
2. `==` behaves as expected for all keywords.
3. `%` allows for string searches. `author % "curtarolo"` matches
   `*curtarolo*`.
4. `~` inverts the filter (equivalent to a boolean `not`).
5. `&` is the logical `and` between two conditions.
6. `|` is the logical `or` between two conditions.

API Documentation
-----------------
   
.. automodule:: aflow.keywords
   :synopsis: Module allowing for logical and matching queries against
	      all supported AFLOW keywords.
   :members:
