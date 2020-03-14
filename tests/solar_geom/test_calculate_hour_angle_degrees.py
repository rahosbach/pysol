from math import inf, nan

import pandas as pd

import numpy as np
import pytest
from hypothesis import given
from hypothesis.extra.pytz import timezones
from hypothesis.strategies import datetimes, floats

from pysoleng.solar_geom import calculate_hour_angle_degrees

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
def test_calculate_hour_angle(dt, longitude):
    """Functional test to ensure the calculate_hour_angle() method
    runs properly given valid arguments."""
    assert isinstance(
        calculate_hour_angle_degrees(
            local_standard_time=dt, longitude_degrees=longitude
        ),
        float,
    )


@pytest.mark.solar_geom
def test_calculate_hour_angle_iterable():
    """Functional test to ensure the calculate_hour_angle() method
    runs properly given valid iterables."""
    assert isinstance(
        calculate_hour_angle_degrees(
            local_standard_time=[
                "February 13, 2020 10:42 AM -06:00",
                "February 23, 2020 10:42 AM -06:00",
            ],
            longitude_degrees=89.4,
        ),
        np.ndarray,
    )
    assert isinstance(
        calculate_hour_angle_degrees(
            local_standard_time=[
                "February 13, 2020 10:42 AM -06:00",
                "February 23, 2020 10:42 AM -06:00",
            ],
            longitude_degrees=89.4,
        )[0],
        float,
    )


@pytest.mark.solar_geom
def test_known_values():
    """Run a test with a known answer to ensure
    calculate_hour_angle() is giving the expected output.

    These known values are taken from:
    1) Duffie & Beckman (2006) Example 1.6.1
    """

    """`local_standard_time` here corresponds to
    10:30 AM solar time for the day and location."""
    assert calculate_hour_angle_degrees(
        local_standard_time="February 13, 2020 10:42 AM -06:00",
        longitude_degrees=89.4,
    ) == pytest.approx(-22.46533)


@pytest.mark.solar_geom
def test_naive_datetime():
    """Run a test with a naive datetime object,
    which should result in a `ValueError`.
    """
    with pytest.raises(ValueError):
        assert calculate_hour_angle_degrees(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=89.4,
        )


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_hour_angle_degrees()."""
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_hour_angle_degrees(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=nan,
        )
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_hour_angle_degrees(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=inf,
        )


@pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_hour_angle_degrees() for `longitude_degrees`."""
    with pytest.raises(ValueError):
        # Test with too-low value
        assert calculate_hour_angle_degrees(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=-10,
        )
    with pytest.raises(ValueError):
        # Test with too-high value
        assert calculate_hour_angle_degrees(
            local_standard_time="February 3, 2020 10:30 AM",
            longitude_degrees=400,
        )
