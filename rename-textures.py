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

# rename (PNG-)texture-filenames inside an .ac file 
# and also creates .png files with the new names
# the result will be in the output folder

# this script was not tested on any other OS than Linux
# non-png textures like .rgb .dds  will be ignored.

import sys, getopt, re
import fileinput, subprocess

helptext = 'rename-textures.py -i <inputfile> '

def read_ac(ac_file):
    
    l = []  # list of old png filenames
    n = []  # list of new png filenames, only used for debug output
    subprocess.call(["mkdir", "output"])
    
    with open(ac_file,"r") as fp:     # collect all old png-filenames, avoiding duplicates
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
                    if index == 0:
                        newname = ac_file.rstrip('.ac') + ".png"
                    else:
                        newname = ac_file.rstrip('.ac') + "_" + str(index) + ".png"
                    
                    extension = texname[-4:]
                    if extension in [".png" ,".PNG"]:
                        l.append(texname)  
                        #print texname , newname
                        # I use cp and not ml because many models might use the same texture file
                        newpath = "output/" + newname
                        subprocess.call(["cp", texname, newpath])  #rename the png file on the harddisk
                        # todo: call convert to scale to a factor of 2
                        n.append(newname)
                        index = index +1
                    else:
                        print "ERROR: not a png:" , texname 
                        #exit(1)
                        
    for i in range(0, len(n)):            
        print l[i],"-> output/"+ n[i] 
                  
    index = 0
    # modify the .ac file inplace, write the original version to NAME.ac.bak
    # no "print" for debugging allowed in this loop
    # because stdout is written to the .ac
    for line in fileinput.input(files=(ac_file),inplace=1, backup='.bak'):
        col = line.find("texture")
        if col == 0:  # a texture line is found
            texname = line[8:].rstrip('"\r\n')
            texname = texname.lstrip('"')
            index = 0
            for name in l:
                if name == texname:
                    if index == 0:
                        newname = ac_file.rstrip('.ac') + ".png"
                    else:
                        newname = ac_file.rstrip('.ac') + "_" + str(index) + ".png"
                    if (name != newname):
                        #debug = texname, name, newname + "\n"
                        #print (debug)    
                        line = re.sub(name,newname, line)  # replace the filename in the .ac file
                index = index +1
        sys.stdout.write(line)
    
    subprocess.call(["cp", ac_file, "output"])
     
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
