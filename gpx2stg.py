#!/usr/bin/python

# gpx2stg.py by d-laser
#
# reads a .gpx file of points that i export from JOSM
# writes stg formated to stdout
#

import sys, getopt
import xml.etree.ElementTree as ET

helptext = 'gpx2stg.py -i <inputfile> -m <path to shared model> -e <elevation>'

def main(argv):
    model = "Models/Industrial/GenericStorageTank15m.ac"
    elev  = 50
    heading = 0
    inputfile = "kugeln.gpx" 
    outputfile=''
    
    try:
        opts, args = getopt.getopt(argv,"hi:m:e:")
    except getopt.GetoptError:
        print helptext
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helptext
            sys.exit()
        elif opt == "-i":
            inputfile = arg
        elif opt == "-m":
            model = arg
        elif opt == "-e":
            elev = arg
    #print 'Input file is ', inputfile
    #print 'Output file is ', outputfile
    #print 'Number of arguments:', len(sys.argv), 'arguments.'
    #print 'Argument List:', str(sys.argv)

    tree = ET.parse(inputfile)
    root = tree.getroot()

    for child in root:
        point = child.attrib
        if point:
            print "OBJECT_SHARED", model, point['lon'],point['lat'], elev, heading 
	    # for upload: elev -> offset to AGL
         #   print "OBJECT_SHARED", model, point['lon'],point['lat'], 0.0, heading ,elev
        
if __name__ == "__main__":
   main(sys.argv[1:])
