#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Martin Herweg    m.herweg@gmx.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

# work in porgress 


# input:
# textfile after gateway api download or DSFTool --dsf2text input.dsf output.txt

#OBJECT_DEF lib/cars/car_static.obj
#OBJECT_DEF lib/airport/Common_Elements/Fueling_Stations/Small_Fuel_Station.obj
#OBJECT_DEF lib/airport/beacons/beacon_airport.obj
#OBJECT_DEF lib/airport/aircraft/GA/KingAirC90B.obj
#OBJECT 0 7.158582390 51.647581197 341.390015
#OBJECT 0 7.158697215 51.647606802 341.390015
#OBJECT 0 7.158960952 51.647664134 341.390015
#OBJECT 0 7.159010291 51.647721467 159.949997
#OBJECT 0 7.158626347 51.647817207 159.949997
#OBJECT 0 7.158860481 51.647689739 159.949997
#OBJECT 0 7.158746553 51.647664691 159.949997
#OBJECT 1 7.161123181 51.647699233 341.290009
#OBJECT 2 7.158290237 51.646829664 72.300003
#OBJECT 3 7.159876924 51.648223785 162.470001

import os, sys, getopt

inputfilename="EDLM.txt"
alt = 72

library =  {"lib/cars/car_static.obj" : ("Models/Transport/hatchback_red.ac",0,0,0,0), 
            "lib/airport/Common_Elements/Parking/10_Spaces_dual.obj" : ("Models/StreetFurniture/10_spaces_dual.ac",0,0,0,90), 
            "lib/airport/Ramp_Equipment/Uni_Jetway_250.obj": ("Models/Airport/Jetway/generic.ac",0,0,0,0),
            "lib/airport/Ramp_Equipment/Uni_Jetway_400.obj": ("Models/Airport/Jetway/generic.ac",0,0,0,0),
            "lib/airport/Ramp_Equipment/Uni_Jetway_500.obj": ("Models/Airport/Jetway/generic.ac",0,0,0,0),
            "lib/airport/Ramp_Equipment/Uni_Jetway_250.obj": ("Models/Airport/Jetway/generic.ac",0,0,0,0),
            "lib/airport/Ramp_Equipment/Ramp_Parking_Stripe.obj": ("Models/Airport/RampParkingStripe.ac",0,0,0,0),
            "lib/g10/global_objects/CafeTbls4x2.obj": ("Models/Misc/picnic_table.ac",0,0,0,0),
            "lib/airport/Common_Elements/Miscellaneous/Picnic_Table.obj": ("Models/Misc/picnic_table.ac",0,0,0,0),
            "lib/airport/Ramp_Equipment/GPU_1.obj":  ("Models/Airport/Vehicles/generic-GPU.xml",0,0,0,0),
            "lib/g10/forests/autogen_tree1.obj": ("Models/Trees/deciduous-tree.xml",0,0,0,0), 
            "lib/g10/forests/autogen_tree2.obj": ("Models/Trees/deciduous-tree.xml",0,0,0,0), 
            "lib/g10/forests/autogen_tree3.obj": ("Models/Trees/deciduous-tree.xml",0,0,0,0), 
            "lib/g10/forests/autogen_tree4.obj": ("Models/Trees/deciduous-tree.xml",0,0,0,0),
        }


#print library["lib/cars/car_static.obj"][0]




def read_obj_def(infile):
    od=[]
    for line in infile:
        line = line.strip()
        #print line
        if line.startswith("OBJECT_DEF "):
            cols = line.split()
            xpath = cols[1]
            od.append(xpath)
    return od

def read_obj(infile,od):
    for line in infile:
        line = line.strip()
        
        if line.startswith("OBJECT "):
            col = line.split()
            index = int(col[1])
            if od[index] in library:
                libtupel = library[od[index]]
                fgpath = libtupel[0]
                xoff = float(libtupel[1])
                yoff = float(libtupel[2])
                zoff = float(libtupel[3])
                hoff = float(libtupel[4])
                lon = float(col[2])
                lat =float(col[3])
                heading = (360 - float(col[4]) ) +hoff
                if heading >= 360:
                    heading = heading - 360
                print "OBJECT_SHARED ", fgpath, lon+xoff, lat+yoff, alt+zoff, heading+hoff
    
    

def main(argv):
    
    try:  
        infile = open(inputfilename, 'r')
    except:
        print "input file ", filename, "not found"
        sys.exit()
    
    od = read_obj_def(infile)
    #print od
    infile.seek(0)
    read_obj(infile,od)
        
   
           


if __name__ == "__main__":
   main(sys.argv[1:])
