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
            latitude=40.8665,
            longitude=124.0828,
            local_standard_time='May 1, 2019 12:00 PM -08:00',
            location_altitude=0)
        default_attr.update(kwargs)
        self.__dict__.update((k,v) for k,v in default_attr.items() if k in list(default_attr.keys()))

        for key in set(default_attr.keys())-set(kwargs.keys()):
            raise Warning('`{}` set to default value of {}'.format(key, default_attr[key]))

        # Attribute validation
        @property
        def G_sc(self):
            return self._G_sc
        @G_sc.setter
        def G_sc(self, G):
            if (not isinstance(G, int)) & (not isinstance(G, float)):
                raise ValueError('Attribute `G_sc` must be a numeric value.')
            elif G <= 0:
                raise ValueError('Attribute `G_sc` must be a value greater than 0 W/m^2.')
            self._G_sc = G

        @property
        def latitude(self):
            return self._latitude
        @latitude.setter
        def latitude(self, lat):
            if (not isinstance(lat, int)) & (not isinstance(lat, float)):
                raise ValueError('Attribute `latitude` must be a numeric value.')
            elif (lat < -90) | (lat > 90):
                raise ValueError('Attribute `latitude` must be a value between -90 and 90 degrees (inclusive).')
            self._lat = lat

        @property
        def longitude(self):
            return self._longitude
        @longitude.setter
        def longitude(self, longi):
            if (not isinstance(longi, int)) & (not isinstance(longi, float)):
                raise ValueError('Attribute `longitude` must be a numeric value.')
            elif (longi < 0) | (longi > 360):
                raise ValueError('Attribute `longitude` must be a value between 0 and 360 degrees (inclusive).')
            self._long = longi

        @property
        def local_standard_time(self):
            return self._local_standard_time
        @local_standard_time.setter
        def local_standard_time(self, lst):
            if not isinstance(parse(lst), dt.datetime):
                raise ValueError('Attribute `local_standard_time` must be a string containing a date, time, and UTC offset.')
            elif not parse(lst).tzinfo:
                raise ValueError('Attribute `local_standard_time` must contain a UTC offset (e.g., +02:00).')
            self._lst = lst

        @property
        def location_altitude(self):
            return self._location_altitude
        @location_altitude.setter
        def location_altitude(self, localt):
            if (not isinstance(localt, int)) & (not isinstance(localt, float)):
                raise ValueError('Attribute `location_altitude` must be a numeric value.')
            self._localt = localt

        self.calculate_all_variables()

    def __repr__(self):
        return '{}(G_sc={}, latitude={}, longitude={}, local_standard_time={})'.format(
                    self.__class__, self.G_sc, self.latitude, self.longitude,
                    self.local_standard_time)

    def __str__(self):
        return ('An instantiation of the Solar_Geometry class using a solar constant of {} W/m^2, '
                'location coordinates of (lat={}, long={}), and a local standard time of {}.').format(
                    self.G_sc, self.latitude, self.longitude, self.local_standard_time)

    def input_validation(self):
        # Ensure local_standard time is valid format
        try:
            parse(self.local_standard_time).timetuple().tm_yday
        except ValueError:
            raise ValueError('Variable `local_standard_time` is not a valid format.')
                    
    @staticmethod
    def calculate_day_number_from_date(date_str):
        '''Method to calculate the day number of the year
        given a string representing a date or date/time.
        '''
        if isinstance(date_str, str):
            try:
                return parse(date_str).timetuple().tm_yday
            except ValueError:
                raise ValueError('date_str is not a valid date format.')
        else:
            return date_str.timetuple().tm_yday

    def calculate_B(self, n=None):
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

    def calculate_G_on_W_m2(self, n=None):
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

    def calculate_E_min(self, n=None):
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

    def calculate_solar_time(self, local_standard_time=None, longitude=None):
        '''Method to calculate solar time given a local timestamp
        (including date and time zone offset from UTC), a location's
        longitude (in degrees west), and an indicator of whether or
        not the provided time is a daylight savings time or a
        standard time.
        '''
        # Use class attributes if available
        local_standard_time = local_standard_time if local_standard_time is not None else self.local_standard_time
        longitude = longitude if longitude is not None else self.longitude
        
        # Ensure longitude is a valid number
        try:
            longitude = float(longitude)
            if (longitude < 0) | (longitude > 360):
                raise ValueError('longitude must be a numeric value between 0 and 360 (inclusive).')
        except ValueError:
            raise ValueError('longitude must be a numeric value between 0 and 360 (inclusive).')

        # Ensure local_standard_time has a date, time, and time zone offset.
        # Note that parse will automaticall fill in a date or time if not
        # provided with the current date the 00:00 (for time).
        local_ts = parse(local_standard_time)
        if not(isinstance(local_ts.tzinfo, tzoffset)):
            raise ValueError('local_standard_time must provide a time zone offset, such as `1/1/2019 12:00 PM -06:00`.')
        if local_ts.date() == dt.datetime.now().date():
            warnings.warn('A date was likely not provided in local_standard_time; therefore, the date has been set to today.')

        utc_offset = local_ts.tzinfo.utcoffset(local_ts).total_seconds() // 3600

        standard_meridian = 15 * abs(utc_offset)
        E = self.calculate_E_min(local_standard_time)
        longitude_correction_mins = 4. * (standard_meridian - longitude)
        return local_ts + dt.timedelta(
            minutes=longitude_correction_mins + E)

    def calculate_declination_degrees(self, n=None):
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

    def calculate_hour_angle_degrees(self, solar_time=None):
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

    def calculate_solar_zenith_degrees(self, solar_time=None, latitude=None, declination=None, hour_angle=None):
        # Use class attributes if available
        solar_time = solar_time if solar_time is not None else self.solar_time
        latitude = latitude if latitude is not None else self.latitude
        declination = declination if declination is not None else self.declination_degrees
        hour_angle = hour_angle if hour_angle is not None else self.hour_angle_degrees

        # Ensure latitude is a valid number
        try:
            latitude = float(latitude)
            if (latitude < -90) | (latitude > 90):
                raise ValueError('latitude must be a numeric value between -90 and 90 (inclusive).')
        except ValueError:
            raise ValueError('latitude must be a numeric value between -90 and 90 (inclusive).')

        n = self.calculate_day_number_from_date(solar_time)
        declination = math.radians(self.calculate_declination_degrees(n))
        if isinstance(solar_time, str):
            hour_angle = math.radians(self.calculate_hour_angle_degrees(parse(solar_time)))
        else:
            hour_angle = math.radians(self.calculate_hour_angle_degrees(solar_time))
        return math.degrees(math.acos(
            (math.cos(math.radians(latitude)) * math.cos(declination) * math.cos(hour_angle)) +
            (math.sin(math.radians(latitude)) * math.sin(declination))))

    def calculate_solar_altitude_degrees(self, solar_time=None, latitude=None):
        # Use class attributes if available
        solar_time = solar_time if solar_time is not None else self.solar_time
        latitude = latitude if latitude is not None else self.latitude

        return 90. - self.calculate_solar_zenith_degrees(solar_time, latitude)

    def calculate_air_mass(self, solar_zenith_degrees=None, site_altitude_m=None):
        # Use class attributes if available
        solar_zenith_degrees = solar_zenith_degrees if solar_zenith_degrees is not None else self.solar_zenith_degrees
        site_altitude_m = site_altitude_m if site_altitude_m is not None else self.location_altitude

        if solar_zenith_degrees <= 70.:
            return 1. / math.cos(math.radians(solar_zenith_degrees))
        elif site_altitude_m is None:
            raise ValueError('For a `solar_zenith_degrees` > 70 degrees, a site altitude (in meters) must be provided.')
        else:
            return math.exp(-0.0001184 * site_altitude_m) / (
                math.cos(math.radians(solar_zenith_degrees)) + 
                (0.5057 * (96.080 - solar_zenith_degrees) ** -1.634))

    def calculate_solar_azimuth_degrees(self, hour_angle=None, solar_zenith=None, latitude=None, declination=None):
        # Use class attributes if available
        hour_angle = hour_angle if hour_angle is not None else self.hour_angle_degrees
        solar_zenith = solar_zenith if solar_zenith is not None else self.solar_zenith_degrees
        latitude = latitude if latitude is not None else self.latitude
        declination = declination if declination is not None else self.declination_degrees

        return (hour_angle) / abs(hour_angle) * abs(math.degrees(math.acos(
            ((math.cos(math.radians(solar_zenith)) * math.sin(math.radians(latitude))) - math.sin(math.radians(declination))) /
            (math.sin(math.radians(solar_zenith)) * math.cos(math.radians(latitude))))))

    def calculate_solar_noon_in_local_standard_time(self, local_standard_time=None, longitude=None):
        # Use class attributes if available
        local_standard_time = local_standard_time if local_standard_time is not None else self.local_standard_time
        longitude = longitude if longitude is not None else self.longitude

        local_ts = parse(local_standard_time)
        if not(isinstance(local_ts.tzinfo, tzoffset)):
            raise ValueError('local_standard_time must provide a time zone offset, such as `1/1/2019 12:00 PM -06:00`.')
        if local_ts.date() == dt.datetime.now().date():
            warnings.warn('A date was likely not provided in local_standard_time; therefore, the date has been set to today.')

        utc_offset = local_ts.tzinfo.utcoffset(local_ts).total_seconds() // 3600

        standard_meridian = 15 * abs(utc_offset)
        E = self.calculate_E_min(local_standard_time)
        longitude_correction_mins = 4. * (standard_meridian - longitude)

        solar_noon = dt.datetime(
            year=local_ts.date().year,
            month=local_ts.date().month,
            day=local_ts.date().day,
            hour=12,
            minute=0,
            second=0,
            tzinfo=local_ts.tzinfo)

        return solar_noon - dt.timedelta(minutes=E + longitude_correction_mins)

    def calculate_all_variables(self):
        self.day_number = self.calculate_day_number_from_date(self.local_standard_time)
        self.B = self.calculate_B()
        self.G_on_W_m2 = self.calculate_G_on_W_m2()
        self.E_min = self.calculate_E_min()
        self.solar_time = self.calculate_solar_time()
        self.declination_degrees = self.calculate_declination_degrees()
        self.hour_angle_degrees = self.calculate_hour_angle_degrees()
        self.solar_zenith_degrees = self.calculate_solar_zenith_degrees()
        self.solar_altitude_degrees = self.calculate_solar_altitude_degrees()
        self.air_mass = self.calculate_air_mass()
        self.solar_azimuth_degrees = self.calculate_solar_azimuth_degrees()
        self.solar_noon_in_local_time = self.calculate_solar_noon_in_local_standard_time()


class Solar_Array(Solar_Geometry):
    def __init__(self, **kwargs):
        # define default attributes
        # latitude and longitude are degrees for Arcata, CA
        # (longitude provided as degrees west)
        default_attr = dict(
            G_sc=1367.,
            latitude=40.8665,
            longitude=124.0828,
            local_standard_time='May 1, 2019 12:00 PM -08:00')
        # define (additional) allowed attributes with no default value
        more_allowed_attr = ['local_standard_time', 'surface_area_m2', 'array_efficiency']
        allowed_attr = list(default_attr.keys()) + more_allowed_attr
        default_attr.update(kwargs)
        self.__dict__.update((k,v) for k,v in default_attr.items() if k in allowed_attr)