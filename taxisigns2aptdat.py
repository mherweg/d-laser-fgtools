#!/usr/bin/python

# taxisigns2aptdat.py  
#read taxisigns from a .stg file and insert them
#into apt.dat so they can be edited and merged with WED (World Editor)

# http://wiki.flightgear.org/Signs
# http://wiki.flightgear.org/File_Formats#OBJECT_SIGN_lines
# http://developer.x-plane.com/tools/worldeditor/
# http://data.x-plane.com/file_specs/XP%20APT1000%20Spec.pdf


#
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

# output is written to output.dat
# after running the script
# import output.dat with WED 
# and check the additional taxi signs

import sys, getopt
helptext = 'taxisigns2aptdat.py -s <input .stg file> -a <input apt.dat file>'

def main(argv):
   
    heading = 0
    lon = 0
    lat = 0
    inputfile = "input.stg"
    aptfile = "apt.dat" 
  
    try:
        opts, args = getopt.getopt(argv,"hs:a:")
    except getopt.GetoptError:
        print helptext
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helptext
            sys.exit()
        elif opt == "-s":
            inputfile = arg
        elif opt == "-a":
            aptfile = arg
    #print 'Input file is ', inputfile
    #print 'Number of arguments:', len(sys.argv), 'arguments.'
    #print 'Argument List:', str(sys.argv)


    out = open("output.dat", 'w')
    with open(aptfile, 'r') as aptin:
        for line in aptin:
            if line[:2] == "99":
                pass
            else:
                out.write(line)
            
        with open(inputfile,"r") as fp:     # collect all old png-filenames, avoiding duplicates
            index = 0
            for line in fp:
                #print line, line[:3]
                if line[:11] == "OBJECT_SIGN":
                    #  ['OBJECT_SIGN', '{@Y}S{^r}', '8.526561', '50.022227', '103.9', '352.00', '1']
                    #print "found:",line.split()
                    col = line.split()
                    text = col[1]
                    lon = col[2]
                    lat = col[3]
                    # heading correct ?
                    heading = 360 - float( col[5] )
                    if text[:4] == "{@B}":
                        size = "5"
                    else:
                        size = "2"
                    #print lat, lon, heading, text
                    #type = 0  #Reserved for future use. Ignore.
                    #size 1=small 2=medium 3=large
                    #     4=  Large distance-remaining sign on runway edge
                    #     5=small distance-remaining sign on runway edge
                  
                    #example:
                    #20  50.03633307  008.54686715 159.0900 0 3 {@Y}{^l}3012M
                    #print("bla %11.8f  %11.8f  %8.4  0 %d %s" % ( float(lat), float(lon), float(heading),size,"foo" ))
                    #print "20 ", lat,lon,heading,0,size,text
                    signline = "20  "+lat+"  "+lon+"  "+str(heading)+"  0  "+size+"  "+text+"\n"
                    #print signline
                    out.write(signline)
                    index+=1
                    
        out.write("99")
        out.close()
        print "wrote",aptfile,"plus",index, "taxisigns to output.dat"
        print "now import output.dat with WED(World Editor)"            
        
           
                 
                    
if __name__ == "__main__":
    main(sys.argv[1:])
