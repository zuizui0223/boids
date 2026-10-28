#!/usr/bin/env python3
"""v17 pure environmental geometry: solar position and wind support/crosswind.

No animals, records, GPS trajectories or fitted effects. Mathematical features
must be computed from *verified* UTC/location and an independently verified
meteorological wind-from bearing. Wind status from unknown clock is forbidden.
NOAA solar approximation has small errors and is NOT a measure of cloudiness,
sun visibility, information reliability, or a pigeon's internal clock.
"""
from __future__ import annotations

import datetime as dt
import math


def wrapped_degrees(angle: float) -> float:
    if not math.isfinite(angle):
        raise ValueError("Nonfinite directional angle")
    return (angle + 180.) % 360. - 180.


def wind_components(wind_speed_m_s: float, wind_from_bearing_deg: float,
                    bird_heading_deg: float) -> dict:
    """Meteorological *wind-from* -> wind-to, then support/crosswind.

    +tailwind supports bird heading. +crosswind is wind displacement to right
    of bird heading, with both bearings clockwise from true north.
    A weather-station raw bearing is not admitted until FROM/TO convention
    and units have independently been checked.
    """
    if (not all(map(math.isfinite,(wind_speed_m_s,
                                 wind_from_bearing_deg,bird_heading_deg)))
        or wind_speed_m_s<0 or wind_speed_m_s>75):
        raise ValueError("Wind source units or magnitude not permitted")
    wind_to = (wind_from_bearing_deg+180.) % 360.
    theta=math.radians(wrapped_degrees(wind_to-bird_heading_deg))
    return {
        "tailwind_support_m_s":wind_speed_m_s*math.cos(theta),
        "signed_crosswind_m_s":wind_speed_m_s*math.sin(theta),
        "crosswind_abs_m_s":abs(wind_speed_m_s*math.sin(theta)),
        "wind_to_bearing_deg":wind_to,
    }


def solar_azimuth_elevation(time_utc:dt.datetime,lat_deg:float,lon_deg_east:float)->dict:
    """NOAA fractional-year approximation, no refraction correction.

    Sources: https://gml.noaa.gov/grad/solcalc/solareqns.PDF
    Longitude is POSITIVE east; azimuth clockwise from geographic north.
    Dates must have timezone info. Naive and ambiguous 'local' times rejected.
    """
    if time_utc.tzinfo is None or time_utc.utcoffset() is None:
        raise ValueError("UTC source timestamp must be timezone-aware")
    if not (-90<=lat_deg<=90 and -180<=lon_deg_east<=180):
        raise ValueError("Invalid site coordinates")
    if not all(map(math.isfinite,(lat_deg,lon_deg_east))):
        raise ValueError("Nonfinite site coordinates")
    moment=time_utc.astimezone(dt.timezone.utc)
    leap=(moment.year%4==0 and (moment.year%100!=0 or moment.year%400==0))
    number_of_days=366 if leap else 365
    day=moment.timetuple().tm_yday
    utc_fractional_hours=(moment.hour+moment.minute/60+
                         moment.second/3600+moment.microsecond/3.6e9)
    gamma=2*math.pi/number_of_days*(day-1+(utc_fractional_hours-12)/24)
    equation_time=229.18*(.000075+.001868*math.cos(gamma)
                         -.032077*math.sin(gamma)
                         -.014615*math.cos(2*gamma)
                         -.040849*math.sin(2*gamma))
    decl=.006918-.399912*math.cos(gamma)+.070257*math.sin(gamma)
    decl+=-.006758*math.cos(2*gamma)+.000907*math.sin(2*gamma)
    decl+=-.002697*math.cos(3*gamma)+.00148*math.sin(3*gamma)
    true_solar_minutes=(utc_fractional_hours*60+equation_time+
                        4*lon_deg_east)%1440.
    hour_angle=math.radians(true_solar_minutes/4-180)
    lat=math.radians(lat_deg)
    coszen=(math.sin(lat)*math.sin(decl)+
            math.cos(lat)*math.cos(decl)*math.cos(hour_angle))
    zenith=math.acos(max(-1.,min(1.,coszen)))
    elev=90-math.degrees(zenith)
    az=math.degrees(math.atan2(math.sin(hour_angle),
                              math.cos(hour_angle)*math.sin(lat)
                              -math.tan(decl)*math.cos(lat)))+180.
    return {
        "solar_azimuth_deg_north_clockwise": az%360.,
        "solar_elevation_deg":elev,
        "equation_of_time_min":equation_time,
        "noaa_approximation_without_refraction":True,
        "actual_cloud_visibility_known":False,
        "animal_circadian_phase_known":False,
    }


def relative_solar_bearing(bird_heading_deg:float,solar_azimuth_deg:float)->float:
    return wrapped_degrees(bird_heading_deg-solar_azimuth_deg)


if __name__=="__main__":
    raise SystemExit("Pure context module only; no standalone GPS analysis")
