# pysoleng: Solar geometry implementation for Python

## Overview
**pysoleng** is a set of python modules that allow for calculating the sun's position, based on the equations provided in _Solar Engineering of Thermal Processes_ (Duffie and Beckman, 2006).  Currently, **pysoleng** has methods for the following:

- Calculating the day number from a date (out of 365, or 366 for leap years)
- Calculating the extraterrestrial radiation incident on the plane normal to the radiation on a specific day of the year
- Calculating the [equation of time](https://en.wikipedia.org/wiki/Equation_of_time)
- Converting local standard time to solar time
- Calculating the declination angle: the angular position of the sun at solar noon with respect to the plane of the equator
- Calculating the hour angle: the angular displacement of the sun east or west of the local meridian due to rotation of the earth on its axis at 15 degrees per hour
- Calculating the solar zenith angle: the angle between the vertical and the line to the sun, that is, the angle of incidence of beam radiation on a horizontal surface
- Calculating the solar altitude angle: the complement to the solar zenith angle
- Calculating the air mass: the ratio of the mass of atmosphere through which beam radiation passes to the mass it would pass through if the sun were at the zenith
- Calculating the solar azimuth angle: the angular displacement from south of the projection of beam radiation on the horizontal plane
- Calculating solar noon in local standard time for a given day and location 

## Example Use
To use all of the pysoleng's current functionality, the setup is relatively simple.  After importing `pandas` and `pysoleng`, create a `DataFrame` with a time series column.  Then, specify the latitude, longitude, and elevation of the location you desire to analyze (note that `pysoleng` does not currently have the functionality to properly handle daylight savings time):

```python
from pysoleng.solar_geom import *
import pandas as pd

df_pre = pd.DataFrame({
    "local_time": pd.date_range("2020-01-01 00:00 -07:00",
              
                                periods=366 * 24,
                                freq="H")
})
latitude = 33.4484 # degrees North
longitude = 112.0740 # degrees West
elevation = 331 # meters
```

After this setup, you can run a simple `assign()` command to generate all of the `pysoleng` properties at once:

```python
df = df_pre.assign(
    solar_time=convert_to_solar_time(df_pre["local_time"], longitude),
    local_day_num=calculate_day_number(df_pre["local_time"]),
    local_solar_noon=calculate_solar_noon_in_local_standard_time(df_pre["local_time"], longitude),
    B_degrees=lambda x: calculate_B_degrees(x["local_day_num"]),
    G_on_W_m2=lambda x: calculate_G_on_W_m2(x["B_degrees"], G_sc),
    E_min=lambda x: calculate_E_min(x["B_degrees"]),
    declination_angle_degrees=lambda x: calculate_declination_degrees(x["B_degrees"]),
    hour_angle_degrees=calculate_hour_angle_degrees(df_pre["local_time"], longitude),
    solar_zenith_degrees=lambda x: calculate_solar_zenith_degrees(latitude, x["declination_angle_degrees"], x["hour_angle_degrees"]),
    solar_altitude_degrees=lambda x: calculate_solar_altitude_degrees(x["solar_zenith_degrees"]),
    air_mass=lambda x: calculate_air_mass(x["solar_zenith_degrees"], elevation),
    solar_azimuth_degrees=lambda x: calculate_solar_azimuth_degrees(x["hour_angle_degrees"], latitude, x["declination_angle_degrees"]) 
)
```

This will produce a `DataFrame` containing all of the `pysoleng` properties for each time stamp.  For this example, the transposed `DataFrame` looks like:

'|                           | 0                                | 1                                | 2                                | 3                                | 4                                |\n|:--------------------------|:---------------------------------|:---------------------------------|:---------------------------------|:---------------------------------|:---------------------------------|\n| local_time                | 2020-01-01 00:00:00-07:00        | 2020-01-01 01:00:00-07:00        | 2020-01-01 02:00:00-07:00        | 2020-01-01 03:00:00-07:00        | 2020-01-01 04:00:00-07:00        |\n| solar_time                | 2019-12-31 23:28:47.974656-07:00 | 2020-01-01 00:28:47.974656-07:00 | 2020-01-01 01:28:47.974656-07:00 | 2020-01-01 02:28:47.974656-07:00 | 2020-01-01 03:28:47.974656-07:00 |\n| local_day_num             | 1                                | 1                                | 1                                | 1                                | 1                                |\n| local_solar_noon          | 2020-01-01 12:31:12.025344-07:00 | 2020-01-01 12:31:12.025344-07:00 | 2020-01-01 12:31:12.025344-07:00 | 2020-01-01 12:31:12.025344-07:00 | 2020-01-01 12:31:12.025344-07:00 |\n| B_degrees                 | 0.0                              | 0.0                              | 0.0                              | 0.0                              | 0.0                              |\n| G_on_W_m2                 | 1414.91335                       | 1414.91335                       | 1414.91335                       | 1414.91335                       | 1414.91335                       |\n| E_min                     | -2.9044223999999996              | -2.9044223999999996              | -2.9044223999999996              | -2.9044223999999996              | -2.9044223999999996              |\n| declination_angle_degrees | -23.058629169260467              | -23.058629169260467              | -23.058629169260467              | -23.058629169260467              | -23.058629169260467              |\n| hour_angle_degrees        | 172.19989439999998               | -172.80010560000002              | -157.80010560000002              | -142.80010560000002              | -127.80010560000002              |\n| solar_zenith_degrees      | 90.0                             | 90.0                             | 90.0                             | 90.0                             | 90.0                             |\n| solar_altitude_degrees    | 0.0                              | 0.0                              | 0.0                              | 0.0                              | 0.0                              |\n| air_mass                  | 36.306578259566194               | 36.306578259566194               | 36.306578259566194               | 36.306578259566194               | 36.306578259566194               |\n| solar_azimuth_degrees     | 62.003579805636065               | -62.003579805636065              | -62.003579805636065              | -62.003579805636065              | -62.003579805636065              |'

## Future Work
**pysoleng** is in its infancy.  Basic geometric equations are currently provided.  Future directions may include:
- A method that takes an array of hourly `datetime` objects for a year and produces a Pandas dataframe containing each of the key solar position results for each timestamp.
- Providing plotting methods for certain geometric results.
- Incorporating photovoltaic or solar thermal array interactions (_i.e._, estimation of how much solar energy can be captured by a given array).

## Acknowledgements
The infrastructure supporting **pysoleng** comes primarily from the [pyjanitor](https://github.com/ericmjl/pyjanitor) infrastructure.  pyjanitor is an awesome project that is not only the first open-source project I ever contributed to, but also a project that was setup with a complete testing structure, continuous integration, development environment creation, and many other features I had never implemented before (and that I have now implemented, or tried to implement, here).  Therefore, I am greatly indebted to the pyjanitor project.
