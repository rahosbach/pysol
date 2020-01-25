from hypothesis import given
from hypothesis.strategies import floats
from math import inf, nan
import pytest

from pysoleng.solar_geom import calculate_air_mass


@pytest.mark.solar_geom
@given(floats(min_value=0, max_value=90, allow_nan=False, allow_infinity=False), floats(min_value=-413, allow_nan=False, allow_infinity=False))
def test_calculate_air_mass(zenith, altitude):
    """Functional test to ensure the calculate_air_mass() method
    runs properly given valid arguments."""
    assert isinstance(calculate_air_mass(solar_zenith_degrees=zenith, site_altitude_m=altitude), float)


@pytest.mark.solar_geom
def test_known_values():
    """Run a test with a known answer to ensure
    calculate_air_mass() is giving the expected output.
    """
    assert calculate_air_mass(solar_zenith_degrees=0, site_altitude_m=0) == pytest.approx(0.999709)
    assert calculate_air_mass(solar_zenith_degrees=60, site_altitude_m=0) == pytest.approx(1.994244)


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_air_mass()."""
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_air_mass(solar_zenith_degrees="blah", site_altitude_m=0)
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_air_mass(solar_zenith_degrees=nan, site_altitude_m=0)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_air_mass(solar_zenith_degrees=inf, site_altitude_m=0)
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_air_mass(solar_zenith_degrees=45, site_altitude_m="blah")
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_air_mass(solar_zenith_degrees=45, site_altitude_m=nan)


@ pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_air_mass()."""
    with pytest.raises(ValueError):
        # Test with too-low value for `solar_zenith_degrees`
        assert calculate_air_mass(solar_zenith_degrees=-10, site_altitude_m=0)
    with pytest.raises(ValueError):
        # Test with too-high value for `solar_zenith_degrees`
        assert calculate_air_mass(solar_zenith_degrees=100, site_altitude_m=0)
    with pytest.raises(ValueError):
        # Test with too-low value for `site_altitude_m`
        assert calculate_air_mass(solar_zenith_degrees=45, site_altitude_m=-500)