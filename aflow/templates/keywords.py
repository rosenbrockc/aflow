"""Implements classes to represent each keyword with overloaded
operators to make querying with AFLUX intuitive.
"""
from six import string_types
import numpy

class Keyword(object):
    """Represents an abstract keyword that can be sub-classed for a
    specific material attribute. This class also represents logical
    operators that define search queries. The combination of two
    keywords with a logical operator produces one more keyword, but
    which has its :attr:`state` altered.

    Args:
        state (str): current query state of this keyword (combination).

    Attributes:
        state (list): of `str` *composite* queries for this keyword (combination).
        ptype (type): python type that values for this keyword will have.
        name (str): keyword name to use in the AFLUX request.
        cache (list): of `str` *simple* operator comparisons.
        classes (set): of `str` keyword names that have been combined into the
          current keyword.
    """
    name = None
    ptype = None
    atype = None
    
    def __init__(self, state=None):
        self.state = state if state is not None else []
        self.cache = []
        self.classes = set([self.name])

    def __str__(self):
        if len(self.state) == 1:
            return self.state[0]
        elif len(self.cache) == 1:
            return self.cache[0]
        else:
            return self.name
        
    def __getattr__(self, attr):
        if attr in self.attributes:
            return self.attributes[attr]
        
    def __lt__(self, other):
        if isinstance(other, string_types):
            self.cache.append("{0}(*'{1}')".format(self.name, other))
        else:
            self.cache.append("{0}(*{1})".format(self.name, other))
        return self
            
    def __gt__(self, other):
        if isinstance(other, string_types):
            self.cache.append("{0}('{1}'*)".format(self.name, other))
        else:
            self.cache.append("{0}({1}*)".format(self.name, other))
        return self

    def __contains__(self, other):
        assert isinstance(other, string_types)
        self.cache.append("{0}(*'{1}'*)".format(self.name, other))
    
    def __eq__(self, other):
        if isinstance(other, string_types):
            self.cache.append("{0}('{1}')".format(self.name, other))
        else:
            self.cache.append("{0}({1})".format(self.name, other))
        return self

    def _generic_combine(self, other, token):
        if other is self:
            #We need to do some special handling. We shouldn't have
            #more than two entries in state; otherwise something went
            #wrong.
            if len(self.cache) == 2:
                args = self.cache[0], token, self.cache[1]
                self.state.append("{0}{1}{2}".format(*args))
            elif len(self.cache) == 1 and len(self.state) == 1:
                args = self.cache[0], token, self.state[0]
                self.state = ["{0}{1}({2})".format(*args)]
            elif len(self.state) == 2:
                args = self.state[0], token, self.state[1]
                self.state = ["({0}){1}({2})".format(*args)]
            else:
                raise ValueError("Inconsistent operators; check your parenthesis.")
                
            self.cache = []
            return self
        else:
            #Just combine the two together into a new keyword that has
            #the combined state.
            s = None
            if len(self.state) == 1 and len(self.cache) == 0:
                s = self.state[0]
            elif len(self.state) == 0 and len(self.cache) == 1:
                s = self.cache[0]

            o = None
            if len(other.state) == 1 and len(other.cache) == 0:
                o = other.state[0]
            elif len(other.state) == 0 and len(other.cache) == 1:
                o = other.cache[0]
            
            assert s is not None
            assert o is not None            
            result = Keyword(["{0}{1}{2}".format(s, token, o)])
            result.classes = self.classes | other.classes
            return result
    
    def __and__(self, other):
        return self._generic_combine(other, ',')
        
    def __or__(self, other):
        return self._generic_combine(other, ':')

    def __invert__(self):
        assert len(self.state) <= 1
        if len(self.state) == 1:
            if '!' in self.state[0]:
                self.state[0] = self.state[0].replace('!', '')
            else:
                self.state[0] = self.state[0].replace('(', "(!")
        return self
    
{% for keyword, metadata in keywords.items() %}    
class _{{keyword}}(Keyword):
    """{{metadata.title}} (`{{metadata.inclusion}}`). Units: `{{metadata.units}}`.
    
    {% if metadata.status != "production" -%}
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    {%- endif %}

    Returns:
        {{metadata.ptype}}: {{metadata.description|indent(12, False)}}
    """
    name = "{{keyword}}"
    ptype = {{metadata.ptype}}
    atype = "{{metadata.type}}"

{{keyword}} = _{{keyword}}()
{% endfor %}
