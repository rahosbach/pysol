from datetime import datetime
from math import inf, nan

import pandas as pd

import pytest
from hypothesis import given
from hypothesis.extra.pytz import timezones
from hypothesis.strategies import datetimes, floats

from pysoleng.solar_geom import convert_to_solar_time

# Create time zone-aware datetimes for use in testing
aware_datetimes = datetimes(
    min_value=pd.Timestamp.min + pd.DateOffset(2),
    max_value=pd.Timestamp.max - pd.DateOffset(2),
    timezones=timezones(),
)


@pytest.mark.solar_geom
@given(
    aware_datetimes,
    floats(min_value=0, max_value=360, allow_nan=False, allow_infinity=False),
)
def test_convert_to_solar_time(dt, longitude):
    """Functional test to ensure the convert_to_solar_time() method
    runs properly given valid arguments."""
    assert isinstance(
        convert_to_solar_time(
            local_standard_time=dt, longitude_degrees=longitude
        ),
        datetime,
    )


@pytest.mark.solar_geom
def test_convert_to_solar_time_iterable():
    """Functional test to ensure the convert_to_solar_time() method
    runs properly given valid interables."""
    assert isinstance(
        convert_to_solar_time(
            local_standard_time=[
                "January 1, 2020 10:00 AM -06:00",
                "January 15, 2020 10:00 AM -06:00",
            ],
            longitude_degrees=89.4,
        ),
        list,
    )
    assert isinstance(
        convert_to_solar_time(
            local_standard_time=[
                "January 1, 2020 10:00 AM -06:00",
                "January 15, 2020 10:00 AM -06:00",
            ],
            longitude_degrees=89.4,
        )[0],
        pd.Timestamp,
    )


@pytest.mark.solar_geom
def test_convert_to_solar_time_pdseries():
    """Functional test to ensure the convert_to_solar_time() method
    runs properly given a Pandas series."""
    x = pd.Series(
        pd.date_range("2020-01-01 00:00 -07:00", periods=72, freq="H")
    )
    assert isinstance(
        convert_to_solar_time(local_standard_time=x, longitude_degrees=89.4,),
        list,
    )


@pytest.mark.solar_geom
def test_known_values():
    """Run a test with a known answer to ensure
    convert_to_solar_time() is giving the expected output
    (good to within 10 seconds).

    These known values are taken from:
    1) Duffie & Beckman (2006) Example 1.5.1
    """
    calculated = convert_to_solar_time(
        local_standard_time="February 3, 2020 10:30 AM -06:00",
        longitude_degrees=89.4,
    )
    reference = pd.to_datetime("February 3, 2020 10:19 AM -06:00")
    assert abs((calculated - reference).total_seconds()) <= 10


@pytest.mark.solar_geom
def test_naive_datetime():
    """Run a test with a naive datetime object,
    which should result in a `ValueError`.
    """
    with pytest.raises(ValueError):
        assert convert_to_solar_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=89.4,
        )
    x = pd.Series(pd.date_range("2020-01-01 00:00", periods=72, freq="H"))
    with pytest.raises(ValueError):
        assert convert_to_solar_time(
            local_standard_time=x, longitude_degrees=89.4
        )


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to convert_to_solar_time()."""
    with pytest.raises(ValueError):
        # Test with NaN value
        assert convert_to_solar_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=nan,
        )
    with pytest.raises(ValueError):
        # Test with infinite value
        assert convert_to_solar_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=inf,
        )


@pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    convert_to_solar_time() for `longitude_degrees`."""
    with pytest.raises(ValueError):
        # Test with too-low value
        assert convert_to_solar_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=-10,
        )
    with pytest.raises(ValueError):
        # Test with too-high value
        assert convert_to_solar_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=400,
        )
