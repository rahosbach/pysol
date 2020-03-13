from datetime import datetime
import pandas as pd

import pytest
from hypothesis import given
from hypothesis.strategies import datetimes

from pysoleng.utils import validate_datetime


@pytest.mark.utils
@given(datetimes(min_value=pd.Timestamp.min, max_value=pd.Timestamp.max))
def test_validate_datetime(dt):
    """Functional test to ensure the validate_datetime() method
    runs properly on naive datetime objects."""
    assert isinstance(validate_datetime(dt), pd.Timestamp)


@pytest.mark.utils
def test_validate_datetime_iterable():
    """Functional test to ensure the validate_datetime() method
    runs properly on naive datetime iterables."""
    iterable = [
        pd.to_datetime("January 1, 2020"),
        pd.to_datetime("January 13, 2020"),
    ]
    assert isinstance(validate_datetime(iterable), pd.DatetimeIndex)
    assert isinstance(validate_datetime(iterable)[0], pd.Timestamp)


@pytest.mark.utils
def test_valid_string():
    """Test to ensure validate_datetime() can parse a typical
    datetime string."""
    assert isinstance(
        validate_datetime("January 1, 2019 12:00 PM"), pd.Timestamp
    )


@pytest.mark.utils
def test_invalid_string():
    """Test to ensure validate_datetime() will throw a
    ValueError with an invalid string input."""
    with pytest.raises(ValueError):
        assert validate_datetime("January 1, blah blah blah")
