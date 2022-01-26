from pathlib import Path

import intake
import pandas as pd
import pytest
from pandasdmx import Request, read_sdmx

import intake_sdmx

data_path = Path(__file__).parent.joinpath("data")


def filepath(name):
    return data_path.joinpath(name)


@pytest.fixture
def source():
    return intake.open_sdmx_sources()


@pytest.fixture
def ecb(source, mocker):
    mocker.patch.object(
        Request, "get", return_value=read_sdmx(filepath("ecb_dataflows.xml"))
    )
    return source.ECB


@pytest.fixture
def mock_exr(ecb, mocker):
    return mocker.patch.object(
        Request, "get", return_value=read_sdmx(filepath("exr_flow.xml"))
    )


@pytest.fixture
def exr(ecb, mock_exr):
    return ecb.EXR


def test_source(source):
    assert isinstance(source, intake_sdmx.SDMXSources)
    assert "ECB" in source


def test_ecb(ecb):
    assert isinstance(ecb, intake_sdmx.SDMXDataflows)
    assert "EXR" in ecb
    assert "Exchange Rates" in ecb


def test_exr(exr):
    assert isinstance(exr, intake_sdmx.SDMXData)
    assert exr.name == "EXR"
    assert exr.description == "Exchange Rates"
    # check default values
    assert exr.kwargs["FREQ"] == ["*"]
    # new instance with valid arg
    exr2 = exr(FREQ=["A"], CURRENCY=["USD", "JPY"])
    assert exr2.kwargs["FREQ"] == ["A"]
    assert exr2.kwargs["CURRENCY"] == ["USD", "JPY"]
    # new instance with invalid arg
    with pytest.raises(ValueError):
        exr3 = exr(FREQ=["X"], CURRENCY=["USD", "JPY"])


def test_exr_by_name(ecb, mock_exr):
    exr4 = ecb["Exchange Rates"]
    assert isinstance(exr4, intake_sdmx.SDMXData)
    assert exr4.name == "EXR"


@pytest.fixture
def dsd(exr):
    flow_id = exr.metadata["dataflow_id"]
    flow_msg = read_sdmx(filepath("exr_flow.xml"))
    return flow_msg.dataflow[flow_id].structure


@pytest.fixture
def mock_get(dsd, mocker):
    return mocker.patch.object(
        Request, "get", return_value=read_sdmx(filepath("exr_data.xml"), dsd=dsd)
    )


@pytest.fixture
def exr_data(exr, mock_get, dsd):
    return exr(CURRENCY=["USD", "JPY"], index_type="period").read()


def test_exr_read(exr_data):
    assert exr_data.shape == (13, 12)
    assert isinstance(exr_data.index, pd.PeriodIndex)


def test_params(exr, mock_get):
    msg = exr(CURRENCY=["USD", "JPY"]).read()
    cur_key = {"CURRENCY": ["USD", "JPY"]}
    assert mock_get.call_args[1]["key"] == cur_key
    # codes by name
    msg = exr(CURRENCY=["US dollar", "Japanese yen"]).read()
    assert mock_get.call_args[1]["key"] == cur_key
    # Duplicate values raise error
    with pytest.raises(ValueError):
        msg = exr(CURRENCY=["US dollar", "USD"]).read()


def test_search(ecb):
    ecb_rates = ecb.search("rates")
    l = list(ecb_rates)
    assert l[0] == "EXR"
    assert l[1] == "Exchange Rates"
    assert len(l) == 4


def test_entry_points(mock_exr):
    src = intake.open_sdmx_sources()
    assert isinstance(src, intake_sdmx.SDMXSources)
    src2 = intake_sdmx.SDMXSources()
    assert src.yaml() == src2.yaml()
    # writing such tests for other drivers would be more tedious.
