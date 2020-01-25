from hypothesis import given
from hypothesis.strategies import floats
from math import inf, nan
import pytest

from pysol.solar_geom import calculate_B_degrees, calculate_declination_degrees


@pytest.mark.solar_geom
@given(floats(min_value=calculate_B_degrees(1), max_value=calculate_B_degrees(366), allow_nan=False, allow_infinity=False, exclude_min=True, exclude_max=True))
def test_calculate_declination_degrees(B):
    """Functional test to ensure the calculate_declination_degrees() method
    runs properly given a valid argument."""
    assert isinstance(calculate_declination_degrees(B_degrees=B), float)


@pytest.mark.solar_geom
def test_known_values():
    """Run a few tests with known answers to ensure
    calculate_declination_degrees() is giving the expected output.
    
    These known values are taken from Duffie & Beckman (2006)
    Table 1.6.1.
    """
    assert calculate_declination_degrees(B_degrees=calculate_B_degrees(day_number=17)) == pytest.approx(-20.903603)
    assert calculate_declination_degrees(B_degrees=calculate_B_degrees(day_number=105)) == pytest.approx(9.480771)
    assert calculate_declination_degrees(B_degrees=calculate_B_degrees(day_number=288)) == pytest.approx(-8.217747)


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_declination_degrees()."""
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_declination_degrees(B_degrees="blah")
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_declination_degrees(B_degrees=nan)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_declination_degrees(B_degrees=inf)


@ pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_declination_degrees()."""
    with pytest.raises(ValueError):
        # Test with too-low value
        assert calculate_declination_degrees(B_degrees=-10)
    with pytest.raises(ValueError):
        # Test with too-high value
        assert calculate_declination_degrees(B_degrees=1_000)