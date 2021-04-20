import intake
import intake_sdmx



def test_drivers():
    sources = intake.open_sdmx_sources()
    assert isinstance(sources, intake_sdmx.SDMXSources)
    ecb_cat = sources.ECB
    assert isinstance(ecb_cat, intake_sdmx.SDMXDataflows)
    # download the dataflow definitions from ECB
    ecb_cat.read()
    # pick the dataflow for exchange rates
    exr = ecb_cat.EXR
    assert isinstance(exr, intake_sdmx.SDMXData)
    assert exr.name == "EXR"
    assert exr.description == "Exchange Rates"
# TODO: _get_schema, read, discover etc.    
    
    
    
    
    
    
    
    