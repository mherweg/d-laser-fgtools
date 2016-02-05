#!/usr/bin/env python
#/usr/bin/python
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

# input:
# textfile after gateway api download or "DSFTool --dsf2text input.dsf output.txt"

##                    show-with*/OBJ.DEF ID                           
#      *from 1=default to 6="totally insane"
#PROPERTY sim/require_agpoint 1/0
#PROPERTY sim/require_object 1/0

#OBJECT_DEF lib/cars/car_static.obj
#OBJECT_DEF lib/airport/Common_Elements/Fueling_Stations/Small_Fuel_Station.obj
#OBJECT_DEF lib/airport/beacons/beacon_airport.obj
#OBJECT_DEF lib/airport/aircraft/GA/KingAirC90B.obj
#OBJECT 0 7.158860481 51.647689739 159.949997
#OBJECT 0 7.158746553 51.647664691 159.949997
#OBJECT 1 7.161123181 51.647699233 341.290009
#OBJECT 2 7.158290237 51.646829664 72.300003
#OBJECT 3 7.159876924 51.648223785 162.470001

import os, sys, getopt
import fgelev
import stg_io2, calc_tile, parameters
from vec2d import vec2d 
import string
import argparse
import logging

logger = logging.getLogger('dsf2stg')
#logger.setLevel("DEBUG")

libfilename="library.txt"

inputfilename="dsf_txt_collection2000/EDDF.txt"
#inputfilename="/mh/LOWW.txt"
path_to_stg =inputfilename
alt = 72

path_to_fgelev = "fgelev"
#path_to_scenery = "/home/mherweg/scenery/2.1/"
path_to_scenery = "/home/mherweg/.fgfs/TerraSync/"

OUR_MAGIC = "dsf2stg"

objects = []
objects_def = {}

class Object_def(object):
    def __init__(self, path, ID):
        path = path.replace('\\', '/')
        splitted = path.strip().split('/')
        self.ID = ID
        if len(splitted) > 1:
            self.prefix = string.join(splitted[:-1], os.sep) + os.sep
        else:
            self.prefix = ""

        self.file, self.ext = os.path.splitext(splitted[-1])
        self.name = self.prefix + os.sep + self.file

    def __str__(self):
        return "%s / %s %g %g %g" % (self.prefix, self.file)


class Object(object):
    def __init__(self, obj_def, lon, lat, hdg, fgpath,zoff, msl=None):
		self.lon = lon
		self.lat = lat
		self.pos = vec2d(lon,lat)
		self.hdg = hdg
		self.msl = msl
        #self.file = obj_def.file
		self.prefix = obj_def.prefix
		self.ext = obj_def.ext
		self.textures_list = []
		self.fgpath=fgpath
		self.zoff=zoff
    def __str__(self):
		return "%s : %g %g %g" % (self.file, self.pos.lon, self.pos.lat, self.hdg)


#library =  {"lib/cars/car_static.obj" : ("Models/Transport/hatchback_red.ac",0,0,0,0), 
            #"lib/airport/Common_Elements/Parking/10_Spaces_dual.obj" : ("Models/StreetFurniture/10_spaces_dual.ac",0,0,0,90), 
            #"lib/airport/Ramp_Equipment/Uni_Jetway_250.obj": ("Models/Airport/Jetway/generic.ac",0,0,0,0),
            #...
            
library = {}

#print library["lib/cars/car_static.obj"][0]

def mk_dirs(path):
    try:
        os.makedirs(path)
    except OSError:
        pass


def read_lib(libfilename):
    try:  
        libfile = open(libfilename, 'r')
    except:
        print "library file ", filename, "not found"
        sys.exit()
    for line in libfile:
        line = line.strip()
        if line.startswith("#"):
            pass
        else:
            cols = line.split()
            #print cols
            #print len(cols)
            if len(cols)==6:
                key = cols[0]
                value = (cols[1],cols[2],cols[3],cols[4],cols[5],)
                library[key]= value
            elif len(cols)==2:
                key = cols[0]
                value = (cols[1],0,0,0,0,)
                library[key]= value
            else:
                if line:
                    print "WARNING: can not parse this line from library:", line
            
    print len(library) , "entries in library.txt"
                

def read_obj_def(infile):
    od=[]
    ID=0
    for line in infile:
        #line = line.strip()
        #print line
        if line.startswith("OBJECT_DEF"):
            cols = line.split()
            xpath = cols[1]
            od.append(xpath)
            obj = Object_def(line[11:], ID)
            objects_def[obj.ID] = obj
            ID += 1
    print ID , "object definitions in source"   
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
                
                o = Object(objects_def[index], lon, lat, heading,fgpath,zoff)  
                objects.append(o)  
            else:
                #pass
                print "no model for", od[index]
    
def jw_init(icao):
	path="Airports"
	#icao="EDDF"    
	for i in range(len(icao)-1):
		path = os.path.join(path, icao[i])
		if os.path.exists(path):
			pass
			#print os.listdir(path)
		else:
			os.mkdir(path)    
            #open file for writing
	gf = '.'.join([icao, 'jetways.xml'])
	path = os.path.join(path, gf)
	f = open(path, 'w')
	f.write('<?xml version="1.0"?>\n')
	f.write('<PropertyList>\n')
	return(f)
	
def jw_entry(o,f,jw_count):
	
	f.write('<jetway n="%d">\n'%(jw_count))
	f.write('  <model type="string">generic</model>\n')
	f.write('  <gate type="string">FG</gate>\n')
	f.write('  <door type="int">1</door>\n')
	f.write('  <airline type="string">FGFS</airline>\n')
	f.write('  <latitude-deg type="double">%s</latitude-deg>\n'%(o.lat))
	f.write('  <longitude-deg type="double">%s</longitude-deg>\n'%(o.lon))
	f.write('  <elevation-m type="double">%s</elevation-m>\n'%(o.msl))
	f.write('  <heading-deg type="double">%s</heading-deg>\n'%(o.hdg))
	f.write('  <initial-position>\n')
	f.write('    <jetway-extension-m type="double">0</jetway-extension-m>\n')
	f.write('    <jetway-heading-deg type="double">0</jetway-heading-deg>\n')
	f.write('    <jetway-pitch-deg type="double">0</jetway-pitch-deg>\n')
	f.write('    <entrance-heading-deg type="double">0</entrance-heading-deg>\n')
	f.write('  </initial-position>\n')
	f.write('</jetway>\n')
		    

def main():
    try:  
        infile = open(inputfilename, 'r')
    except:
        print "input file ", inputfilename, "not found"
        sys.exit()
    #print inputfilename
    n2=os.path.basename(inputfilename)
    (icao,ext)=os.path.splitext(n2)
    print icao
 
    # 1. Init STG_Manager
    parameters.show()
    stg_manager = stg_io2.STG_Manager(parameters.PATH_TO_OUTPUT, OUR_MAGIC, overwrite=True)
    #read translation file
    lib = read_lib(libfilename)
    od = read_obj_def(infile)
    #print od
    infile.seek(0)
    read_obj(infile,od)
    linecount=0
    jw_count=0
    jw_init_flag=False


    elev_prober = fgelev.Probe_fgelev(path_to_fgelev, path_to_scenery,inputfilename)
    logger.info("probing elevation")  
    for o in objects:
		if o.msl == None:
			if True: 
				o.msl = elev_prober(o.pos) + o.zoff
				#o.msl=72
			else:
				o.msl = 72
			logger.debug("object %s: elev probed %s" % (o.fgpath, str(o.msl)))
		else:
			#pass
			logger.debug("object %s: using provided MSL=%g" % (o.fgpath, o.msl))

		if o.fgpath=="Models/Airport/Jetway/jetway.xml":
			#print "jetway"
			if not jw_init_flag:
				f=jw_init(icao)
				jw_init_flag=True
			jw_entry(o,f,jw_count)
			jw_count+=1
		else:
			stg_manager.add_object_shared(o.fgpath , o.pos, o.msl, o.hdg)
			
		linecount+=1
    elev_prober.save_cache()
        
    stg_manager.write()
    print "wrote" , linecount, "stg lines"
    if jw_init_flag:
		f.write('</PropertyList>\n')
		print "wrote"  , jw_count, "jetway.xml entries"
		f.close() 
    print "done."

        

if __name__ == "__main__":
    
    #logger = logging.getLogger()
    
    #logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.WARNING)
    logger.debug("hello")
    
    parser = argparse.ArgumentParser(description="Convert X-plane gateway scenery package to FlightGear")
    parser.add_argument("-i", "--input-path", help="path to x-plane scenery", metavar="PATH", default=None)
    parser.add_argument("-o", "--output-path", help="path to fg scenery", metavar="PATH")
   
    parser.add_argument("-e", "--no-elev", action="store_true", help="don't probe elevation", default=False)
    parser.add_argument("-u", dest="uninstall", action="store_true", help="uninstall ours from .stg")
    parser.add_argument("-l", "--loglevel", help="set loglevel. Valid levels are VERBOSE, DEBUG, INFO, WARNING, ERROR, CRITICAL")
    args = parser.parse_args() 
    
    if args.loglevel:
        parameters.set_loglevel(args.loglevel)
    else:
        parameters.set_loglevel("WARNING")
        
    if args.input_path:
        parameters.INPUT_PATH = args.input_path
        inputfilename = args.input_path
    else:
        parameters.INPUT_PATH = "EDLM.txt"
    if args.output_path:
        parameters.PATH_TO_OUTPUT = args.output_path
   
    main()
