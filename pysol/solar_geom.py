import datetime as dt
import math
from dateutil.parser import *
from dateutil.tz import *
import pytz
import warnings

G_sc = 1367. # W/m2

def calculate_day_number_from_date(date_str):
    '''Method to calculate the day number of the year
    given a string representing a date or date/time.
    '''
    try:
        return parse(date_str).timetuple().tm_yday
    except ValueError:
        raise ValueError('date_str is not a valid date format.')

def calculate_B(n):
    '''B is a preliminary value used in calculating the extraterrestrial
    radiation incident on the plane normal to the radiation on the nth
    day of the year (G_on) per an equation given by Spencer (1971).
    '''
    if not(isinstance(n, int)):
        try:
            n = calculate_day_number_from_date(n)
        except ValueError:
            raise ValueError('If n is not an integer, it must be a date string.')
    elif (n <= 0) | (n >= 366):
        raise ValueError('If n is an integer, it must be between 1 and 365 (inclusive).')
    return (n - 1) * 360. / 365.

def calculate_G_on(n):
    '''G_on is the extraterrestrial radiation incident on the plane normal
    to the radiation on the nth day of the year per an equation given by
    Spencer (1971).
    ''' 
    B = calculate_B(n)
    multiplier = (1.000110 +
                  (0.034221 * math.cos(B)) +
                  (0.001280 * math.sin(B)) +
                  (0.000719 * math.cos(2 * B)) +
                  (0.000077 * math.sin(2 * B)))
    return G_sc * multiplier

def calculate_E(n):
    '''E is the equation of time, an equation given by Spencer (1971).
    '''
    B = math.radians(calculate_B(n))
    return (229.2 *
            (0.000075 +
             (0.001868 * math.cos(B)) -
             (0.032077 * math.sin(B)) -
             (0.014615 * math.cos(2 * B)) -
             (0.04089 * math.sin(2 * B))))

def calculate_solar_time(local_time, longitude, dst=False):
    '''Method to calculate solar time given a local timestamp
    (including date and time zone offset from UTC), a location's
    longitude (in degrees west), and an indicator of whether or
    not the provided time is a daylight savings time or a
    standard time.
    '''
    # Ensure longitude is a valid number
    try:
        longitude = float(longitude)
        if (longitude < 0) | (longitude > 360):
            raise ValueError('longitude must be a numeric value between 0 and 360 (inclusive).')
    except ValueError:
        raise ValueError('longitude must be a numeric value between 0 and 360 (inclusive).')

    # Ensure local_time has a date, time, and time zone offset.
    # Note that parse will automaticall fill in a date or time if not
    # provided with the current date the 00:00 (for time).
    local_ts = parse(local_time)
    if not(isinstance(local_ts.tzinfo, tzoffset)):
        raise ValueError('local_time must provide a time zone offset, such as `1/1/2019 12:00 PM -06:00`.')
    if local_ts.date() == dt.datetime.now().date():
        warnings.warn('A date was likely not provided in local_time; therefore, the date has been set to today.')
    
    utc_offset = abs(local_ts.tzinfo.utcoffset(local_ts).seconds // 3600)
    # utc_offset can give values greater than 12, which we don't want.
    # For instance, if the time zone is -4, utc_offset will be 20,
    # when we really need it to be 4 for this calculation.  This if
    # construct fixes that.
    if utc_offset > 12:
        utc_offset = 24 - utc_offset

    # Correct for daylight savings time
    if dst:
        local_ts = local_ts - dt.timedelta(hours=1)

    standard_meridian = 15 * utc_offset
    E = calculate_E(local_time)
    longitude_correction_mins = 4. * (standard_meridian - longitude)
    return local_ts + dt.timedelta(
        minutes=longitude_correction_mins + E)

def calculate_declination(n):
    '''The declination is the angular position of the sun
    at solar noon with respect to the plane of the 
    equator (north is positive).  The equation is from
    Spencer (!971).
    '''
    B = math.radians(calculate_B(n))
    return 180. / math.pi * (
        0.006918 -
        (0.399912 * math.cos(B)) +
        (0.070257 * math.sin(B)) -
        (0.006758 * math.cos(2 * B)) +
        (0.000907 * math.sin(2 * B)) -
        (0.002697 * math.cos(3 * B)) +
        (0.00148 * math.sin(3 * B)))

def calculate_hour_angle(solar_time):
    '''The hour angle is the angular displacement of the
    sun east (negative) or west (positive) of the local
    meridian due to rotation of the earth on its axis at 
    15 degrees per hour.
    '''
    solar_noon = dt.datetime(
        year=solar_time.date().year,
        month=solar_time.date().month,
        day=solar_time.date().day,
        hour=12,
        minute=0,
        second=0,
        tzinfo=solar_time.tzinfo)
    hours_diff = (solar_time - solar_noon).total_seconds() / 3600
    return hours_diff * 15.