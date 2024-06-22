from senseagronomy.converter import *
import pytest

def test_str2pixel_error():
    with pytest.raises(RuntimeError):
        str2pixel(["UNKNOWN_OPTION"])


def test_str2pixel_length():
    responses = str2pixel(["FILL", "DILLATED_CLOUD", "CIRRUS", "CLOUD", "CLOUD_SHADOW"])
    assert len(responses) == 5


def test_str2pixel_empty():
    assert str2pixel([]) == []


def test_str2radsat_error():
    with pytest.raises(RuntimeError):
        str2radsat(["UNKNOWN_OPTION"])


def test_str2radsat_length():
    responses = str2radsat(["B1", "B2", "B3", "B4", "B5", "B6", "B7"])
    assert len(responses) == 7


def test_str2radsat_empty():
    assert str2radsat([]) == []


def test_str2aerosol_error():
    with pytest.raises(RuntimeError):
        str2aerosol("OLI", ["UNKNOWN_OPTION"], ["UNKNOWN_OPTION"])


def test_str2aerosol_length_oli():
    responses = str2aerosol("OLI", ["FILL", "VALID_RETRIEVAL", "INTERPOLATED", "CLIMATOLOGY"], [])
    assert len(responses) == 4


def test_str2aerosol_length_tm():
    responses = str2aerosol("TM", [], ["CLOUD", "CLOUD_SHADOW", "NEAR_CLOUD"])
    assert len(responses) == 3


def test_str2aerosol_unknown_sensor():
    with pytest.raises(AttributeError):
        str2aerosol("MSS", [], [])


def test_str2aerosol_empty():
    assert str2aerosol("TM", [], []) == []
