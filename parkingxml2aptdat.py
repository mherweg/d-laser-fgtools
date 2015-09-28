#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  (C) 2015 d-laser  http://wiki.flightgear.org/User:Laserman
# --------------------------------------------------------------------------
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# --------------------------------------------------------------------------

# convert from Flightgear/TaxiDraw parking.xml or ICAO.groundnet.xml
# to "1300" type lines in apt.dat format
#
# you will find input files for this script in $FGDATA/AI/Airports
# and $FGDATA/Airports/?/?/?/
#
#  purpose: to merge parking locations from legacy files
#  and edit them all together in WED
#  
#  hot to use:
#
# download the latest apt.dat of your airport,
# open it in a text editor,
# insert the lines that this script made
# save the file
# in WED: import apt.dat
# remove duplicates




import sys, getopt
import xml.etree.ElementTree as ET
def convert_to_decimal(foo):
    lonl = foo.split(' ')
    #print lonl[0] , lonl[1]
    lon = lonl[0].replace('W', '-')
    lon = lon.replace('E', '')
    lon = lon.replace('N', '')
    lon = lon.replace('S', '-')
    #print lon 
    dlon = float(lon) + (float(lonl[1])/60)
    #print dlon
    return dlon
    
def convert_to_decimal_lat(lat):
    
    return 0
    
    
    
def main(argv):
    helptext = 'parkingxml2aptdat.py -i <inputfile> '
    #inputfile = "Airports/E/D/D/EDDF.groundnet.xml"

    heading = 0
    
    try:
        opts, args = getopt.getopt(argv,"hi:")
    except getopt.GetoptError:
        print helptext
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helptext
            sys.exit()
        elif opt == "-i":
            inputfile = arg
      
    print 'Input file is ', inputfile
    #print 'Number of arguments:', len(sys.argv), 'arguments.'
    #print 'Argument List:', str(sys.argv)

    tree = ET.parse(inputfile)
    root = tree.getroot()
    xp_type = "heavy|jets"
    xp_service = "gate"
    for child in root:
        if child.tag == 'parkingList':
            print child.tag,child.attrib
            for cc in child:
                #print cc.tag,cc.attrib
                if cc.tag == 'Parking':
                    # <Parking index="0" type="gate" name="V109" lat="N50 2.991748" lon="E8 35.487733" heading="160.6"  radius="44" pushBackRoute="92" airlineCodes="" />
                    #print cc.attrib['index'] , cc.attrib['type'], cc.attrib['name'] , cc.attrib['number'], cc.attrib['lat'] , cc.attrib['lon'], cc.attrib['heading'] , cc.attrib['radius']
                    
                    name =   cc.attrib['name'] 
                    if "number" in cc.attrib:
                        name = name + cc.attrib['number'] 
                    heading = cc.attrib['heading']
                    lon = convert_to_decimal(cc.attrib['lon']) 
                    lat = convert_to_decimal(cc.attrib['lat'])
                    #1300  51.64821489  007.16123693  74.61 tie_down turboprops|props Apron start 3
                    print "1300", lat, lon, heading, xp_service, xp_type, name
                 
                    
if __name__ == "__main__":
    main(sys.argv[1:])
