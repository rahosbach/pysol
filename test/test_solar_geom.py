import datetime as dt
import unittest

from dateutil.parser import *
from pysol.solar_geom import Solar_Geometry

from pdb import set_trace as bp

class SolarGeomTest(unittest.TestCase):
    def setUp(self):
        self.solar_geometry = Solar_Geometry()

    def test_validate_times(self):
        self.assertEqual(self.solar_geometry.validate_times('January 1, 2019 12:00 PM'), dt.datetime(2019, 1, 1, 12, 0, 0))
        self.assertRaises(ValueError, lambda: self.solar_geometry.validate_times('January Blah Blah'))
        self.assertRaises(ValueError, lambda: self.solar_geometry.validate_times(20190101))
        self.assertEqual(self.solar_geometry.validate_times(dt.datetime(2019, 1, 1, 12, 0, 0)), dt.datetime(2019, 1, 1, 12, 0, 0))

    def test_calculate_day_number_from_date(self):
        self.assertEqual(self.solar_geometry.calculate_day_number_from_date('January 2, 2018'), 2)
        self.assertEqual(self.solar_geometry.calculate_day_number_from_date('1/2/2018'), 2)
        self.assertEqual(self.solar_geometry.calculate_day_number_from_date('20180102'), 2)
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_day_number_from_date('20183535'))

    def test_calculate_B(self):
        self.assertEqual(self.solar_geometry.calculate_B('January 1, 2019'), 0)
        self.assertAlmostEqual(self.solar_geometry.calculate_B('1/10/2019'), 8.8767, places=4)
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_B(0))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_B(10))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_B('R'))
    
    def test_calculate_G_on_W_m2(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_G_on_W_m2('January 1, 2019'), 1414.91335, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_G_on_W_m2('July 1, 2019'), 1328.5414, places=4)

    def test_calculate_E_min(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_E_min('January 1, 2019'), -2.9044, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_E_min('February 3, 2019'), -13.4885, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_E_min('10/31/2019'), 16.3751, places=4)

    def test_calculate_solar_time(self):
        self.assertTrue(abs(
            (self.solar_geometry.calculate_solar_time('February 3, 2019 10:30 AM -06:00', 89.4) -
            parse('February 3, 2019 10:19 AM -06:00')).total_seconds()) <= 30)
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM -02:00', 375.))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM -02:00', 'long'))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM', 100.))
        self.assertWarns(Warning, lambda: self.solar_geometry.calculate_solar_time('10:00 AM -02:00', 100.))

    def test_calculate_declination_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_declination_degrees('February 16, 2019'), -12.6090, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_declination_degrees('April 15, 2019'), 9.4808, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_declination_degrees('December 10, 2018'), -22.8406, places=4)

    def test_calculate_hour_angle_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle_degrees(parse("1/1/2019 10:30 AM -08:00"), 124.), -27.2261, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle_degrees(parse("12/31/2019 11:00 AM -02:00"), 124.), -109.6133, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle_degrees(parse("June 10, 2002 5:47 PM -08:00"), 124.), 83.0013, places=4)

    def test_calculate_solar_zenith_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_zenith_degrees("February 13, 9:30 AM -08:00", 41., 124.), 73.1066, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_zenith_degrees("July 1, 6:30 PM -08:00", 41., 124.), 73.4281, places=4)

    def test_calculate_solar_altitude_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_altitude_degrees("February 13, 9:30 AM -08:00", 41., 124.), 16.8934, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_altitude_degrees("July 1, 6:30 PM -08:00", 41., 124.), 16.5719, places=4)

    def test_calculate_air_mass(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_air_mass('January 1, 2019 2:00 PM -08:00', 41., 124.), 2.5428, places=4)
        #self.assertAlmostEqual(self.solar_geometry.calculate_air_mass(test_date, 0.), 1.0000, places=4)
        #self.assertAlmostEqual(self.solar_geometry.calculate_air_mass(test_date, 70.), 2.9238, places=4)
        #self.assertAlmostEqual(self.solar_geometry.calculate_air_mass(test_date, 71., 0.), 3.0471, places=4)
        #self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_air_mass(test_date, 71.))

    def test_calculate_solar_azimuth_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_azimuth_degrees('January 1, 2019 2:00 PM -08:00', 41., 124.), 20.5637, places=4 )
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_azimuth_degrees('March 10, 2019 3:00 PM -08:00', 41., 124.), 40.2467, places=4 )

    def test_calculate_solar_noon_in_local_standard_time(self):
        self.assertTrue(abs(
            (self.solar_geometry.calculate_solar_noon_in_local_standard_time('February 3, 2019 10:30 AM -06:00', 89.4) -
            parse('February 3, 2019 12:11:25 PM -06:00')).total_seconds()) <= 30)
        self.assertTrue(abs(
            (self.solar_geometry.calculate_solar_noon_in_local_standard_time('June 7, 2019 2:15 PM -08:00', 124) -
            parse('June 7, 2019 12:14:54 PM -08:00')).total_seconds()) <= 30)

