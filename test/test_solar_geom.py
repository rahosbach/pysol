import datetime as dt
import unittest

from dateutil.parser import *
from pysol.solar_geom import Solar_Geometry

from pdb import set_trace as bp

class SolarGeomTest(unittest.TestCase):
    def setUp(self):
        self.solar_geometry = Solar_Geometry()

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
    
    def test_calculate_G_on(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_G_on(1), 1414.91335, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_G_on(182), 1328.5414, places=4)

    def test_calculate_E(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_E(1), -2.9044, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_E(34), -13.4885, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_E(304), 16.3751, places=4)

    def test_calculate_solar_time(self):
        self.assertTrue(abs(
            (self.solar_geometry.calculate_solar_time('February 3, 2019 10:30 AM -06:00', 89.4, False) -
            parse('February 3, 2019 10:19 AM -06:00')).total_seconds()) <= 30)
        self.assertTrue(abs(
            (self.solar_geometry.calculate_solar_time('February 3, 2019 10:30 AM -05:00', 89.4, True) -
            parse('February 3, 2019 9:19 AM -06:00')).total_seconds()) <= 30)
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM -02:00', 375., False))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM -02:00', 'long', False))
        self.assertRaises(ValueError, lambda: self.solar_geometry.calculate_solar_time('1/1/2019 8:00 AM', 100., False))
        self.assertWarns(Warning, lambda: self.solar_geometry.calculate_solar_time('10:00 AM -02:00', 100., False))

    def test_calculate_declination(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_declination(47), -12.6090, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_declination(105), 9.4808, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_declination(344), -22.8406, places=4)

    def test_calculate_hour_angle(self):
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle(parse("10:30 AM")), -22.5, places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle(parse("12/31/2019 11:00 AM -02:00")), -15., places=4)
        self.assertAlmostEqual(self.solar_geometry.calculate_hour_angle(parse("June 10, 2002 5:47 PM")), 86.7500, places=4)

    def test_calculate_air_mass(self):
        pass