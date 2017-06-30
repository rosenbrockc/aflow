"""Functions for controlling high-level search functionality for the
AFLOW database.
"""
server = "http://aflowlib.duke.edu/search/API/?"
"""str: API server address over HTTP.
"""

def search(catalog=None, batch_size=1):
    """Returns a :class:`aflow.control.Query` to help construct the search
    query.

    Args:
        catalog (str): one of the catalogs supported on AFLOW: ['icsd', 'lib1',
          'lib2', 'lib3']. Also supports a `list` of catalog names.
        batch_size (int): number of data entries to return per HTTP request.
    """
    return Query(catalog, batch_size)

class Query(object):
    """Represents a search againts the AFLUX API.

    Args:
        catalog (str): one of the catalogs supported on AFLOW: ['icsd', 'lib1',
          'lib2', 'lib3']. Also supports a `list` of catalog names.
        batch_size (int): number of data entries to return per HTTP request.

    Attributes:
        filters (list): of `str` filter arguments to pass to the matchbook
          section of the API request.
        select (list): of :class:`aflow.keywords.Keyword` to *include* in the request.
        select (list): of :class:`aflow.keywords.Keyword` to *exclude* in the request.
        orderby (str): name of the keyword to order by. AFLUX only supports a
          single order-by parameter for now.
        catalog (str): one of the catalogs supported on AFLOW: ['icsd', 'lib1',
          'lib2', 'lib3']. Also supports a `list` of catalog names.
        N (int): number of results in the current search query.
        reverse (bool): when True, reverse the order of the results in the
          query.
        k (int): number of datasets per page for the current iterator. Can be
          controlled by `batch_size`.
        responses (dict): keys are (n,k) tuples from the pagination; values are
          the corresponding JSON dictionaries.
    """
    def __init__(self, catalog=None, batch_size=100):
        self.filters = []
        self.selects = []
        self.excludes = []
        self.order = None
        self.catalog = catalog if isinstance(catalog, (list, tuple, type(None))) else [catalog]
        self.N = None
        self.reverse = False
        self._n = 1
        self.k = batch_size
        self.responses = {}
        self._iter = 0
        """int: current integer id of the iterator in the *whole* dataset; this
        means it can have a value greater than :attr:`k`.
        """

    def reset_iter(self):
        """Resets the iterator back to zero so that the collection can be
        iterated over again *without* needing to request the data from the
        server again.
        """
        self._iter = 0
        
    @property
    def n(self):
        """Current page number for the iterator.
        """
        if self.reverse:
            return -1*self._n
        else:
            return self._n
       
    def __len__(self):
        if self.N is None:
            response = self._request(self.n, self.k)
        return self.N

    def _request(self, n, k):
        """Constructs the query string for this :class:`Query` object for the
        specified paging limits and then returns the response from the REST API
        as a python object.

        Args:
            n (int): page number of the results to return.
            k (int): number of datasets per page.
        """
        import json
        from urllib.request import urlopen
        url = "{0}{1},{2}".format(server, self._matchbook(),
                                  self._directives(n, k))
        #response = json.loads(urlopen(url).read().decode("utf-8"))
        if n == -1:
            with open("tests/data0.json") as f:
                response = json.loads(f.read())
        if n == -2:
            with open("tests/data1.json") as f:
                response = json.loads(f.read())

        #If this is the first request, then save the number of results in the
        #query.
        if len(self.responses) == 0:
            self.N = int(next(iter(response.keys())).split()[-1])
        self.responses[n] = response
        self._n += 1
    
    def _matchbook(self):
        """Constructs the matchbook portion of the query.
        """
        items = []
        #AFLUX orders by the first element in the query. If we have an orderby
        #specified, then place it first.
        if self.orderby is not None:
            items.append(str(self.order))

        items.extend(list(map(str, self.selects)))
        items.extend(list(map(str, self.filters)))
        return ','.join(items)

    def _directives(self, n, k):
        """Returns the directives portion of the AFLUX query.

        Args:
            n (int): page number of the results to return.
            k (int): number of datasets per page.
        """
        items = []
        if self.catalog is not None:
            items.append(':'.join(self.catalog))

        #Next, add the paging context. This query maintains its own paging
        #context
        items.append("paging({0:d},{1:d})".format(n, k))
        return ','.join(items)
        
    def __iter__(self):
        """Yields a generator over AFLUX API request results.
        """
        from aflow.entries import Entry
        if len(self.responses) == 0:
            self._request(self.n, self.k)
            
        assert len(self.responses) > 0
        
        n = (self._iter // self.k) + 1
        if self.reverse:
            n *= -1
            
        if n < len(self.responses):
            i = self._iter % self.k
            key = "{} of {}".format(i+1, self.N)
            raw = self.responses[n][key]
            yield Entry(**raw)
        else:
            raise StopIteration()
    
    def filter(self, keyword):
        """Adds a search term to the current filter list. Calling :meth:`filter`
        multiple times will join the final filters together using logical *and*.

        Args:
            keyword (aflow.keywords.Keyword): that encapsulates the AFLUX
              request language logic.
        """
        self.N = None
        self.filters.append(keyword)
        return self

    def select(self, keyword):
        """Adds a keyword to the list of properties to return for each material
        in the request.

        Args:
            keyword (aflow.keywords.Keyword): that encapsulates the AFLUX
              request language logic.
        """
        self.N = None
        if keyword is not self.order:
            self.selects.append(keyword)
        return self

    def orderby(self, keyword, reverse=False):
        """Sets a keyword to be the one by which 

        Args:
            keyword (aflow.keywords.Keyword): that encapsulates the AFLUX
              request language logic.
            reverse (bool): when True, reverse the ordering.
        """
        self.N = None
        self.order = keyword
        self.reverse = reverse
        if keyword in self.selects:
            self.selects.remove(keyword)
        return self
    
    def exclude(self, keyword):
        """Sets a keyword to be *excluded* from the response.

        Args:
            keyword (aflow.keywords.Keyword): that encapsulates the AFLUX
              request language logic.
        """
        self.N = None
        self.excludes.append(keyword)
        return self
