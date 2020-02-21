import pytest
from hypothesis import given
from hypothesis.strategies import floats

from pysoleng.utils import validate_numeric_value


@pytest.mark.utils
@given(
    floats(
        min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
    )
)
def test_validate_numeric_value(value):
    """Functional test to ensure validate_numeric_value()
    runs properly for range-valid values."""
    validate_numeric_value(value, minimum=-1e6, maximum=1e6)


@pytest.mark.utils
def test_invalid_type():
    """Test to ensure a TypeError is thrown when a
    non-numeric value is provided."""
    with pytest.raises(TypeError):
        assert validate_numeric_value("blah", minimum=0, maximum=10)


@pytest.mark.utils
def test_no_requirements():
    """Test to ensure that no errors are thrown when a
    numeric value is provided with no `minimum` or
    `maximum`."""
    validate_numeric_value(10, minimum=None, maximum=None)


@pytest.mark.utils
def test_outside_range():
    """Test to ensure that a ValueError is thrown
    when a value less than `minimum` or greater than
    `maximum` is provided."""
    with pytest.raises(ValueError):
        # Check `minimum` requirement.
        assert validate_numeric_value(-10, minimum=0, maximum=10)
    with pytest.raises(ValueError):
        # Check `maximum` requirement
        assert validate_numeric_value(10, minimum=0, maximum=9)
