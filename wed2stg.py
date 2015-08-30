#!/usr/bin/python




#<?xml version="1.0" encoding="UTF-8"?>
#<doc>
#    <objects>
#   <object class="WED_ObjPlacement" id="75" parent_id="5">
#            <sources/>
#            <viewers/>
#            <children/>
#            <hierarchy hidden="0" locked="0" name="P180_avanti_ferrari.obj"/>
#            <point heading="4.93" latitude="45.811811394" longitude="15.113382618"/>
#            <obj_placement custom_msl="0" msl="0.000" resource="objects/Hangar.obj" show_level="1 Default"/>
#        </object>
#    </objects>

#  lib/   see: Resources/default scenery/sim objects/library.txt
# objects/    = Custom Scenery/ICAO/objects
# objects/foo = Custom Scenery/ICAO/objects/foo

import sys, getopt
import xml.etree.ElementTree as ET

helptext = 'wed2stg.py -i <inputfile> -e <elevation>'

def main(argv):
    #model = "Models/Industrial/GenericStorageTank15m.ac"
    #model = "Models/Commercial/Petrolstation1.ac"
    model = "Models/Misc/generic_church_02.ac"
    elev  = 500
    heading = 0
    lon = 0
    lat = 0
    inputfile = "earth.wed.xml" 
  
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
        elif opt == "-e":
            elev = arg
    #print 'Input file is ', inputfile
    #print 'Number of arguments:', len(sys.argv), 'arguments.'
    #print 'Argument List:', str(sys.argv)

    tree = ET.parse(inputfile)
    root = tree.getroot()
    ncount = 0
    wcount = 0
 
    for child in root:
        #print child
        if child.tag == 'objects':
            for cc in child:
                
                #print cc
                if cc.attrib['class'] == "WED_ObjPlacement":
                    point=False
                    place=False
                    for ccc in cc:
                        if ccc.tag == 'point':
                            heading = ccc.attrib['heading']
                            lat = ccc.attrib['latitude']
                            lon = ccc.attrib['longitude']
                            point=True
                        if ccc.tag == "obj_placement":
                            xppath = ccc.attrib['resource']
                            model =  xppath.replace("objects/", "")
                            model = model.replace(".obj", ".xml")
                            #TODO : use .ac if .xml does not exist
                            #       use .xml if it exists
                            
                            place=True
                    if point and place:
                        print "OBJECT_SHARED", model, lon,lat, elev, heading
                        point=False
                        place=False
                        ncount+=1
       
                 
                    
if __name__ == "__main__":
    main(sys.argv[1:])
