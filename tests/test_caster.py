"""Additional tests for the caster to ensure full code coverage.
"""
import pytest
def test_corner():
    from aflow.caster import cast
    assert cast("numbers", "spinD", None) is None
    assert cast("numbers", "spinD", "garbage") is None
