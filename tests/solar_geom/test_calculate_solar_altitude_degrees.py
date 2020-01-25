from hypothesis import given
from hypothesis.strategies import floats
from math import inf, nan
import pytest

from pysol.solar_geom import calculate_solar_altitude_degrees


@pytest.mark.solar_geom
@given(floats(min_value=0, max_value=90, allow_nan=False, allow_infinity=False))
def test_calculate_solar_altitude_degrees(zenith):
    """Functional test to ensure the calculate_solar_altitude_degrees() method
    runs properly given a valid zenith angle."""
    assert isinstance(calculate_solar_altitude_degrees(solar_zenith_degrees=zenith), float)


@pytest.mark.solar_geom
def test_known_values():
    """Run a test with a known answer to ensure
    calculate_solar_altitude_degrees() is giving the expected output.
    """

    assert calculate_solar_altitude_degrees(solar_zenith_degrees=0) == pytest.approx(90)
    assert calculate_solar_altitude_degrees(solar_zenith_degrees=33) == pytest.approx(57)
    assert calculate_solar_altitude_degrees(solar_zenith_degrees=67.2) == pytest.approx(22.8)


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_solar_altitude_degrees()."""
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_solar_altitude_degrees(solar_zenith_degrees="blah")
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_solar_altitude_degrees(solar_zenith_degrees=nan)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_solar_altitude_degrees(solar_zenith_degrees=inf)


@ pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_solar_altitude_degrees()."""
    with pytest.raises(ValueError):
        # Test with too-low value
        assert calculate_solar_altitude_degrees(solar_zenith_degrees=-10)
    with pytest.raises(ValueError):
        # Test with too-high value
        assert calculate_solar_altitude_degrees(solar_zenith_degrees=100)