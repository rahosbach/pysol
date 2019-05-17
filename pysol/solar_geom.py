import datetime as dt
import math
from dateutil.parser import *
from dateutil.tz import *
import pytz
import warnings

class Solar_Geometry:
    def __init__(self):
        self.G_sc = 1367. # W/m^2

    def __repr__(self):
        return '{}(G_sc={})'.format(self.__class__, self.G_sc)

    def __str__(self):
        return ('An instantiation of the Solar_Geometry class with the solar '
        'constant assumed to be {} W/m^2.'.format(self.G_sc))

    @staticmethod
    def validate_times(date_time_obj):
        if isinstance(date_time_obj, str):
            try:
                ts = parse(date_time_obj)
                return ts
            except ValueError:
                raise ValueError('Variable `date_time_obj` is not a valid datetime format.')
        elif not(isinstance(date_time_obj, dt.datetime)):
            raise ValueError('If variable `local_stdate_time_objandard_time` is not a datetime string, it must be a datetime object.')
        else:
            return date_time_obj 

    @staticmethod
    def validate_long_lat(value, longitude=True):
        long_err_message = 'Variable `longitude` must be a numeric value between 0 and 360 (inclusive).'
        lat_err_message = 'Variable `latitude` must be a numeric value between -90 and 90 (inclusive).'
        try:
            value = float(value)
        except:
            if longitude:
                raise ValueError(long_err_message)
            else:
                raise ValueError(lat_err_message)
        if longitude:
            if (value < 0) | (value > 360):
                raise ValueError(long_err_message)
        else:
            if (value < -90) | (value > 90):
                raise ValueError(lat_err_message)
        return value

    @staticmethod
    def validate_altitude(altitude):
        err_message = 'Variable `site_altitude_m` must be a numeric value.'
        try:
            value = float(altitude)
        except:
            raise ValueError(err_message)
        return altitude
                    
    @staticmethod
    def calculate_day_number_from_date(date):
        '''Method to calculate the day number of the year
        given a string representing a date or date/time.
        '''
        date = validate_times(date)
        return date.timetuple().tm_yday

    def calculate_B(self, date):
        '''B is a preliminary value used in calculating the extraterrestrial
        radiation incident on the plane normal to the radiation on the nth
        day of the year (G_on) per an equation given by Spencer (1971).
        '''
        date = validate_times(date)
        n = self.calculate_day_number_from_date(date)
        return (n - 1) * 360. / 365.

    def calculate_G_on_W_m2(self, date):
        '''G_on is the extraterrestrial radiation incident on the plane normal
        to the radiation on the nth day of the year per an equation given by
        Spencer (1971).
        ''' 
        B = self.calculate_B(date)
        multiplier = (1.000110 +
                    (0.034221 * math.cos(B)) +
                    (0.001280 * math.sin(B)) +
                    (0.000719 * math.cos(2 * B)) +
                    (0.000077 * math.sin(2 * B)))
        return self.G_sc * multiplier

    def calculate_E_min(self, date):
        '''E is the equation of time, an equation given by Spencer (1971).
        '''
        B = math.radians(self.calculate_B(date))
        return (229.2 *
                (0.000075 +
                (0.001868 * math.cos(B)) -
                (0.032077 * math.sin(B)) -
                (0.014615 * math.cos(2 * B)) -
                (0.04089 * math.sin(2 * B))))

    def calculate_solar_time(self, local_standard_time, longitude):
        '''Method to calculate solar time given a local timestamp
        (including date and time zone offset from UTC), a location's
        longitude (in degrees west), and an indicator of whether or
        not the provided time is a daylight savings time or a
        standard time.
        '''
        longitude = validate_long_lat(longitude)
        local_ts = validate_times(local_standard_time)

        # Ensure local_standard_time has a date, time, and time zone offset.
        # Note that parse will automaticall fill in a date or time if not
        # provided with the current date the 00:00 (for time).
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

    def calculate_declination_degrees(self, date):
        '''The declination is the angular position of the sun
        at solar noon with respect to the plane of the 
        equator (north is positive).  The equation is from
        Spencer (1971).
        '''
        B = math.radians(self.calculate_B(date))
        return 180. / math.pi * (
            0.006918 -
            (0.399912 * math.cos(B)) +
            (0.070257 * math.sin(B)) -
            (0.006758 * math.cos(2 * B)) +
            (0.000907 * math.sin(2 * B)) -
            (0.002697 * math.cos(3 * B)) +
            (0.00148 * math.sin(3 * B)))

    def calculate_hour_angle_degrees(self, local_standard_time, longitude):
        '''The hour angle is the angular displacement of the
        sun east (negative) or west (positive) of the local
        meridian due to rotation of the earth on its axis at 
        15 degrees per hour.
        '''
        longitude = validate_long_lat(longitude)
        local_ts = validate_time(local_standard_time)
        solar_ts = self.calculate_solar_time(local_ts, longitude)

        solar_noon = dt.datetime(
            year=solar_ts.date().year,
            month=solar_ts.date().month,
            day=solar_ts.date().day,
            hour=12,
            minute=0,
            second=0,
            tzinfo=solar_ts.tzinfo)
        hours_diff = (solar_ts - solar_noon).total_seconds() / 3600
        return hours_diff * 15.

    def calculate_solar_zenith_degrees(self, local_standard_time, latitude, longitude):
        longitude = validate_long_lat(longitude)
        latitude = validate_long_lat(latitude, False)
        
        local_ts = self.validate_times(local_standard_time)
        solar_ts= self.calculate_solar_time(local_ts, longitude)

        n = self.calculate_day_number_from_date(solar_ts)
        declination = math.radians(self.calculate_declination_degrees(n))
        hour_angle = math.radians(self.calculate_hour_angle_degrees(solar_ts))
        return math.degrees(math.acos(
            (math.cos(math.radians(latitude)) * math.cos(declination) * math.cos(hour_angle)) +
            (math.sin(math.radians(latitude)) * math.sin(declination))))

    def calculate_solar_altitude_degrees(self, local_standard_time, latitude, longitude):
        longitude = validate_long_lat(longitude)
        latitude = validate_long_lat(latitude, False)
        local_ts = self.validate_times(local_standard_time)
        solar_ts= self.calculate_solar_time(local_ts, longitude)
        return 90. - self.calculate_solar_zenith_degrees(solar_ts, latitude)

    def calculate_air_mass(self, local_standard_time, latitude, longitude, site_altitude_m):
        longitude = validate_long_lat(longitude)
        latitude = validate_long_lat(latitude, False)
        local_ts = self.validate_times(local_standard_time)
        solar_ts = self.calculate_solar_time(local_ts, longitude)
        solar_zenith_degrees = self.calculate_solar_zenith_degrees(solar_ts, latitude)

        if solar_zenith_degrees <= 70.:
            return 1. / math.cos(math.radians(solar_zenith_degrees))
        elif site_altitude_m is None:
            raise ValueError('For a `solar_zenith_degrees` > 70 degrees, a site altitude (in meters) must be provided.')
        else:
            site_altitude_m = validate_altitude(site_altitude_m)
            return math.exp(-0.0001184 * site_altitude_m) / (
                math.cos(math.radians(solar_zenith_degrees)) + 
                (0.5057 * (96.080 - solar_zenith_degrees) ** -1.634))

    def calculate_solar_azimuth_degrees(self, local_standard_time, latitude, longitude):
        longitude = validate_long_lat(longitude)
        latitude = validate_long_lat(latitude, False)
        local_ts = self.validate_times(local_standard_time)
        solar_ts = self.calculate_solar_time(local_ts, longitude)
        hour_angle = self.calculate_hour_angle_degrees(solar_ts)
        solar_zenith = self.calculate_solar_zenith_degrees(solar_ts, latitude)
        declination = self.calculate_declination_degrees(solar_ts)

        return (hour_angle) / abs(hour_angle) * abs(math.degrees(math.acos(
            ((math.cos(math.radians(solar_zenith)) * math.sin(math.radians(latitude))) - math.sin(math.radians(declination))) /
            (math.sin(math.radians(solar_zenith)) * math.cos(math.radians(latitude))))))

    def calculate_solar_noon_in_local_standard_time(self, local_standard_time, longitude):
        longitude = validate_long_lat(longitude)
        local_ts = validate_times(local_standard_time)
        if not(isinstance(local_ts.tzinfo, tzoffset)):
            raise ValueError('local_standard_time must provide a time zone offset, such as `1/1/2019 12:00 PM -06:00`.')
        if local_ts.date() == dt.datetime.now().date():
            warnings.warn('A date was likely not provided in local_standard_time; therefore, the date has been set to today.')

        utc_offset = local_ts.tzinfo.utcoffset(local_ts).total_seconds() // 3600

        standard_meridian = 15 * abs(utc_offset)
        E = self.calculate_E_min(local_ts)
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

    def calculate_all_variables(self, **kwargs):
        default_attr = dict(
            local_standard_time=None,
            latitude=None,
            longitude=None,
            site_altitude_m=None,
            print_results=False)
        default_attr.update(kwargs)

        if default_attr['local_standard_time'] is None:
            raise ValueError('A datetime string must be provided, at a minimum.')
        else:
            local_ts = self.validate_times(default_attr['local_standard_time'])
        
        # Create empty results dictionary
        results = dict()
        for result_var in ['B', 'G_on_W_m2', 'E_min', 'solar_time', 'declination_degrees',
                           'hour_angle_degrees', 'solar_zenith_degrees', 'solar_altitude_degrees',
                           'air_mass', 'solar_azimuth_degrees', 'solar_noon_in_local_time']:
            results[results_var] = None
        
        # Results that only require a date
        results['B'] = self.calculate_B(local_ts)
        results['G_on_W_m2'] = self.calculate_G_on_W_m2(local_ts)
        results['E_min'] = self.calculate_E_min(local_ts)
        results['declination_degrees'] = self.calculate_declination_degrees(local_ts)
        
        # Results that require a date and longitude
        if default_attr['longitude'] is not None:
            longitude = self.validate_long_lat(default_attr['longitude'])
            results['solar_time'] = self.calculate_solar_time(local_ts, longitude)
            results['hour_angle_degrees'] = self.calculate_hour_angle_degrees(local_ts, longitude)
            results['solar_noon_in_local_time'] = self.calculate_solar_noon_in_local_standard_time(local_ts, longitude)
        
        # Results that require a date, longitude, and latitude
        if default_attr['latitude'] is not None:
            latitude = self.validate_long_lat(default_attr['latitude'], False)
            results['solar_zenith_degrees'] = self.calculate_solar_zenith_degrees(local_ts, latitude, longitude)
            results['solar_altitude_degrees'] = self.calculate_solar_altitude_degrees(local_ts, latitude, longitude)
            if results['solar_zenith_degrees'] > 70.:
                if default_attr['site_altitude_m'] is not None:
                    site_altitude_m = self.validate_altitude(default_attr['site_altitude_m'])
                    results['air_mass'] = self.calculate_air_mass(local_ts, latitude, longitude, site_altitude_m)
                else:
                    results['air_mass'] = 'Cannot calculate properly without a site altitude.'
            else:
                results['air_mass'] = self.calculate_air_mass(local_ts, latitude, longitude)
            results['solar_azimuth_degrees'] = self.calculate_solar_azimuth_degrees(local_ts, latitude, longitude)
        
        if default_attr['print_results']:
            for key, value in results.items():
                print('{}: {}'.format(key, value))

        return results

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