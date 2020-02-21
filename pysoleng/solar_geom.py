from datetime import datetime, timedelta
from math import acos, copysign, cos, degrees, exp, pi, radians, sin
from typing import Union
from warnings import warn

from pysoleng.utils import (
    ensure_numeric,
    validate_datetime,
    validate_numeric_value,
)


def calculate_day_number(date: Union[datetime, str]) -> int:
    """
    Method to calculate the day number of the year
    given a proper date.

    :param date: A proper datetime object or a string
        that can be parsed into a proper datetime object.

    :returns: An integer corresponding to the day number of `date`.
    """

    # Ensure `date` can be parsed into a datetime object
    date = validate_datetime(datetime_object=date)
    # Return the day number corresponding to `date`
    return date.timetuple().tm_yday


def calculate_B_degrees(day_number: int) -> float:
    """
    B is a preliminary value used in calculating the extraterrestrial
    radiation incident on the plane normal to the radiation on the
    `day_number` day of the year (G_on),
    per an equation given by Spencer (1971).

    The equation used is from Duffie & Beckman (2006)
    Equation 1.4.2.

    :param day_number: An integer representing the day number
        (of the year) of a specific date.  For example,
        January 1 corresponds to day number 1, and
        December 31 corresponds to day number 365
        (or 366, if a leap year).

    :returns: A float value, in units of degrees.
    """

    # Ensure `day_number` is an integer
    ensure_numeric(
        day_number,
        valid_types=[int],
        nan_acceptable=False,
        inf_acceptable=False,
    )
    # Ensure `day_number` is in the proper range
    validate_numeric_value(day_number, minimum=1, maximum=366)
    return (day_number - 1) * 360.0 / 365.0


def calculate_G_on_W_m2(
    B_degrees: Union[int, float], G_sc: Union[int, float] = 1_367
) -> float:
    """
    Method to calculate the extraterrestrial radiation
    incident on the plane normal to the radiation
    on a specific day of the year,
    per an equation given by Spencer (1971).

    The equation used is from Duffie & Beckman (2006)
    Equation 1.4.1b.

    :param B_degrees: A numeric value (generally a float)
        which is calculated based on the day of the year,
        in units of degrees.
    :param G_sc: The extraterrestrial solar radiation,
        assumed to be 1,367 W/m2 by default.

    :returns: A float value corresponding to `G_on` in units
        of W/m2.
    """

    # Type-check `B_degrees` and `G_sc`
    ensure_numeric(
        B_degrees,
        valid_types=[int, float],
        nan_acceptable=False,
        inf_acceptable=False,
    )
    ensure_numeric(
        G_sc,
        valid_types=[int, float],
        nan_acceptable=False,
        inf_acceptable=False,
    )

    # Range-check `B_degrees` and `G_sc`
    validate_numeric_value(
        B_degrees,
        minimum=calculate_B_degrees(1),
        maximum=calculate_B_degrees(366),
    )
    validate_numeric_value(G_sc, minimum=0, maximum=None)

    # Convert `B_degrees` to radians for use in the calculation
    B_radians = radians(B_degrees)

    # Calculate the multiplier for `G_sc`
    multiplier = (
        1.000110
        + (0.034221 * cos(B_radians))
        + (0.001280 * sin(B_radians))
        + (0.000719 * cos(2 * B_radians))
        + (0.000077 * sin(2 * B_radians))
    )
    return G_sc * multiplier


def calculate_E_min(B_degrees: Union[int, float]) -> float:
    """
    E is the equation of time (in minutes), which is
    based on the day of the year.
    The equation is given by Spencer (1971).

    The equation used is from Duffie & Beckman (2006)
    Equation 1.5.3.

    :param B_degrees: A numeric value (generally a float)
        which is calculated based on the day of the year,
        in units of degrees.

    :returns: A float value representing the equation of
        time for the given `B_degrees`, in units of minutes.
    """

    # Type-check `B_degrees`
    ensure_numeric(
        B_degrees,
        valid_types=[int, float],
        nan_acceptable=False,
        inf_acceptable=False,
    )
    # Range-check `B_degrees`
    validate_numeric_value(
        B_degrees,
        minimum=calculate_B_degrees(1),
        maximum=calculate_B_degrees(366),
    )
    # Convert `B_degrees` to radians for use in the calculation
    B_radians = radians(B_degrees)
    return 229.2 * (
        0.000075
        + (0.001868 * cos(B_radians))
        - (0.032077 * sin(B_radians))
        - (0.014615 * cos(2 * B_radians))
        - (0.04089 * sin(2 * B_radians))
    )


def convert_to_solar_time(
    local_standard_time: Union[datetime, str],
    longitude_degrees: Union[int, float],
) -> datetime:
    """
    Method to calculate solar time given a local standard timestamp
    (including date and time zone offset from UTC) and a location's
    longitude (in degrees west).

    The equation used is from Duffie & Beckman (2006)
    Equation 1.5.2.

    :param local_standard_time: A `datetime` object,
        containing a timezone offset, representing the time that
        will be converted to solar time.
    :param longitude_degrees: A numeric value representing a location's
        angular distance west of the meridian at Greenwich, England.
        `longitude_degrees` should be between 0 and 360 degrees.

    :returns: A datetime object representing the solar time
        corresponding to `local_standard_time` at the given
        `longitude_degrees`.
    """

    # Type- and range-check `longitude_degrees`
    validate_numeric_value(longitude_degrees, minimum=0, maximum=360)
    # Validate `local_standard_time`
    local_ts = validate_datetime(datetime_object=local_standard_time)

    """Ensure local_standard_time has a date, time, and time zone offset.
    Note that parse will automaticall fill in a date or time if not
    provided with the current date and 00:00 (for time)."""
    if local_ts.tzinfo is None:
        # Check that `local_ts` has a timezone offset
        raise ValueError(
            """`local_standard_time` must provide a time zone offset,
            such as `1/1/2019 12:00 PM -06:00`."""
        )
    if local_ts.date() == datetime.now().date():
        # Provide a warning if `local_ts` only contains a time, but no date
        warn(
            UserWarning(
                """A date was likely not provided in local_standard_time;
                therefore, the date has been set to today."""
            )
        )

    # Calculate offset from UTC, using timezone offset in `local_ts`
    utc_offset = local_ts.tzinfo.utcoffset(local_ts).total_seconds() // 3_600

    """Determine the standard meridian for the given `longitude_degrees`,
    which corresponds to 15 degrees per hour offset."""
    standard_meridian = 15 * abs(utc_offset)

    E = calculate_E_min(
        calculate_B_degrees(calculate_day_number(local_standard_time))
    )
    longitude_correction_mins = 4.0 * (standard_meridian - longitude_degrees)
    return local_ts + timedelta(minutes=longitude_correction_mins + E)


def calculate_declination_degrees(B_degrees: Union[int, float]) -> float:
    """
    The declination is the angular position of the sun
    at solar noon with respect to the plane of the
    equator (north is positive).  The declination angle
    must be between -23.45 and 23.45 degrees.
    The equation is from Spencer (1971).

    The equation used is from Duffie & Beckman (2006)
    Equation 1.6.1b.

    :param B_degrees: A numeric value (generally a float)
        which is calculated based on the day of the year,
        in units of degrees.

    :returns: A float value representing the
        declination angle of the sun.
    """

    # Type-check `B_degrees`
    ensure_numeric(
        B_degrees,
        valid_types=[int, float],
        nan_acceptable=False,
        inf_acceptable=False,
    )
    # Range-check `B_degrees` and `G_sc`
    validate_numeric_value(
        B_degrees,
        minimum=calculate_B_degrees(1),
        maximum=calculate_B_degrees(366),
    )

    # Convert `B_degrees` to radians for use in the calculation
    B_radians = radians(B_degrees)
    declination_degrees = (
        180.0
        / pi
        * (
            0.006918
            - (0.399912 * cos(B_radians))
            + (0.070257 * sin(B_radians))
            - (0.006758 * cos(2 * B_radians))
            + (0.000907 * sin(2 * B_radians))
            - (0.002697 * cos(3 * B_radians))
            + (0.00148 * sin(3 * B_radians))
        )
    )

    # Range-check `declination_degrees` before returning
    validate_numeric_value(declination_degrees, minimum=-23.45, maximum=23.45)

    return declination_degrees


def calculate_hour_angle_degrees(
    local_standard_time: Union[datetime, str],
    longitude_degrees: Union[int, float],
) -> float:
    """
    The hour angle is the angular displacement of the
    sun east (negative) or west (positive) of the local
    meridian due to rotation of the earth on its axis at
    15 degrees per hour, which must be between
    -180 and 180 degrees (+/- 15 degreees/hour * 12 hours).

    :param local_standard_time: A `datetime` object,
        containing a timezone offset, representing the time that
        will be converted to solar time.
    :param longitude_degrees: A numeric value representing a location's
        angular distance west of the meridian at Greenwich, England.
        `longitude_degrees` should be between 0 and 360 degrees.

    :returns: A float value representing the angular displacement
        of the sun.
    """

    # The `convert_to_solar_time()` method will validate the inputs
    solar_ts = convert_to_solar_time(local_standard_time, longitude_degrees)

    # Create a datetime object for noon on the same date as `solar_ts`
    solar_noon = datetime(
        year=solar_ts.date().year,
        month=solar_ts.date().month,
        day=solar_ts.date().day,
        hour=12,
        minute=0,
        second=0,
        tzinfo=solar_ts.tzinfo,
    )

    # Calculate the difference (in hours) and multiply by 15
    hours_diff = (solar_ts - solar_noon).total_seconds() / 3600
    hour_angle = hours_diff * 15.0

    # Valiate `hour_angle`
    validate_numeric_value(hour_angle, minimum=-180, maximum=180)
    return hour_angle


def calculate_solar_zenith_degrees(
    latitude_degrees: Union[int, float],
    declination_degrees: Union[int, float],
    hour_angle_degrees: Union[int, float],
) -> float:
    """
    The solar zenith angle is the angle between
    the vertical and the line to the sun, that is,
    the angle of incidence of beam radiation
    on a horizontal surface.  The solar zenith
    angle must be between 0 and 90 degrees, because
    anything greater than 90 degrees indicates
    the sun is below the horizon.

    The equation used is from Duffie & Beckman (2006)
    Equation 1.6.5.

    :param latitude_degrees: A numeric value representing a location's
        position north (positive) or south (negative) of the equator,
        which must be between -90 and 90 degrees.
    :param declination_degrees: A numeric value representing
        the declination angle of the sun,
        which must be between -23.45 and 23.45 degrees.
    :param hour_angle_degrees: A numeric value corresponding
        to the angular displacement of the sun east (negative)
        or west (positive) of the local meridian due to rotation
        of the earth on its axis at 15 degrees per hour,
        which must be between -180 and 180 degrees.

    :returns: A float value representing the solar zenith angle in degrees.
    """

    # Validate arguments
    validate_numeric_value(value=latitude_degrees, minimum=-90, maximum=90)
    validate_numeric_value(
        value=declination_degrees, minimum=-23.45, maximum=23.45
    )
    validate_numeric_value(value=hour_angle_degrees, minimum=-180, maximum=180)

    calculated_zenith = degrees(
        acos(
            (
                cos(radians(latitude_degrees))
                * cos(radians(declination_degrees))
                * cos(radians(hour_angle_degrees))
            )
            + (
                sin(radians(latitude_degrees))
                * sin(radians(declination_degrees))
            )
        )
    )
    return min(90.0, calculated_zenith)


def calculate_solar_altitude_degrees(solar_zenith_degrees: float) -> float:
    """
    The solar altitude is the angle complementing the
    solar zenith angle.  Therefore, it is the angle
    between the horizontal and the line to the sun.

    :param solar_zenith_degrees: A float value representing the
        sun's current zenith angle,
        which must be between 0 and 90 degrees.

    :returns: A float value representing the solar altitude angle in degrees.
    """

    # Validate `solar_zenith_degrees`
    validate_numeric_value(value=solar_zenith_degrees, minimum=0, maximum=90)
    return 90.0 - solar_zenith_degrees


def calculate_air_mass(
    solar_zenith_degrees: Union[int, float],
    site_altitude_m: Union[int, float] = 0,
) -> float:
    """
    Air mass is the ratio of the mass of atmosphere through which
    beam radiation passes to the mass it would pass through if
    the sun were at the zenith (i.e., directly overhead).

    The equation used is from a footnote provided in
    Duffie & Beckman (2006) providing an empirical relationship
    from Kasten and Young (1989).

    :param solar_zenith_degrees: A numeric value representing the
        sun's current zenith angle,
        which must be between 0 and 90 degrees.
    :param site_altitude_m: A numeric value representing the
        altitude above sea level (0 m, the default),
        which must be at least -413 m
        (the lowest land elevation, on the shore of the Dead Sea).

    :returns: A float value representing the air mass.
    """

    # Validate `solar_zenith_degrees` and `site_altitude_m`
    validate_numeric_value(value=solar_zenith_degrees, minimum=0, maximum=90)
    validate_numeric_value(value=site_altitude_m, minimum=-413, maximum=None)

    return exp(-0.0001184 * site_altitude_m) / (
        cos(radians(solar_zenith_degrees))
        + (0.5057 * (96.080 - solar_zenith_degrees) ** -1.634)
    )


def calculate_solar_azimuth_degrees(
    hour_angle_degrees: Union[int, float],
    latitude_degrees: Union[int, float],
    declination_degrees: Union[int, float],
) -> float:
    """
    The solar azimuth angle is the angular displacement from south
    of the projection of beam radiation on the horizontal plane.
    Displacements east of south are negative, and
    displacements west of south are positive.

    The equation used is from Duffie & Beckman (2006)
    Equation 1.6.6.

    :param hour_angle_degrees: A numeric value corresponding
        to the angular displacement of the sun east (negative)
        or west (positive) of the local meridian due to rotation
        of the earth on its axis at 15 degrees per hour,
        which must be between -180 and 180 degrees.
    :param latitude_degrees: A numeric value representing a location's
        position north (positive) or south (negative) of the equator,
        which must be between -90 and 90 degrees.
    :param declination_degrees: A numeric value representing
        the declination angle of the sun,
        which must be between -23.45 and 23.45 degrees.

    :returns: A float value representing the solar azimuth angle.
    """

    # Validate arguments
    validate_numeric_value(value=hour_angle_degrees, minimum=-180, maximum=180)
    validate_numeric_value(value=latitude_degrees, minimum=-90, maximum=90)
    validate_numeric_value(
        value=declination_degrees, minimum=-23.45, maximum=23.45
    )

    # Calculate solar zenith angle
    solar_zenith_degrees = calculate_solar_zenith_degrees(
        latitude_degrees=latitude_degrees,
        declination_degrees=declination_degrees,
        hour_angle_degrees=hour_angle_degrees,
    )

    # copysign(x, y) returns `x` with the sign of `y`
    try:
        return copysign(1, hour_angle_degrees) * abs(
            degrees(
                acos(
                    (
                        (
                            cos(radians(solar_zenith_degrees))
                            * sin(radians(latitude_degrees))
                        )
                        - sin(radians(declination_degrees))
                    )
                    / (
                        sin(radians(solar_zenith_degrees))
                        * cos(radians(latitude_degrees))
                    )
                )
            )
        )
    except (ZeroDivisionError, ValueError):
        """A `ZeroDivisionError` or `ValueError` can occur when the sun
        is directly overhead, which is possible:
        on the equator, on an equinox, at solar noon.
        In this case, just return 0."""
        return 0.0


def calculate_solar_noon_in_local_standard_time(
    local_standard_time: Union[datetime, str],
    longitude_degrees: Union[int, float],
) -> datetime:
    """
    Method to calculate solar noon given a local standard timestamp
    (including date and time zone offset from UTC) and a location's
    longitude (in degrees west).

    The equation used is from Duffie & Beckman (2006)
    Equation 1.5.2.

    :param local_standard_time: A `datetime` object,
        containing a timezone offset, representing the time that
        will be converted to solar time.
    :param longitude_degrees: A numeric value representing a location's
        angular distance west of the meridian at Greenwich, England.
        `longitude_degrees` should be between 0 and 360 degrees.

    :returns: A datetime object representing the local standard
        time that corresponds to solar noon for the given
        date in `local_standard_time` and `longitude_degrees`.
    """

    # Type- and range-check `longitude_degrees`
    validate_numeric_value(longitude_degrees, minimum=0, maximum=360)
    # Validate `local_standard_time`
    local_ts = validate_datetime(datetime_object=local_standard_time)

    """Ensure local_standard_time has a date, time, and time zone offset.
    Note that parse will automaticall fill in a date or time if not
    provided with the current date and 00:00 (for time)."""
    if local_ts.tzinfo is None:
        # Check that `local_ts` has a timezone offset
        raise ValueError(
            """`local_standard_time` must provide a time zone offset,
            such as `1/1/2019 12:00 PM -06:00`."""
        )
    if local_ts.date() == datetime.now().date():
        # Provide a warning if `local_ts` only contains a time, but no date
        warn(
            UserWarning(
                """A date was likely not provided in local_standard_time;
                therefore, the date has been set to today."""
            )
        )

    # Calculate offset from UTC, using timezone offset in `local_ts`
    utc_offset = local_ts.tzinfo.utcoffset(local_ts).total_seconds() // 3_600

    """Determine the standard meridian for the given `longitude_degrees`,
    which corresponds to 15 degrees per hour offset."""
    standard_meridian = 15 * abs(utc_offset)

    E = calculate_E_min(
        calculate_B_degrees(calculate_day_number(local_standard_time))
    )
    longitude_correction_mins = 4.0 * (standard_meridian - longitude_degrees)

    solar_noon = datetime(
        year=local_ts.date().year,
        month=local_ts.date().month,
        day=local_ts.date().day,
        hour=12,
        minute=0,
        second=0,
        tzinfo=local_ts.tzinfo,
    )

    return solar_noon - timedelta(minutes=E + longitude_correction_mins)
