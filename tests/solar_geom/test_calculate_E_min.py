from math import inf, nan

import pytest
from hypothesis import given
from hypothesis.strategies import floats

from pysoleng.solar_geom import calculate_B_degrees, calculate_E_min


@pytest.mark.solar_geom
@given(
    floats(
        min_value=calculate_B_degrees(1),
        max_value=calculate_B_degrees(366),
        allow_nan=False,
        allow_infinity=False,
    )
)
def test_calculate_E_min(B):
    """Functional test to ensure the calculate_E_min() method
    runs properly given a valid argument."""
    assert isinstance(calculate_E_min(B_degrees=B), float)


@pytest.mark.solar_geom
def test_known_values():
    """Run a few tests with known answers to ensure
    calculate_E_min() is giving the expected output.

    These known values are taken from:
    1) Duffie & Beckman (2006) Example 1.5.1, and
    2) Estimated from Duffie & Beckman (2006) Figure 1.5.1
    """
    assert calculate_E_min(
        B_degrees=calculate_B_degrees(day_number=34)
    ) == pytest.approx(-13.488457)
    assert calculate_E_min(
        B_degrees=calculate_B_degrees(day_number=304)
    ) == pytest.approx(16.37505)


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_E_min()."""
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_E_min(B_degrees="blah")
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_E_min(B_degrees=nan)
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_E_min(B_degrees=inf)


@pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_E_min()."""
    with pytest.raises(ValueError):
        # Test with too-low value
        assert calculate_E_min(B_degrees=-10)
    with pytest.raises(ValueError):
        # Test with too-high value
        assert calculate_E_min(B_degrees=1_000)
