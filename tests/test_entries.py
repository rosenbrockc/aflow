"""Tests that :class:`aflow.entries.Entry` objects have the correct
attributes and that lazy fetching works correctly.
"""
def test_fetched(paper):
    """Makes sure that the attributes included in the original query
    are returned correctly.
    """
    paper.reset_iter()
