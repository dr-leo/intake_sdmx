import intake
import intake_sdmx
from pandasdmx import Request, read_sdmx
import pandas as pd
import pytest
from pathlib import Path

data_path = Path(__file__).parent.joinpath("data")


def filepath(name):
    return data_path.joinpath(name)


@pytest.fixture
def source():
    return intake.open_sdmx()


@pytest.fixture
def ecb(source, mocker):
    mocker.patch.object(
        Request, "get", return_value=read_sdmx(filepath("ecb_dataflows.xml"))
    )
    return source.ECB


@pytest.fixture
def exr(ecb, mocker):
    mocker.patch.object(
        Request, "get", return_value=read_sdmx(filepath("exr_flow.xml"))
    )
    return ecb.EXR


def test_source(source):
    assert isinstance(source, intake_sdmx.SDMXSources)


def test_ecb(ecb):
    assert isinstance(ecb, intake_sdmx.SDMXDataflows)
    assert "EXR" in ecb
    assert "Exchange Rates" in ecb


def test_exr(exr, ecb):
    assert isinstance(exr, intake_sdmx.SDMXData)
    assert exr.name == "EXR"
    assert exr.description == "Exchange Rates"
    # check default values
    assert exr.kwargs["FREQ"] == "n/a"
    # new instance with valid arg
    exr2 = exr(FREQ="A")
    assert exr2.kwargs["FREQ"] == "A"
    # new instance with invalid arg
    with pytest.raises(ValueError):
        exr3 = exr(FREQ="invalid")

def test_exr_many_codes(exr, ecb):
    cur_str = 'JPY+USD+CHF'
    exr2=exr(CURRENCY=cur_str)
    assert exr2.kwargs['CURRENCY'] == cur_str  

@pytest.fixture
def exr_data(exr, mocker):
    flow_id = exr.metadata["dataflow_id"]
    flow_msg = read_sdmx(filepath("exr_flow.xml"))
    dsd = flow_msg.dataflow[flow_id].structure
    mocker.patch.object(
        Request, "get", return_value=read_sdmx(filepath("exr_data.xml"), dsd=dsd)
    )
    return exr(index_type="period").read()


def test_exr_read(exr_data):
    assert exr_data.shape == (13, 12)
    assert isinstance(exr_data.index, pd.PeriodIndex)


def test_search(ecb):
    ecb_rates = ecb.search("rates")
    l = list(ecb_rates)
    assert l[0] == "EXR"
    assert l[1] == "Exchange Rates"
    assert len(l) == 4
