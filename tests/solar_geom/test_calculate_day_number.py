from hypothesis import given
from hypothesis.strategies import datetimes
import pytest

from pysoleng.solar_geom import calculate_day_number


@pytest.mark.solar_geom
@given(datetimes())
def test_calculate_day_number(value):
    """Functional test to ensure the calculate_day_number() method
    runs properly on proper datetime objects."""
    assert isinstance(calculate_day_number(date=value), int)


@pytest.mark.solar_geom
def test_known_values():
    """Run a few tests with known answers to ensure
    calculate_day_number() is giving the expected output."""
    assert calculate_day_number(date="January 1, 2020") == 1
    assert calculate_day_number(date="December 31, 2019") == 365
    assert calculate_day_number(date="December 31, 2020") == 366


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError is raised when an
    invalid value is provided to calculate_day_number()."""
    with pytest.raises(TypeError):
        assert calculate_day_number(date=123)


@ pytest.mark.solar_geom
def test_valid_string():
    """Test to ensure calculate_day_number() can handle a typical
    datetime string."""
    assert isinstance(calculate_day_number(date="January 1, 2019 12:00 PM"), int)


@pytest.mark.solar_geom
def test_invalid_string():
    """Test to ensure calculate_day_number() will throw a 
    ValueError with an invalid string input."""
    with pytest.raises(ValueError):
        assert calculate_day_number(date="January 1, blah blah blah")