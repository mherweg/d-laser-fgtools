#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Central place to store parameters / settings / variables in osm2city.
All length, height etc. parameters are in meters, square meters (m2) etc.

The assigned values are default values. The Config files will overwrite them

Created on May 27, 2013

@author: vanosten
"""

import argparse
import sys
import types
from os.path import os
from vec2d import vec2d
from pdb import pm

# default_args_start # DO NOT MODIFY THIS LINE
#=============================================================================
# PARAMETERS FOR ALL osm2city MODULES
#=============================================================================

# -- Scenery folder, typically a geographic name or the ICAO code of the airport
#PREFIX = "LSZR"

USE_PKL = False             # -- instead of parsing the OSM file, read a previously created cache file $PREFIX/buildings.pkl
IGNORE_PKL_OVERWRITE = True # -- Ignore overwriting of Cache File

# -- Full path to the scenery folder without trailing slash. This is where we
#    will probe elevation and check for overlap with static objects. Most
#    likely you'll want to use your TerraSync path here.
PATH_TO_SCENERY = "/home/mherweg/.fgfs/TerraSync"

# -- The generated scenery (.stg, .ac, .xml) will be written to this path.
#    If empty, we'll use the correct location in PATH_TO_SCENERY. Note that
#    if you use TerraSync for PATH_TO_SCENERY, you MUST choose a different
#    path here. Otherwise, TerraSync will overwrite the generated scenery.
#    Also make sure PATH_TO_OUTPUT is included in your $FG_SCENERY.
PATH_TO_OUTPUT = "/home/mherweg/scenery/test"

NO_ELEV = False             # -- skip elevation probing
ELEV_MODE = "FgelevCaching" # -- elev probing mode. Possible values are FgelevCaching (recommended), Manual, or Telnet
FG_ELEV = 'fgelev'

# -- Distance between raster points for elevation map. Xx is horizontal, y is
#    vertical. Relevant only for ELEV_MODE = Manual or Telnet.
ELEV_RASTER_X = 10
ELEV_RASTER_Y = 10


def set_loglevel(foo):
    pass

def set_parameters(param_dict):
    for k in param_dict:
        if k in globals():
            if isinstance(globals()[k], types.BooleanType):
                globals()[k] = parse_bool(k, param_dict[k])
            elif isinstance(globals()[k], types.FloatType):
                float_value = parse_float(k, param_dict[k])
                if None is not float_value:
                    globals()[k] = float_value
            elif isinstance(globals()[k], types.IntType):
                int_value = parse_int(k, param_dict[k])
                if None is not int_value:
                    globals()[k] = int_value
            elif isinstance(globals()[k], types.StringType):
                if None is not param_dict[k]:
                    globals()[k] = param_dict[k].strip().strip('"\'')
            elif isinstance(globals()[k], types.ListType):
                globals()[k] = parse_list(param_dict[k])
            else:
                print "Parameter", k, "has an unknown type/value:", param_dict[k]
        else:
            print "Ignoring unknown parameter", k


def get_OSM_file_name():
    """
    Returns the path to the OSM File
    """
    return PREFIX + os.sep + OSM_FILE


def get_center_global():
    cmin = vec2d(BOUNDARY_WEST, BOUNDARY_SOUTH)
    cmax = vec2d(BOUNDARY_EAST, BOUNDARY_NORTH)
    return (cmin + cmax) * 0.5

def get_extent_global():
    cmin = vec2d(BOUNDARY_WEST, BOUNDARY_SOUTH)
    cmax = vec2d(BOUNDARY_EAST, BOUNDARY_NORTH)
    return cmin, cmax

def show():
    """
    Prints all parameters as key = value
    """
    print '--- Using the following parameters: ---'
    my_globals = globals()
    for k in sorted(my_globals.iterkeys()):
        if k.startswith('__'):
            continue
        elif k == "args":
            continue
        elif k == "parser":
            continue
        elif isinstance(my_globals[k], types.ClassType) or \
                isinstance(my_globals[k], types.FunctionType) or \
                isinstance(my_globals[k], types.ModuleType):
            continue
        elif isinstance(my_globals[k], types.ListType):
            value = ', '.join(my_globals[k])
            print k, '=', value
        else:
            print k, '=', my_globals[k]
    print '------'


def parse_list(string_value):
    """
    Tries to parse a string containing comma separated values and returns a list
    """
    my_list = []
    if None is not string_value:
        my_list = string_value.split(',')
        for index in range(len(my_list)):
            my_list[index] = my_list[index].strip().strip('"\'')
    return my_list


def parse_float(key, string_value):
    """
    Tries to parse a string and get a float. If it is not possible, then None is returned.
    On parse exception the key and the value are printed to console
    """
    float_value = None
    try:
        float_value = float(string_value)
    except ValueError:
        print 'Unable to convert', string_value, 'to decimal number. Relates to key', key
    return float_value


def parse_int(key, string_value):
    """
    Tries to parse a string and get an int. If it is not possible, then None is returned.
    On parse exception the key and the value are printed to console
    """
    int_value = None
    try:
        int_value = int(string_value)
    except ValueError:
        print 'Unable to convert', string_value, 'to number. Relates to key', key
    return int_value


def parse_bool(key, string_value):
    """
    Tries to parse a string and get a boolean. If it is not possible, then False is returned.
    """
    if string_value.lower() in ("yes", "true", "on", "1"):
        return True
    if string_value.lower() in ("no", "false", "off", "0"):
        return False
    print "Boolean value %s for %s not understood. Assuming False." % (string_value, key)
    # FIXME: bail out if not understood!
    return False


def read_from_file(filename):
    print 'Reading parameters from file:', filename
    try:
        f = open(filename, 'r')
        param_dict = {}
        full_line = ""
        for line in f:
            # -- ignore comments and empty lines
            line = line.split('#')[0].strip()
            if line == "":
                continue

            full_line += line  # -- allow for multi-line lists
            if line.endswith(","):
                continue

            pair = full_line.split("=", 1)
            key = pair[0].strip().upper()
            value = None
            if 2 == len(pair):
                value = pair[1].strip()
            param_dict[key] = value
            full_line = ""

        set_parameters(param_dict)
        f.close()
    except IOError, reason:
        print "Error processing file with parameters:", reason
        sys.exit(1)

def show_default():
    """show default parameters by printing all params defined above between
        # default_args_start and # default_args_end to screen.
    """
    f = open(sys.argv[0], 'r')
    do_print = False
    for line in f.readlines():
        if line.startswith('# default_args_start'):
            do_print = True
            continue
        elif line.startswith('# default_args_end'):
            return
        if do_print:
            print line,

if __name__ == "__main__":
    # Handling arguments and parameters
    parser = argparse.ArgumentParser(
        description="The parameters module provides parameters to osm2city - used as main it shows the parameters used.")
    parser.add_argument("-f", "--file", dest="filename",
                        help="read parameters from FILE (e.g. params.ini)", metavar="FILE")
    parser.add_argument("-d", "--show-default", action="store_true", help="show default parameters")
    args = parser.parse_args()
    if args.filename is not None:
        read_from_file(args.filename)
        show()
    if args.show_default:
        show_default()

