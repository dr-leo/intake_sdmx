import intake
import intake_sdmx
import pytest

def test_ECB_EXR():
    sources = intake.open_sdmx_sources()
    assert isinstance(sources, intake_sdmx.SDMXSources)
    ecb = sources.ECB
    assert isinstance(ecb, intake_sdmx.SDMXDataflows)
    # pick the dataflow for exchange rates
    exr = ecb.EXR
    assert isinstance(exr, intake_sdmx.SDMXData)
    assert exr.name == "EXR"
    assert exr.description == "Exchange Rates"
    # check default values
    assert exr.kwargs['FREQ'] == ''
    # new instance with valid arg
    exr2 = exr(FREQ='A')
    assert exr2.kwargs['FREQ'] == 'A'
    # new instance with invalid arg
    with pytest.raises(ValueError):
        exr3 = exr(FREQ='invalid')
    
    


