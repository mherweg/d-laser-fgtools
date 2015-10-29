#!/usr/bin/python
# -*- coding: utf-8 -*-

# taxisigns2stg.py  
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

#  reads X-plane/WED/Flightgear apt.dat Lines with taxi-sign information 
# (lines that begin with "20")
# and writes stg lines for Flightgear scenery to stdout

# known limitation :
# * elevation is fixed for all signs 



import sys, getopt
import re
helptext = 'taxisigns2stg.py -f <input apt.dat file> -i <ICAO> -e <elevation>'


def main(argv):
   
    elev  = 500
    heading = 0
    filename = "EDDG.dat" 
    airport = 'EDDG'
   
    try:
        opts, args = getopt.getopt(argv,"hf:i:e:")
    except getopt.GetoptError:
        print helptext
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helptext
            sys.exit()
        elif opt == "-f":
            filename = arg
        elif opt == "-i":
            airport = arg
        elif opt == "-e":
            elev = arg

    infile = open(filename, 'r')

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

        #                          l             l             heading          0            size           text
    pattern20 = re.compile(r"^20\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
    count=0                                                                                                                                                   
    for line in infile:                                                                                                                                             
                line = line.strip()                                                                                                                                     
                # If the airport description ends, break                                                                                                               
                if line.startswith("1 "):                                                                                                                               
                        break                                                                                                                                           
                                                                                                                                                                    
                lat = -555                                                                                                                                             
                lon = -555
                heading = 0
               
                result = pattern20.match(line)
                
                # Match line 20
                if result:
                        lat = float(result.group(1))
                        lon = float(result.group(2))
                        # apt.dat: Orientation of sign in true degrees (heading of someone looking at sign’s front)
                        # STG: the same but counter clockwise ?
                        #wed-heading = float(result.group(3))
                        # is this correct ???
                        heading = 360 - float(result.group(3))
                        
                        #print lat, lon , heading  
                        size = result.group(5)
                        text = result.group(6)
                        # OBJECT_SIGN <text> <longitude> <latitude> <elevation-m> <heading-deg> <size>
                        print "OBJECT_SIGN", text, lon , lat, elev, heading, size
                        count+=1
                        
               
    if count == 0:
        print "The input file did not contain any Taxi Signs for airport", airport
                  
    infile.close()



               
if __name__ == "__main__":
    main(sys.argv[1:])



