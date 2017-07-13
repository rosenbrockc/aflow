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
        return cast(atype, attr, value)
    else:
        return value

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

    def _lazy_load(self, keyword):
        """Loads the value of the specified keyword via HTTP request against the
        AFLUX API, if it isn't already present on the object.

        Args:
            keyword (str): name of the keyword to retrieve for this entry.
        """
        if keyword not in self.keywords:
            return
        
        if keyword in self.attributes:
            return self.attributes[keyword]
        else:
            import requests
            import json
            url = "http://{0}?{1}".format(self.keywords["aurl"], keyword)
            r = requests.get(url)

            #We need to coerce the string returned from aflow into the
            #appropriate python format.
            result = _val_from_str(keyword, r.text)
            self.attributes[keyword] = result
            return result
    {% for keyword, metadata in keywords.items() %}
    @property
    def {{keyword}}(self):
        """{{metadata.title}} (`{{metadata.inclusion}}`). Units: `{{metadata.units}}`.
        
        {% if metadata.status != "production" -%}
        .. warning:: This keyword is still listed as development level. Use it
          knowing that it is subject to change or removal.

        {%- endif %}
        {% if "verification" in metadata -%}
        .. note:: The following verifications are available for this
          keyword. They are exposed as additional methods on this object.
          {% for verify in metadata.verification %}
          - :meth:`{{verify}}`
          {%- endfor %}

        {%- endif %}

        Returns:
            {{metadata.ptype}}: {{metadata.description|indent(12, False)}}
        {% if "example" in metadata %}
        Examples:
            You can expect the *content* of the result to be something like:

            `{{metadata.example}}`
        {% endif -%}
        """
        return self._lazy_load("{{keyword}}")    
    {% endfor %}
