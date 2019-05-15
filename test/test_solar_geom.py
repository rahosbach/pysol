import datetime as dt
import unittest

from dateutil.parser import *
from pysol.solar_geom import Solar_Geometry

from pdb import set_trace as bp

class SolarGeomTest(unittest.TestCase):
    def setUp(self):
        self.solar_geometry = Solar_Geometry(
            G_sc=1367.,
            latitude=40.8665,
            longitude=124.0828,
            local_standard_time='May 1, 2019 12:00 PM -08:00')

    def test_calculate_day_number_from_date(self):
        self.assertEqual(self.solar_geometry.calculate_day_number_from_date('January 2, 2018'), 2)
        self.assertEqual(self.solar_geometry.calculate_day_number_from_date('1/2/2018'), 2)
        self.assertEqual(self.solar_geometry.calculate_day_number_from_date('20180102'), 2)
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_day_number_from_date('20183535'))

    def test_calculate_B(self):
        self.assertEqual(self.solar_geometry.calculate_B(1), 0)
        self.assertAlmostEqual(self.solar_geometry.calculate_B(10), 8.8767, places=4)
        self.assertEqual(self.solar_geometry.calculate_B('January 1, 2019'), 0)
        self.assertAlmostEqual(self.solar_geometry.calculate_B('1/10/2019'), 8.8767, places=4)
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_B(0))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_B(366))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_B('R'))
    
    def test_calculate_G_on_W_m2(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_G_on_W_m2(1), 1414.91335, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_G_on_W_m2(182), 1328.5414, places=4)

    def test_calculate_E(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_E(1), -2.9044, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_E(34), -13.4885, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_E(304), 16.3751, places=4)

    def test_calculate_solar_time(self):
        self.assertTrue(abs(
            (self.solar_geometry.calculate_solar_time('February 3, 2019 10:30 AM -06:00', 89.4) -
            parse('February 3, 2019 10:19 AM -06:00')).total_seconds()) <= 30)
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM -02:00', 375.))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM -02:00', 'long'))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM', 100.))
        self.assertWarns(Warning, lambda: self.solar_geometry.calculate_solar_time('10:00 AM -02:00', 100.))

    def test_calculate_declination_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_declination_degrees(47), -12.6090, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_declination_degrees(105), 9.4808, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_declination_degrees(344), -22.8406, places=4)

    def test_calculate_hour_angle_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle_degrees(parse("10:30 AM")), -22.5, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle_degrees(parse("12/31/2019 11:00 AM -02:00")), -15., places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle_degrees(parse("June 10, 2002 5:47 PM")), 86.7500, places=4)

    def test_calculate_solar_zenith_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_zenith_degrees("February 13, 9:30 AM", 43), 66.2222, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_zenith_degrees("July 1, 6:30 PM", 43), 79.5917, places=4)

    def test_calculate_solar_altitude_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_altitude_degrees("February 13, 9:30 AM", 43), 23.7778, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_altitude_degrees("July 1, 6:30 PM", 43), 10.4083, places=4)

    def test_calculate_air_mass(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_air_mass(60.), 2.0000, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_air_mass(0.), 1.0000, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_air_mass(70.), 2.9238, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_air_mass(71., 0.), 3.0471, places=4)
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_air_mass(71.))

    def test_calculate_solar_azimuth_degrees(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_azimuth_degrees(-37.5, 66.5, 43., -14.), -39.9886, places=4 )
        self.assertAlmostEqual(self.solar_geometry.calculate_solar_azimuth_degrees(97.5, 79.6, 43., 23.1), 111.9789, places=4 )

    def test_calculate_solar_noon_in_local_time(self):
        self.assertTrue(abs(
            (self.solar_geometry.calculate_solar_noon_in_local_time('February 3, 2019 10:30 AM -06:00', 89.4) -
            parse('February 3, 2019 12:11:25 PM -06:00')).total_seconds()) <= 30)
        self.assertTrue(abs(
            (self.solar_geometry.calculate_solar_noon_in_local_time('June 7, 2019 2:15 PM -08:00', 124) -
            parse('June 7, 2019 12:14:54 PM -08:00')).total_seconds()) <= 30)

