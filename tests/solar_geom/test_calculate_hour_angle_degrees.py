from dateutil.parser import parse
from hypothesis import given
from hypothesis.extra.pytz import timezones
from hypothesis.strategies import datetimes, floats
from math import inf, nan
import pytest

from pysoleng.solar_geom import calculate_hour_angle_degrees


# Create time zone-aware datetimes for use in testing
aware_datetimes = datetimes(timezones=timezones())

@pytest.mark.solar_geom
@given(aware_datetimes, floats(min_value=0, max_value=360, allow_nan=False, allow_infinity=False))
def test_calculate_hour_angle(dt, longitude):
    """Functional test to ensure the calculate_hour_angle() method
    runs properly given valid arguments."""
    assert isinstance(calculate_hour_angle_degrees(local_standard_time=dt, longitude_degrees=longitude), float)


@pytest.mark.solar_geom
def test_known_values():
    """Run a test with a known answer to ensure
    calculate_hour_angle() is giving the expected output.
    
    These known values are taken from:
    1) Duffie & Beckman (2006) Example 1.6.1
    """

    # `local_standard_time` here corresponds to 10:30 AM solar time for the day and location
    assert calculate_hour_angle_degrees(local_standard_time="February 13, 2020 10:42 AM -06:00", longitude_degrees=89.4) == pytest.approx(-22.46533)


@pytest.mark.solar_geom
def test_naive_datetime():
    """Run a test with a naive datetime object,
    which should result in a `ValueError`.
    """
    with pytest.raises(ValueError):
        assert calculate_hour_angle_degrees(local_standard_time=parse("February 3, 2020 10:30 AM"), longitude_degrees=89.4)


@pytest.mark.solar_geom
def test_no_date_given():
    """Run a test with an object that only includes
    a time, with no date.  This should throw a 
    warning.
    """
    with pytest.warns(UserWarning):
        assert calculate_hour_angle_degrees(local_standard_time=parse("10:30 AM -06:00"), longitude_degrees=89.4)


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_hour_angle_degrees()."""
    with pytest.raises(ValueError):
        # Test with string value
        assert calculate_hour_angle_degrees(local_standard_time="blah", longitude_degrees=89.4)
    with pytest.raises(TypeError):
        # Test with float value
        assert calculate_hour_angle_degrees(local_standard_time=21.0, longitude_degrees=89.4)
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_hour_angle_degrees(local_standard_time=parse("February 3, 2020 10:30 AM"), longitude_degrees=nan)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_hour_angle_degrees(local_standard_time=parse("February 3, 2020 10:30 AM"), longitude_degrees=inf)


@ pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_hour_angle_degrees() for `longitude_degrees`."""
    with pytest.raises(ValueError):
        # Test with too-low value
        assert calculate_hour_angle_degrees(local_standard_time=parse("February 3, 2020 10:30 AM"), longitude_degrees=-10)
    with pytest.raises(ValueError):
        # Test with too-high value
        assert calculate_hour_angle_degrees(local_standard_time=parse("February 3, 2020 10:30 AM"), longitude_degrees=400)