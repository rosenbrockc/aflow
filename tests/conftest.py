
@pytest.fixture
def paper():
    """Returns a search query that mimics the one shown in the paper
    for electrically-insulating heat sinks.
    """
    import aflow
    import aflow.keywords as kw
    return aflow.search(batch_size=20
        ).select(kw.agl_thermal_conductivity_300K
        ).filter(kw.Egap > 6).orderby(kw.agl_thermal_conductivity_300K, True)
