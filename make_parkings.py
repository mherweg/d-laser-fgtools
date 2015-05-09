#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

infile = open(sys.argv[1], 'r')

airport = sys.argv[2]

found = False

for line in infile:
            line = line.strip()
            # 1 for airports, 16 for seaports
            if line.startswith("1 "):
                    if " %s "%airport in line:
                            found = True
                            break

if not found:
            print("Airport not found")
            sys.exit(1)

    # Here, we are at the airport

import re
    # There are two lines that describe parkings: line 15 and line 1300
pattern15 = re.compile(r"^15\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
pattern1300 = re.compile(r"^1300\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\w|]*)\s*(.*)$")
                                                                                                                                                                
parkings = []                                                                                                                                                   
for line in infile:                                                                                                                                             
            line = line.strip()                                                                                                                                     
            # If the airport description ends, break                                                                                                               
            if line.startswith("1 "):                                                                                                                               
                    break                                                                                                                                           
                                                                                                                                                                
            lat = -555                                                                                                                                             
            lon = -555
            heading = 0
            result = pattern15.match(line)
            # Math line 15
            if result:
                    lat = float(result.group(1))
                    lon = float(result.group(2))
                    heading = float(result.group(3))
                    name = result.group(4).replace(' ', '_')
            # Match line 1300
            else:
                    result = pattern1300.match(line)
                    if result:
                            lat = float(result.group(1))
                            lon = float(result.group(2))
                            heading = float(result.group(3))
                            # group 4 has the type of aircraft and group 5 is services available at the parking
                            name = result.group(6).replace(' ', '_')
            # If found, convert values
            if lat != -555:
                    if lat < 0:
                            lat2 = "S%d %f"%(int(abs(lat)), (abs(lat) - int(abs(lat)) )* 60)
                    else:
                            lat2 = "N%d %f"%(int(abs(lat)), (abs(lat) - int(abs(lat)) )* 60)
                    if lon < 0:
                            lon2 = "W%d %f"%(int(abs(lon)), (abs(lon) - int(abs(lon)) )* 60)
                    else:
                            lon2 = "E%d %f"%(int(abs(lon)), (abs(lon) - int(abs(lon)) )* 60)
                    parkings.append((lat2, lon2, heading, name),)

infile.close()

i = 0
print('<?xml version="1.0"?>\n<groundnet>\n    <parkingList>')
for p in parkings:
            print('        <Parking index="%d" type="gate" name="%s" lat="%s" lon="%s" heading="%f" />'%(i, p[3], p[0], p[1], p[2]))
            i = i + 1
print("    </parkingList>\n</groundnet>")


