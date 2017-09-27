Code Templating Generators
==========================

Because the number and type of keywords provided in AFLOW is subject
to change, we opted for a dynamic generation of the :doc:`keywords`
and :doc:`entries`. The generators make a request to the schema
introspection of AFLOW API to determine what's available and how it is
documented. This provides data to generate custom modules for the
`aflow` python library.

.. automodule:: aflow.generators
   :synopsis: Dynamic code generators for the supported AFLOW keywords.
   :members:

