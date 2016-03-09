#!/usr/bin/python

# conv-timezone.py  
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

# input file format: .conf
# see: http://wiki.flightgear.org/Interactive_traffic#Tools
#


import sys, getopt, re
import fileinput, subprocess
import pytz
from datetime import datetime, time

helptext = 'localtime2utc.py -i <inputfile> -z <timezone>\nexample:\nlocaltime2utc.py  -i peach.conf -z "Asia/Tokyo" > out.conf'

def convert_to_utc(tstring,zone):
    ldt="2000." + tstring
    ltime = datetime.strptime(ldt,"%Y.%H:%M")
    local = pytz.timezone (zone)
    local_dt = local.localize(ltime)
    utc_dt = local_dt.astimezone(pytz.utc)         
    return( utc_dt.strftime("%H:%M") )
    

def convert2stdout(conf_file,zone):

    for line in fileinput.input(files=(conf_file),inplace=0, backup='.bak'):
        if line.startswith("FLIGHT "):
            col =  line.split()
            col[4] = convert_to_utc(col[4],zone)
            col[6] = convert_to_utc(col[6],zone)
            #print col
            outline= " ".join(col)
            print outline
        else:
            print line.rstrip('"\r\n')
            
def main(argv):
    
    delta=0
    conf_file="../AI/peach.conf"
    zone = "Asia/Tokyo"
    
    try:
        opts, args = getopt.getopt(argv,"hi:z:")
    except getopt.GetoptError:
        print helptext
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helptext
            sys.exit()
        elif opt == "-i":
            conf_file = arg
        elif opt == "-z":
            zone = arg  
            
                
    print '#Input file is ', conf_file
    print "#converted from timezone", zone , "to UTC by convert-timezone.py "
    #print 'Number of arguments:', len(sys.argv), 'arguments.'
    #print 'Argument List:', str(sys.argv)
    convert2stdout(conf_file, zone)
    
        
if __name__ == "__main__":
    main(sys.argv[1:])


