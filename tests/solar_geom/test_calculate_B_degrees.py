from datetime import datetime
from hypothesis import given
from hypothesis.strategies import integers
from math import inf, nan
import pytest

from pysol.solar_geom import calculate_B_degrees


@pytest.mark.solar_geom
@given(integers(min_value=1, max_value=366))
def test_calculate_B_degrees(value):
    """Functional test to ensure the calculate_B_degrees() method
    runs properly on integer values in the correct range."""
    assert isinstance(calculate_B_degrees(day_number=value), float)


@pytest.mark.solar_geom
def test_known_values():
    """Run a few tests with known answers to ensure
    calculate_B_degrees() is giving the expected output."""
    assert calculate_B_degrees(day_number=1) == 0
    assert calculate_B_degrees(day_number=74) == 72
    assert calculate_B_degrees(day_number=366) == 360


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_B_degrees()."""
    with pytest.raises(TypeError):
        # Test with float value
        assert calculate_B_degrees(day_number=123.5)
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_B_degrees(day_number=nan)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_B_degrees(day_number=inf)
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_B_degrees(day_number="blah")
    with pytest.raises(TypeError):
        # Test with datetime object
        assert calculate_B_degrees(day_number=datetime(2020, 1, 1))


@ pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_B_degrees()."""
    with pytest.raises(ValueError):
        # Test with too-low value
        assert calculate_B_degrees(day_number=-10)
    with pytest.raises(ValueError):
        # Test with too-high value
        assert calculate_B_degrees(day_number=1_000)