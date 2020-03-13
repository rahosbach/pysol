from datetime import datetime
from math import inf, nan

import numpy as np
import pandas as pd

import pytest
from hypothesis import given
from hypothesis.extra.pytz import timezones
from hypothesis.strategies import datetimes, floats

from pysoleng.solar_geom import calculate_solar_noon_in_local_standard_time

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
def test_calculate_solar_noon_in_local_standard_time(dt, longitude):
    """Functional test to ensure the
    calculate_solar_noon_in_local_standard_time() method
    runs properly given valid arguments."""
    assert isinstance(
        calculate_solar_noon_in_local_standard_time(
            local_standard_time=dt, longitude_degrees=longitude
        ),
        datetime,
    )


@pytest.mark.solar_geom
def test_calculate_solar_noon_in_local_standard_time_iterable():
    """Functional test to ensure the
    calculate_solar_noon_in_local_standard_time() method
    runs properly given valid iterables."""
    assert isinstance(
        calculate_solar_noon_in_local_standard_time(
            local_standard_time=[
                "February 3, 2019 10:30 AM -06:00",
                "February 10, 2019 10:30 AM -06:00",
            ],
            longitude_degrees=89.4,
        ),
        np.ndarray,
    )
    assert isinstance(
        calculate_solar_noon_in_local_standard_time(
            local_standard_time=[
                "February 3, 2019 10:30 AM -06:00",
                "February 10, 2019 10:30 AM -06:00",
            ],
            longitude_degrees=89.4,
        )[0],
        datetime,
    )


@pytest.mark.solar_geom
def test_known_values():
    """Run a test with a known answer to ensure
    calculate_solar_noon_in_local_standard_time()
    is giving the expected output (good to within 10 seconds).

    These known values are taken (approximately) from:
    http://www.solar-noon.com/

    """
    calculated = calculate_solar_noon_in_local_standard_time(
        local_standard_time="February 3, 2019 10:30 AM -06:00",
        longitude_degrees=89.4,
    )
    reference = pd.to_datetime("February 3, 2019 12:11:05 PM -06:00")
    assert abs((calculated - reference).total_seconds()) <= 10

    calculated = calculate_solar_noon_in_local_standard_time(
        local_standard_time="December 1, 2019 10:30 AM -06:00",
        longitude_degrees=89.4,
    )
    reference = pd.to_datetime("December 1, 2019 11:46:52 AM -06:00")
    assert abs((calculated - reference).total_seconds()) <= 10


@pytest.mark.solar_geom
def test_naive_datetime():
    """Run a test with a naive datetime object,
    which should result in a `ValueError`.
    """
    with pytest.raises(ValueError):
        assert calculate_solar_noon_in_local_standard_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=89.4,
        )


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to
    calculate_solar_noon_in_local_standard_time()."""
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_solar_noon_in_local_standard_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=nan,
        )
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_solar_noon_in_local_standard_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=inf,
        )


@pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_solar_noon_in_local_standard_time() for `longitude_degrees`."""
    with pytest.raises(ValueError):
        # Test with too-low value
        assert calculate_solar_noon_in_local_standard_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=-10,
        )
    with pytest.raises(ValueError):
        # Test with too-high value
        assert calculate_solar_noon_in_local_standard_time(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=400,
        )
