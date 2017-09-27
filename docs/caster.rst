`AFLOW` Custom Deserializers
============================

Unfortunately, the AFLOW library uses a custom-built serialization
language for its keywords. This means that it isn't possible to
standardize the deserialization across all :doc:`keywords`. Instead,
we have to implement custom deserialization for some of the keyword
types.

.. automodule:: aflow.caster
   :synopsis: Functions for deserializing the JSON representations of
	      various keyword values.
   :members:
