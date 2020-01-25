from hypothesis import given
from hypothesis.strategies import floats
from math import inf, nan
import pytest

from pysol.solar_geom import calculate_B_degrees, calculate_G_on_W_m2


@pytest.mark.solar_geom
@given(floats(min_value=calculate_B_degrees(1), max_value=calculate_B_degrees(366), allow_nan=False, allow_infinity=False),   
       floats(min_value=0, allow_nan=False, allow_infinity=False))
def test_calculate_G_on_W_m2(B, Gsc):
    """Functional test to ensure the calculate_G_on_W_m2() method
    runs properly given valid arguments."""
    assert isinstance(calculate_G_on_W_m2(B_degrees=B, G_sc=Gsc), float)


@pytest.mark.solar_geom
def test_known_values():
    """Run a few tests with known answers to ensure
    calculate_G_on_W_m2() is giving the expected output.
    
    These known values are estimated from Duffie & Beckman (2006) Figure 1.4.1.
    """
    assert calculate_G_on_W_m2(B_degrees=calculate_B_degrees(1), G_sc=1_367) == pytest.approx(1_414.9134)
    assert calculate_G_on_W_m2(B_degrees=calculate_B_degrees(180), G_sc=1_367) == pytest.approx(1_321.5236)


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_G_on_W_m2()."""
    with pytest.raises(TypeError):
        # Test with string value for `B_degrees`
        assert calculate_G_on_W_m2(B_degrees="blah", G_sc=1_367)
    with pytest.raises(TypeError):
        # Test with string value for `G_sc`
        assert calculate_G_on_W_m2(B_degrees=200, G_sc="blah")
    with pytest.raises(ValueError):
        # Test with NaN value for `B_degrees`
        assert calculate_G_on_W_m2(B_degrees=nan, G_sc=1_367)
    with pytest.raises(ValueError):
        # Test with NaN value for `G_sc`
        assert calculate_G_on_W_m2(B_degrees=200, G_sc=nan)
    with pytest.raises(ValueError):
        # Test with infinite value for `B_degrees`
        assert calculate_G_on_W_m2(B_degrees=inf, G_sc=1_367)
    with pytest.raises(ValueError):
        # Test with infinite value for `G_sc`
        assert calculate_G_on_W_m2(B_degrees=200, G_sc=inf)


@ pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_G_on_W_m2()."""
    with pytest.raises(ValueError):
        # Test with too-low value for `B_degrees`
        assert calculate_G_on_W_m2(B_degrees=-10, G_sc=1_367)
    with pytest.raises(ValueError):
        # Test with too-low value for `G_sc`
        assert calculate_G_on_W_m2(B_degrees=200, G_sc=-10)
    with pytest.raises(ValueError):
        # Test with too-high value for `B_degrees`
        assert calculate_G_on_W_m2(B_degrees=1_000, G_sc=1_367)