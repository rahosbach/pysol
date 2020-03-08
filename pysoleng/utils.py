from collections.abc import Iterable
from datetime import datetime
from math import isinf, isnan
from typing import Any, Iterable, Optional, Union

from dateutil.parser import parse

import numpy as np
import pandas as pd


def validate_datetime(
    datetime_object: Union[datetime, np.datetime64, str, Iterable[Union[datetime, np.datetime64, str]]]
) -> Union[pd.Timestamp, Iterable[pd.Timestamp]]:
    """
    Method to validate a datetime object.

    This method relies on the Pandas to_datetime() method for
    parsing the input into a proper datetime object.

    :param date_time_object: A proper datetime object, a string
        that can be parsed into a proper datetime object, or an
        iterable containing proper datetime objects or
        parse-able strings.

    :returns: A Pandas Timestamp object, or a Pandas DatetimeIndex of multiple objects.
    """

    try:
        return pd.to_datetime(datetime_object)
    # If `datetime_object` can't be parsed, raise a ValueError.
    except ValueError:
        raise ValueError(
            f"""{datetime_object} cannot be parsed into
            a proper datetime object."""
        )


def ensure_numeric(
    value,
    valid_types: Iterable[Any] = [int, float],
    nan_acceptable: bool = False,
    inf_acceptable: bool = False,
) -> None:
    """
    Method to ensure a given `value` is of the proper numeric type.

    `value` should be an object corresponding to one of the values
    in `valid_types`.

    :param value: A value that will be type-checked against the
        values in `valid_types`.
    :param valid_types: An iterable containing acceptable types
        for `value`.
    :param nan_acceptable: A boolean value to indicate whether
        NaN values are acceptable.
    :param inf_acceptable: A boolean value to indicate whether
        infinite values are acceptable.
    """

    # Convert `value` to a list, if not already an iterable
    if not(isinstance(value, Iterable)):
        value = [value]
    
    for val in value:
        if (isnan(val)) & (not (nan_acceptable)):
            raise ValueError(
                "NaN values are not valid when `nan_acceptable`=False."
            )
        elif (isinf(val)) & (not (inf_acceptable)):
            raise ValueError(
                "Infinite values are not valid when `inf_acceptable`=False."
            )
        elif type(val) not in valid_types:
            # If `val` is not of an acceptable type, raise a TypeError.
            raise TypeError(f"`value` must contain one of: {valid_types}.")


def validate_numeric_value(
    value: Union[int, float, Iterable[Union[int, float]]],
    minimum: Optional[Union[int, float]] = None,
    maximum: Optional[Union[int, float]] = None,
    tolerance: [float] = 1e-2,
) -> None:
    """
    Method to ensure a given value is within the proper range.

    `value` should be a numeric value within the range [minimum, maximum].

    :param value: A numeric value to be range-checked.
    :param minimum: A numeric value representing the minimum acceptable value
        for `value`, or `None` (the default) if no minimum is required.
    :param maximum: A numeric value representing the maximum acceptable value
        for `value`, or `None` (the default) if no maximum is required.
    :param tolerance: An allowable tolerance for comparing to
        `minimum` and `maximum` (default 1e-2).
    """

    # Type-check `value` and `tolerance`
    ensure_numeric(
        value,
        valid_types=[int, float],
        nan_acceptable=False,
        inf_acceptable=True,
    )
    ensure_numeric(
        tolerance,
        valid_types=[float],
        nan_acceptable=False,
        inf_acceptable=False,
    )

    # Create standard error message for calling when raising ValueErrors.
    error_message = f"""`value` must be between {minimum} and {maximum}
    (inclusive, +/- {tolerance})."""

    if (minimum is None) & (maximum is None):
        # No range requirements, so `value` is OK.
        pass
    else:
        if minimum is not None:
            # Type-check `minimum`
                ensure_numeric(
                    minimum,
                    valid_types=[int, float],
                    nan_acceptable=False,
                    inf_acceptable=True,
                )
        if maximum is not None:
            # Type-check `maximum`
                ensure_numeric(
                    maximum,
                    valid_types=[int, float],
                    nan_acceptable=False,
                    inf_acceptable=True,
                )

    # Convert `value` to a list, if not already an iterable
    if not(isinstance(value, Iterable)):
        value = [value]

    for val in value:   
        if minimum is not None:
            # Check `minimum`
            if val < (minimum - tolerance):
                """If a minimum requirement is set and `value` is
                less than that requirement, raise a ValueError."""
                raise ValueError(error_message)

        if maximum is not None:
            # Check `maximum`
            if val > (maximum + tolerance):
                """If a maximum requirement is set and `value` is
                more than that requirement, raise a ValueError."""
                raise ValueError(error_message)
