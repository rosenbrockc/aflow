`AFLOW` Database Entries
========================

Once an initial search has been performed using `aflow`, the results
are setup as a python generator that returns
:class:`~aflow.entries.Entry` objects. These provide immediate access
to properties specified in the search query, and lazy access to all
other properties that are available for the given material entry.

.. automodule:: aflow.entries
   :synopsis: Entry class for interacting with a single AFLOW database entry.
   :members:
