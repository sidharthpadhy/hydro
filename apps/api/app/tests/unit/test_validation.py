import pytest

from app.services.validation import validate_dem_file, validate_streams_file


def test_validate_dem_file_ok():
    validate_dem_file("terrain.tif", 1024, 10)


def test_validate_dem_file_ext_error():
    with pytest.raises(ValueError):
        validate_dem_file("terrain.png", 1024, 10)


def test_validate_streams_file_ok():
    validate_streams_file("streams.kml", 1024, 10)
