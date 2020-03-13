from math import inf, nan

import numpy as np
import pytest
from hypothesis import given
from hypothesis.strategies import floats

from pysoleng.solar_geom import calculate_solar_zenith_degrees


@pytest.mark.solar_geom
@given(
    floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False),
    floats(
        min_value=-23.45,
        max_value=23.45,
        allow_nan=False,
        allow_infinity=False,
    ),
    floats(
        min_value=-180, max_value=180, allow_nan=False, allow_infinity=False
    ),
)
def test_calculate_solar_zenith_degrees(latitude, declination, hour_angle):
    """Functional test to ensure the calculate_hour_angle() method
    runs properly given valid arguments."""
    assert isinstance(
        calculate_solar_zenith_degrees(
            latitude_degrees=latitude,
            declination_degrees=declination,
            hour_angle_degrees=hour_angle,
        ),
        float,
    )


@pytest.mark.solar_geom
def test_calculate_solar_zenith_degrees_iterable():
    """Functional test to ensure the calculate_hour_angle() method
    runs properly given valid arguments."""
    assert isinstance(
        calculate_solar_zenith_degrees(
            latitude_degrees=35,
            declination_degrees=[-10, -15],
            hour_angle_degrees=[0, 10],
        ),
        np.ndarray,
    )
    assert isinstance(
        calculate_solar_zenith_degrees(
            latitude_degrees=35,
            declination_degrees=[-10, -15],
            hour_angle_degrees=[0, 10],
        )[0],
        float,
    )


@pytest.mark.solar_geom
def test_known_values():
    """Run a test with a known answer to ensure
    calculate_solar_zenith_degrees() is giving the expected output.

    These known values are taken from Duffie & Beckman (2006) Example 1.6.2.
    """

    assert calculate_solar_zenith_degrees(
        latitude_degrees=43, declination_degrees=-14, hour_angle_degrees=-37.5
    ) == pytest.approx(66.54701)
    assert calculate_solar_zenith_degrees(
        latitude_degrees=43, declination_degrees=23.1, hour_angle_degrees=97.5
    ) == pytest.approx(79.64385)


@pytest.mark.solar_geom
def test_invalid_type():
    """Test to ensure a TypeError or ValueError is raised
    when an invalid value is provided to calculate_solar_zenith_degrees()."""
    # `latitude_degrees` argument
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_solar_zenith_degrees(
            latitude_degrees="blah",
            declination_degrees=-14,
            hour_angle_degrees=-37.5,
        )
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_solar_zenith_degrees(
            latitude_degrees=nan,
            declination_degrees=-14,
            hour_angle_degrees=-37.5,
        )
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_solar_zenith_degrees(
            latitude_degrees=inf,
            declination_degrees=-14,
            hour_angle_degrees=-37.5,
        )
    # `declination_degrees` argument
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43,
            declination_degrees="blah",
            hour_angle_degrees=-37.5,
        )
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43,
            declination_degrees=nan,
            hour_angle_degrees=-37.5,
        )
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43,
            declination_degrees=inf,
            hour_angle_degrees=-37.5,
        )
    # `hour_angle_degrees` argument
    with pytest.raises(TypeError):
        # Test with string value
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43,
            declination_degrees=-14,
            hour_angle_degrees="blah",
        )
    with pytest.raises(ValueError):
        # Test with NaN value
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43,
            declination_degrees=-14,
            hour_angle_degrees=nan,
        )
    with pytest.raises(ValueError):
        # Test with infinite value
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43,
            declination_degrees=-14,
            hour_angle_degrees=inf,
        )


@pytest.mark.solar_geom
def test_invalid_range():
    """Test to ensure a ValueError is raised when a value
    outside the specified range is provided to
    calculate_solar_zenith_degrees()."""
    # Tests with too-low values
    with pytest.raises(ValueError):
        assert calculate_solar_zenith_degrees(
            latitude_degrees=-100,
            declination_degrees=-14,
            hour_angle_degrees=0,
        )
    with pytest.raises(ValueError):
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43, declination_degrees=-30, hour_angle_degrees=0
        )
    with pytest.raises(ValueError):
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43,
            declination_degrees=-14,
            hour_angle_degrees=-200,
        )
    # Tests with too-high values
    with pytest.raises(ValueError):
        assert calculate_solar_zenith_degrees(
            latitude_degrees=100, declination_degrees=-14, hour_angle_degrees=0
        )
    with pytest.raises(ValueError):
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43, declination_degrees=-30, hour_angle_degrees=0
        )
    with pytest.raises(ValueError):
        assert calculate_solar_zenith_degrees(
            latitude_degrees=43,
            declination_degrees=-14,
            hour_angle_degrees=200,
        )
