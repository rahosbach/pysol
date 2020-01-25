from hypothesis import given
from hypothesis.strategies import floats
from math import inf, nan
import pytest

from pysoleng.solar_geom import calculate_solar_azimuth_degrees


@pytest.mark.solar_geom
@given(floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False, exclude_min=True, exclude_max=True),
       floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False, exclude_min=True, exclude_max=True),
       floats(min_value=-23.45, max_value=23.45, allow_nan=False, allow_infinity=False, exclude_min=True, exclude_max=True))
def test_calculate_solar_azimuth_degrees(hour_angle, latitude, declination):
    """Functional test to ensure the calculate_solar_azimuth_degrees() method
    runs properly given valid arguments."""
    assert isinstance(calculate_solar_azimuth_degrees(hour_angle_degrees=hour_angle, latitude_degrees=latitude, declination_degrees=declination), float)


@pytest.mark.solar_geom
def test_known_values():
    """Run tests with knowns answer to ensure
    calculate_solar_azimuth_degrees() is giving the expected output.
    These known values come from Duffie & Beckman (2006) Example 1.6.2.
    """

    assert calculate_solar_azimuth_degrees(hour_angle_degrees=-37.5, latitude_degrees=43, declination_degrees=-14) == pytest.approx(-40.08106)
    assert calculate_solar_azimuth_degrees(hour_angle_degrees=97.5, latitude_degrees=43, declination_degrees=23.1) == pytest.approx(112.019756)


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_solar_azimuth_degrees()."""
    # `hour_angle_degrees` argument
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees="blah", latitude_degrees=43, declination_degrees=-14)
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=nan, latitude_degrees=43, declination_degrees=-14)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=inf, latitude_degrees=43, declination_degrees=-14)
    # `latitude_degrees` argument
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees="blah", declination_degrees=-14)
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=nan, declination_degrees=-14)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=inf, declination_degrees=-14)
    # `declination_degrees` argument
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=43, declination_degrees="blah")
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=43, declination_degrees=nan)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=43, declination_degrees=inf)


@ pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_solar_azimuth_degrees()."""
    # Tests with too-low values
    with pytest.raises(ValueError):
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=-200, latitude_degrees=43, declination_degrees=0)
    with pytest.raises(ValueError):
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=-100, declination_degrees=0)
    with pytest.raises(ValueError):
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=43, declination_degrees=-30)
    # Tests with too-high values
    with pytest.raises(ValueError):
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=200, latitude_degrees=43, declination_degrees=0)
    with pytest.raises(ValueError):
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=100, declination_degrees=0)
    with pytest.raises(ValueError):
        assert calculate_solar_azimuth_degrees(hour_angle_degrees=0, latitude_degrees=43, declination_degrees=30)
