#!/usr/bin/python

# rename-textures.py  
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

# rename texture filenames inside an .ac file 
# and also renames the .png files

# this script was not tested on any other OS than Linux


import sys, getopt, re
import fileinput, subprocess

helptext = 'remane-textures.py -i <inputfile> '



def read_ac(ac_file):
    
    l = []
    n = []
    with open(ac_file,"r") as fp:
        index = 0
        for line in fp:
            #print line
            col = line.find("texture")
            if col == 0:
                #print "FOUND", line[8:]
                texname = line[8:].rstrip('"\r\n')
                texname = texname.lstrip('"')
                if texname in l:
                    pass
                else:
                    l.append(texname)
                    if index == 0:
                        newname = ac_file.rstrip('.ac') + ".png"
                    else:
                        newname = ac_file.rstrip('.ac') + "_" + str(index) + ".png"
                    #subprocess.call(["cp", texname, newname])
                    subprocess.call(["mv", texname, newname])
                    n.append(newname)
                    index = index +1
                    
    print "old:",l 
    print "new:",n               
    index = 0
    for line in fileinput.input(files=(ac_file),inplace=1, backup='.bak'):
        col = line.find("texture")
        if col == 0:
            index = 0
            for name in l:
                if index == 0:
                    newname = ac_file.rstrip('.ac') + ".png"
                else:
                    newname = ac_file.rstrip('.ac') + "_" + str(index) + ".png"
                if (name != newname):    
                    line = re.sub(name,newname, line)

                index = index +1
        sys.stdout.write(line)
     
                
                
                
  
   

def main(argv):
    model = ""
    ac_file = "terminal-A-B.ac"
  
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
            ac_file = arg
      
    print 'Input file is ', ac_file
    #print 'Number of arguments:', len(sys.argv), 'arguments.'
    #print 'Argument List:', str(sys.argv)
    read_ac(ac_file)
    
    
    


                 
                    
if __name__ == "__main__":
    main(sys.argv[1:])
