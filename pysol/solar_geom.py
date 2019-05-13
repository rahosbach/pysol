import datetime as dt
import math
from dateutil.parser import *
from dateutil.tz import *
import pytz
import warnings

class Solar_Geometry:
    def __init__(self, **kwargs):
        # define default attributes
        # latitude and longitude are degrees for Arcata, CA
        # (positive latitude is north, longitude provided as degrees west)
        default_attr = dict(
            G_sc=1367.,
            location_latitude=40.8665,
            location_longitude=124.0828,
            local_time='May 1, 2019 12:00 PM -08:00',
            dst=False)
        default_attr.update(kwargs)
        self.__dict__.update((k,v) for k,v in default_attr.items() if k in list(default_attr.keys()))

        for key in set(default_attr.keys())-set(kwargs.keys()):
            raise Warning('`{}` set to default value of {}'.format(key, default_attr[key]))

    def __repr__(self):
        return '{}(G_sc={}, location_latitude={}, location_longitude={}, local_time={}, dst={})'.format(
                    self.__class__, self.G_sc, self.location_latitude, self.location_longitude,
                    self.local_time, self.dst)

    def __str__(self):
        if self.dst:
            dst_string = 'daylight savings'
        else:
            dst_string = 'standard'
        return ('An instantiation of the Solar_Geometry class using a solar constant of {} W/m^2, '
                'location coordinates of (lat={}, long={}), and a local {} time of {}.').format(
                    self.G_sc, self.location_latitude, self.location_longitude, dst_string,
                    self.local_time)
                    
    @staticmethod
    def calculate_day_number_from_date(date_str):
        '''Method to calculate the day number of the year
        given a string representing a date or date/time.
        '''
        try:
            return parse(date_str).timetuple().tm_yday
        except ValueError:
            raise ValueError('date_str is not a valid date format.')

    def calculate_B(self, n):
        '''B is a preliminary value used in calculating the extraterrestrial
        radiation incident on the plane normal to the radiation on the nth
        day of the year (G_on) per an equation given by Spencer (1971).
        '''
        # Use class attributes if available
        n = n if n is not None else self.day_number

        if not(isinstance(n, int)):
            try:
                n = self.calculate_day_number_from_date(n)
            except ValueError:
                raise ValueError('If n is not an integer, it must be a date string.')
        elif (n <= 0) | (n >= 366):
            raise ValueError('If n is an integer, it must be between 1 and 365 (inclusive).')
        return (n - 1) * 360. / 365.

    def calculate_G_on_W_m2(self, n):
        '''G_on is the extraterrestrial radiation incident on the plane normal
        to the radiation on the nth day of the year per an equation given by
        Spencer (1971).
        ''' 
        # Use class attributes if available
        n = n if n is not None else self.day_number

        B = self.calculate_B(n)
        multiplier = (1.000110 +
                    (0.034221 * math.cos(B)) +
                    (0.001280 * math.sin(B)) +
                    (0.000719 * math.cos(2 * B)) +
                    (0.000077 * math.sin(2 * B)))
        return self.G_sc * multiplier

    def calculate_E(self, n):
        '''E is the equation of time, an equation given by Spencer (1971).
        '''
        # Use class attributes if available
        n = n if n is not None else self.day_number

        B = math.radians(self.calculate_B(n))
        return (229.2 *
                (0.000075 +
                (0.001868 * math.cos(B)) -
                (0.032077 * math.sin(B)) -
                (0.014615 * math.cos(2 * B)) -
                (0.04089 * math.sin(2 * B))))

    def calculate_solar_time(self, local_time=None, longitude=None, dst=None):
        '''Method to calculate solar time given a local timestamp
        (including date and time zone offset from UTC), a location's
        longitude (in degrees west), and an indicator of whether or
        not the provided time is a daylight savings time or a
        standard time.
        '''
        # Use class attributes if available
        local_time = local_time if local_time is not None else self.local_time
        longitude = longitude if longitude is not None else self.location_longitude
        dst = dst if dst is not None else self.dst
        
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

        utc_offset = local_ts.tzinfo.utcoffset(local_ts).total_seconds() // 3600

        # Correct for daylight savings time
        if dst:
            local_ts = local_ts - dt.timedelta(hours=1)
            local_ts = dt.datetime(
                year=local_ts.year,
                month=local_ts.month,
                day=local_ts.day,
                hour=local_ts.hour,
                minute=local_ts.minute,
                tzinfo=tzoffset(None, (utc_offset - 1) * 3600)) 
            utc_offset -= 1

        standard_meridian = 15 * abs(utc_offset)
        E = self.calculate_E(local_time)
        longitude_correction_mins = 4. * (standard_meridian - longitude)
        return local_ts + dt.timedelta(
            minutes=longitude_correction_mins + E)

    def calculate_declination_degrees(self, n):
        '''The declination is the angular position of the sun
        at solar noon with respect to the plane of the 
        equator (north is positive).  The equation is from
        Spencer (!971).
        '''
        # Use class attributes if available
        n = n if n is not None else self.day_number

        B = math.radians(self.calculate_B(n))
        return 180. / math.pi * (
            0.006918 -
            (0.399912 * math.cos(B)) +
            (0.070257 * math.sin(B)) -
            (0.006758 * math.cos(2 * B)) +
            (0.000907 * math.sin(2 * B)) -
            (0.002697 * math.cos(3 * B)) +
            (0.00148 * math.sin(3 * B)))

    def calculate_hour_angle_degrees(self, solar_time):
        '''The hour angle is the angular displacement of the
        sun east (negative) or west (positive) of the local
        meridian due to rotation of the earth on its axis at 
        15 degrees per hour.
        '''
        # Use class attributes if available
        solar_time = solar_time if solar_time is not None else self.solar_time

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

    def calculate_solar_zenith_degrees(self, solar_time=None, latitude=None):
        # Use class attributes if available
        solar_time = solar_time if solar_time is not None else self.solar_time
        latitude = latitude if latitude is not None else self.location_latitude

        # Ensure latitude is a valid number
        try:
            latitude = float(latitude)
            if (latitude < -90) | (latitude > 90):
                raise ValueError('latitude must be a numeric value between -90 and 90 (inclusive).')
        except ValueError:
            raise ValueError('latitude must be a numeric value between -90 and 90 (inclusive).')

        n = self.calculate_day_number_from_date(solar_time)
        declination = math.radians(self.calculate_declination_degrees(n))
        hour_angle = math.radians(self.calculate_hour_angle_degrees(parse(solar_time)))
        return math.degrees(math.acos(
            (math.cos(math.radians(latitude)) * math.cos(declination) * math.cos(hour_angle)) +
            (math.sin(math.radians(latitude)) * math.sin(declination))))

    def calculate_solar_altitude_degrees(self, solar_time=None, latitude=None):
        # Use class attributes if available
        solar_time = solar_time if solar_time is not None else self.solar_time
        latitude = latitude if latitude is not None else self.location_latitude

        return 90. - self.calculate_solar_zenith_degrees(solar_time, latitude)

    def calculate_all_attributes(self):
        self.day_number = self.calculate_day_number_from_date(self.local_time)
        self.B = self.calculate_B(self.day_number)
        self.G_on = self.calculate_G_on_W_m2(self.day_number)
        self.E = self.calculate_E(self.day_number)
        self.solar_time = self.calculate_solar_time(self.local_time, self.location_longitude, self.dst)
        self.declination = self.calculate_declination_degrees(self.day_number)
        self.hour_angle = self.calculate_hour_angle_degrees(self.solar_time)
        self.zenith = self.calculate_solar_zenith_degrees(self.solar_time, self.location_latitude)
        self.altitude = self.calculate_solar_altitude_degrees(self.solar_time, self.location_latitude)


class Solar_Array(Solar_Geometry):
    def __init__(self, **kwargs):
        # define default attributes
        # latitude and longitude are degrees for Arcata, CA
        # (longitude provided as degrees west)
        default_attr = dict(
            G_sc=1367.,
            location_latitude=40.8665,
            location_longitude=124.0828,
            local_time='May 1, 2019 12:00 PM -08:00',
            dst=False)
        # define (additional) allowed attributes with no default value
        more_allowed_attr = ['local_time', 'dst', 'surface_area_m2', 'array_efficiency']
        allowed_attr = list(default_attr.keys()) + more_allowed_attr
        default_attr.update(kwargs)
        self.__dict__.update((k,v) for k,v in default_attr.items() if k in allowed_attr)