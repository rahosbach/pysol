from datetime import datetime
from hypothesis import given
from hypothesis.strategies import datetimes
import pytest

from pysoleng.utils import validate_datetime


@pytest.mark.utils
@given(datetimes())
def test_validate_datetime(dt):
    """Functional test to ensure the validate_datetime() method
    runs properly on naive datetime objects."""
    assert isinstance(validate_datetime(dt), datetime)


@pytest.mark.utils
def test_invalid_type():
    """Test to ensure a TypeError is raised when an
    invalid value is provided to validate_datetime()."""
    with pytest.raises(TypeError):
        assert validate_datetime(123)


@ pytest.mark.utils
def test_valid_string():
    """Test to ensure validate_datetime() can parse a typical
    datetime string."""
    assert isinstance(validate_datetime("January 1, 2019 12:00 PM"), datetime)


@pytest.mark.utils
def test_invalid_string():
    """Test to ensure validate_datetime() will throw a 
    ValueError with an invalid string input."""
    with pytest.raises(ValueError):
        assert validate_datetime("January 1, blah blah blah")
