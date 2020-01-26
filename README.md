# pysoleng: Solar geometry implementation for Python

## Overview
**pysoleng** is a set of python modules that allow for calculating the sun's position, based on the equations provided in _Solar Engineering of Thermal Processes_ (Duffie and Beckman, 2006).  By choice, the geometric equation implementation is coded using
Python's standard library only (_i.e._, packages such as numpy, pytz, and others are not used).  Currently, **pysoleng** has methods for the following:

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


## Future Work
**pysoleng** is in its infancy.  Basic geometric equations are currently provided.  Future directions may include:
- A method that takes an array of hourly `datetime` objects for a year and produces a Pandas dataframe containing each of the key solar position results for each timestamp.
- Providing plotting methods for certain geometric results.
- Incorporating photovoltaic or solar thermal array interactions (_i.e._, estimation of how much solar energy can be captured by a given array).

## Acknowledgements
The infrastructure supporting **pysoleng** comes primarily from the [pyjanitor](https://github.com/ericmjl/pyjanitor) infrastructure.  pyjanitor is an awesome project that is not only the first open-source project I ever contributed to, but also a project that was setup with a complete testing structure, continuous integration, development environment creation, and many other features I had never implemented before (and that I have now implemented, or tried to implement, here).  Therefore, I am greatly indebted to the pyjanitor project.
