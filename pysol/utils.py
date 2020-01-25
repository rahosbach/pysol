from datetime import datetime
from dateutil.parser import parse
from math import isinf, isnan
from typing import Any, Iterable, Optional, Union


def validate_datetime(datetime_object: Union[datetime, str]) -> datetime:
    """
    Method to validate a datetime object.

    `date_time_object` should be a proper datetime object
    or a string that can be parsed into a proper datetime object.

    :param date_time_object: A proper datetime object or a string
        that can be parsed into a proper datetime object.

    :returns: A proper datetime object.
    """

    if isinstance(datetime_object, str):
        # If `datetime_object` is a string, try to parse it.
        try:
            ts = parse(datetime_object)
            return ts
        # If `datetime_object` can't be parsed, raise a ValueError.
        except ValueError:
            raise ValueError('`date_time_obj` cannot be parsed into a proper datetime object.')
    elif not(isinstance(datetime_object, datetime)):
        # If `datetime_object` is not a string or a proper datetime value, raise a ValueError.
        raise TypeError('If variable `date_time_obj` is not a datetime string, it must be a datetime object.')
    else:
        # Otherwise, `datetime_object` should be OK to use.
        return datetime_object


def ensure_numeric(value, valid_types: Iterable[Any] = [int, float],
                   nan_acceptable: bool = False, inf_acceptable: bool = False) -> None:
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

    if (isnan(value)) & (not(nan_acceptable)):
        raise ValueError("NaN values are not valid when `nan_acceptable`=False.")
    elif (isinf(value)) & (not(inf_acceptable)):
        raise ValueError("Infinite values are not valid when `inf_acceptable`=False.")
    elif type(value) not in valid_types:
        # If `value` is not of an acceptable type, raise a TypeError.
        raise TypeError(f'`value` must be one of: {valid_types}.')
    else:
        pass


def validate_numeric_value(value: Union[int, float], minimum: Optional[Union[int, float]] = None, maximum: Optional[Union[int, float]] = None, tolerance: [float] = 1e-2) -> None:
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
    ensure_numeric(value, valid_types=[int, float], nan_acceptable=False, inf_acceptable=True)
    ensure_numeric(tolerance, valid_types=[float], nan_acceptable=False, inf_acceptable=False)

    # Create standard error message for calling when raising ValueErrors.
    error_message = f'`value` must be between {minimum} and {maximum} (inclusive, +/- {tolerance}).'

    if (minimum is None) & (maximum is None):
        # No range requirements, so `value` is OK.
        pass
    if minimum is not None:
        # Check `minimum`
        if value < (minimum - tolerance):
            # Type-check `minimum`
            ensure_numeric(minimum, valid_types=[int, float], nan_acceptable=False, inf_acceptable=True)
            # If a minimum requirement is set and `value` is less than that requirement, raise a ValueError.
            raise ValueError(error_message)
        else:
            # `value` is OK against `minimum`
            pass
    if maximum is not None:
        # Check `maximum`
        if value > (maximum + tolerance):
            # Type-check `maximum`
            ensure_numeric(maximum, valid_types=[int, float], nan_acceptable=False, inf_acceptable=True)
            # If a maximum requirement is set and `value` is more than that requirement, raise a ValueError.
            raise ValueError(error_message)
        else:
            # `value` is OK against `maximum`
            pass