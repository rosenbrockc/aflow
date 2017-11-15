"""Implements classes to represent each keyword with overloaded
operators to make querying with AFLUX intuitive.
"""
from six import string_types
import numpy

_all_keywords = []
"""list: of `str` keyword names for which class instances exist within
this module.
"""

def load(target):
    """Loads all keywords into the specified target dictionary.
    """
    import sys
    self = sys.modules[__name__]    
    _find_all()

    for n in _all_keywords:
        cls = getattr(self, n)
        target[n] = cls

def _find_all():
    """Finds the names of all keywords supported in this module.
    """
    #Get a reference to the module and its global keyword cache.
    global _all_keywords    
    if len(_all_keywords) == 0:
        import sys
        import inspect
        self = sys.modules[__name__]
        for n, o in inspect.getmembers(self):
            if isinstance(o, Keyword):
                _all_keywords.append(n)    

def reset():
    """Resets all the keyword instances internal states so that they
    can be re-used for a new query.
    """
    import sys
    self = sys.modules[__name__]
    _find_all()
    
    for n in _all_keywords:
        cls = getattr(self, n)
        cls.state = []
        cls.cache = []

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

    def __hash__(self):
        return hash(self.name)
        
    def __str__(self):
        if len(self.state) == 1:
            s = self.state[0]
        elif len(self.cache) == 1:
            s = self.cache[0]
        else:
            return self.name

        if len(self.classes) == 1:
            return "{0}({1})".format(self.name, s)
        else:
            return s
        
    def __lt__(self, other):
        if isinstance(other, string_types):
            self.cache.append("*'{0}'".format(other))
        else:
            self.cache.append("*{0}".format(other))
        return self
            
    def __gt__(self, other):
        if isinstance(other, string_types):
            self.cache.append("'{0}'*".format(other))
        else:
            self.cache.append("{0}*".format(other))
        return self

    def __mod__(self, other):
        assert isinstance(other, string_types)
        self.cache.append("*'{0}'*".format(other))
        return self
    
    def __eq__(self, other):
        if isinstance(other, string_types):
            self.cache.append("'{0}'".format(other))
        else:
            self.cache.append("{0}".format(other))
        return self

    def _generic_combine(self, other, token):
        if other is self:
            #We need to do some special handling. We shouldn't have
            #more than two entries in cache; otherwise something went
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
            #if ':' in s or ',' in s:
            s = "{0}({1})".format(self.name, s)
                
            o = None
            if len(other.state) == 1 and len(other.cache) == 0:
                o = other.state[0]
            elif len(other.state) == 0 and len(other.cache) == 1:
                o = other.cache[0]
            #if ':' in o or ',' in o:
            o = "{0}({1})".format(other.name, o)

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
        assert len(self.state) == 1 or len(self.cache) == 1
        #The two uncovered cases below are coded for completeness, but we don't
        #have any tests to trigger them; i.e., they don't come up in normal
        #operations.
        if len(self.state) == 1:
            if '!' in self.state[0]:
                self.state[0] = self.state[0].replace('!', '')
            elif '(' in self.state[0]:
                self.state[0] = self.state[0].replace('(', "(!")
            else:# pragma: no cover
                self.state[0] = '!' + self.state[0]
        elif len(self.cache) == 1:
            if '!' in self.cache[0]:
                self.cache[0] = self.cache[0].replace('!', '')
            elif '(' in self.cache[0]:# pragma: no cover
                self.cache[0] = self.cache[0].replace('(', "(!")
            else:
                self.cache[0] = '!' + self.cache[0]
        return self    
    
{% for keyword, metadata in keywords.items() %}    
class _{{keyword}}(Keyword):
    """{{metadata.title}} (`{{metadata.inclusion}}`). Units: `{{metadata.units}}`.
    
    {% if metadata.status != "production" -%}
    .. warning:: This keyword is still listed as development level. Use it
      knowing that it is subject to change or removal.

    {%- endif %}

    Returns:
        {%- if "customdoc" in metadata %}
        {{metadata["customdoc"]|indent(12, False)}}
        {%- else %}
        {{metadata.ptype}}: {{metadata.description|indent(12, False)}}
        {% endif %}
    """
    name = "{{keyword}}"
    ptype = {{metadata.ptype}}
    atype = "{{metadata.type}}"

{{keyword}} = _{{keyword}}()
{% endfor %}
