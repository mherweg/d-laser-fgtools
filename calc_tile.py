#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
shamelessly translated from calc-tile.pl
"""
import os
from math import floor
import numpy as np


def bucket_span(lat):
    """Latitude Range -> Tile Width (deg)"""
    alat = abs(lat)
    if alat >= 89:
        return 360
    if alat >= 88:
        return 8
    if alat >= 86:
        return 4
    if alat >= 83:
        return 2
    if alat >= 76:
        return 1
    if alat >= 62:
        return .5
    if alat >= 22:
        return .25
    return .125


def format_lon(lon):
    """Format longitude as e/w."""
    if lon < 0.:
        return "w%03d" % int(0. - lon)
    else:
        return "e%03d" % int(lon)


def format_lat(lat):
    """Format latitude as n/s."""
    if lat < 0.:
        return "s%02d" % int(0. - lat)
    else:
        return "n%02d" % int(lat)


def root_directory_name(position):
    lon=position[0]
    lat=position[1]
    """Generate the directory name for a location."""
    lon_chunk = floor(lon/10.0) * 10
    lat_chunk = floor(lat/10.0) * 10
    return format_lon(lon_chunk) + format_lat(lat_chunk) + os.sep 


def directory_name(position):
    lon=position[0]
    lat=position[1]
    """Generate the directory name for a location."""
    lon_floor = floor(lon)
    lat_floor = floor(lat)
    lon_chunk = floor(lon/10.0) * 10
    lat_chunk = floor(lat/10.0) * 10
    return format_lon(lon_chunk) + format_lat(lat_chunk) + os.sep \
         + format_lon(lon_floor) + format_lat(lat_floor)


def tile_index(position, x=0, y=0):
    lon=position[0]
    lat=position[1]
    if x == 0 and y == 0:
        y = calc_y(lat)
        x = calc_x(lon, lat)

    index = (int(floor(lon)) + 180) << 14
    index += (int(floor(lat)) + 90) << 6
    index += y << 3
    index += x
    #print("tile_index " + str(index))
    return index


def construct_path_to_stg(base_directory, center_global):
    """Returns the path to the stg-files in a FG scenery directory hierarchy at a given global lat/lon location"""
    return base_directory + os.sep + 'Objects' + os.sep + directory_name(center_global) + os.sep


def construct_stg_file_name(center_global):
    """Returns the file name of the stg-file at a given global lat/lon location"""
    filename = str(tile_index(center_global)) + ".stg"
    print ("construct_stg_file_name: " + filename)
    return filename
	

def construct_btg_file_name(center_global):
    """Returns the file name of the stg-file at a given global lat/lon location"""
    return "%07i.btg.gz" % tile_index(center_global)


def get_north_lat(lat, y):
    return float(floor(lat)) + y / 8.0 + .125


def get_south_lat(lat, y):
    return float(floor(lat)) + y / 8.0


def get_west_lon(lon, lat, x):
    if x == 0:
        return float(floor(lon))
    else: 
        return float(floor(lon)) + x * (bucket_span(lat))


def get_east_lon(lon, lat, x):
    if x == 0:
        return float(floor(lon)) + (bucket_span(lat))
    else: 
        return float(floor(lon)) + x * (bucket_span(lat)) + (bucket_span(lat))


def calc_x(lon, lat):
    """
    FIXME: is this correct? Also: some returns do not take calculations into account.
    According to http://wiki.flightgear.org/Tile_Index_Scheme it would be calculated differently
    """
    EPSILON = 0.0000001
    span = bucket_span(lat)
    if span < EPSILON:
        lon = 0
        return 0
    elif span <= 1.0:
        return int((lon - floor(lon)) / span)
    else:
        if lon >= 0:
            lon = int(int(lon/span) * span)
        else:
            lon = int(int((lon+1)/span) * span - span)
            if lon < -180:
                lon = -180
        return 0


def calc_y(lat):
    return int((lat - floor(lat)) * 8)
    

def get_stg_files_in_boundary(boundary_west, boundary_south, boundary_east, boundary_north, path_to_scenery):
    """Based on boundary rectangle returns a list of stg-files (incl. full path) to be found within the boundary of
    the scenery"""
    stg_files = []
    for my_lat in np.arange(boundary_south, boundary_north, 0.125):  # latitude
        for my_lon in np.arange(boundary_west, boundary_east, bucket_span(my_lat)):  # longitude
            coords = (my_lon, my_lat)
            stg_files.append(construct_path_to_stg(path_to_scenery, coords) + construct_stg_file_name(coords))
    return stg_files


if __name__ == "__main__":
    for lon, lat, idx in ((13.687944, 51.074664, 3171138),
                          (13.9041667, 51.1072222, 3171139),
                          (13.775, 51.9638889, 3171195),
                          (0.258094, 29.226081, 2956745),
                          (-2.216667, 30.008333, 2907651)):
        print (tile_index([lon, lat]) - idx)
        print (directory_name([lon, lat]))
