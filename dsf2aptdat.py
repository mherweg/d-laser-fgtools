#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Martin Herweg    m.herweg@gmx.de
# Copyright (C) 2020 Benedikt Wolf (D-ECHO)
# Copyright (C) 2020 Israel Hernandez (IAHM-COL)
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

# work in progress 

#convert facade polygons from dsf-txt files into taxiway polygons for apt.dat
# and
# into OSM XML to be read by osm2city

#INPUT dsf/txt:

#rectangle example:

#POLYGON_DEF lib/airport/Common_Elements/Fence_Facades/Fenced_Parking.fac
#BEGIN_POLYGON 0 10 2
#BEGIN_WINDING
#POLYGON_POINT 14.254323548 50.109449149
#POLYGON_POINT 14.254458019 50.109444381
#POLYGON_POINT 14.254452773 50.109646086
#POLYGON_POINT 14.254321641 50.109646563
#END_WINDING
#END_POLYGON

# bezier example, 4 "corners"
#BEGIN_POLYGON 1 10 4
#BEGIN_WINDING
#POLYGON_POINT 14.254323548 50.109449149 14.254323548 50.109449149  <- x1=x2 y1=y2  ... sharp corner 
#POLYGON_POINT 14.254458019 50.109444381 14.254458019 50.109444381
#POLYGON_POINT 14.254449435 50.109617475 14.254447051 50.109658007  <  x1 != x2  y1 != y2 ... rounded
#POLYGON_POINT 14.254321641 50.109646563 14.254321641 50.109646563
#END_WINDING
#END_POLYGON


#OUTPUT  apt.dat:
#=================
#rectangle asphalt:
#110 1 0.00 162.0000 New Taxiway 4
#111  50.10966649  014.25446889
#111  50.10966566  014.25455490
#111  50.10969759  014.25455555
#113  50.10969801  014.25446825

#bezier asphalt      162=texture heading    0.00 roughness
#110 1 0.00 162.0000 New Taxiway 5
#111  50.10965280  014.25447148
#111  50.10965114  014.25453938
#112  50.10969054  014.25453615  50.10971584  014.25451157
#113  50.10969179  014.25446825

#bezier 2=concrete    22=line & light attributes
#110 2 0.12 99.0000 New Taxiway 5
#111  50.10964136  014.25448294 22
#111  50.10964155  014.25454792 22
#112  50.10968462  014.25453213  50.10970992  014.25450756 22
#113  50.10968998  014.25447146 22

import os, sys, getopt, fileinput, subprocess
helptext = './dsf2aptdat.py -i ICAO'

nodeid=0
minx=False
maxx=False
miny=False
maxy=False

class Polygon(object):
    def __init__(self, ID, a,b,c,text):
        self.verts=[]
        self.ID = ID
        self.a = a
        self.b = b
        self.c = c
        self.text = text
    def out(self):
        print(self.ID, self.a,self.b,self.c)
        for e in self.verts:
            print (e)
        
class Vert(object):
    def __init__(self,style,x1,y1,x2=None,y2=None):
        global nodeid, minx, miny, maxx, maxy
        self.style=style
        self.x1=x1
        self.y1=y1
        # needs float type
        #if nodeid==0:
            #minx=x1
            #maxx=x1
            #miny=y1
            #maxy=y1
        
        #if x1<minx:
            #minx=x1
        #if x1>maxx:
            #maxx=x1
       
        #if y1<miny:
            #miny=y1
        #if y1>maxy:
            #maxy=y1
        self.x2=x2
        self.y2=y2
        self.nodeid=nodeid
        nodeid+=1
    def __str__(self):
        return "%d %s / %s %s %s %s " % (self.nodeid, self.style, self.x1,self.y1,self.x2,self.y2)

def read_poly_def(infile):
    pd=[]
    for line in infile:
        #line = line.strip()
        #print (line)
        if line.startswith("POLYGON_DEF"):
            cols = line.split()
            xpath = cols[1]
            pd.append(xpath)
     
    return pd
    
def read_poly(infile,pd):
    polys=[]
    ID=0
    for line in infile:
        if line.startswith("BEGIN_POLYGON"):
            col = line.split()
            text = pd[int(col[1])]
            poly=Polygon(ID,col[1],col[2],col[3],text)
            text = pd[int(poly.a)]
        if line.startswith("BEGIN_WINDING"):
            green=True
            cache1=-1
            cache2=-1
        if line.startswith("POLYGON_POINT") and green:
            col = line.split()
            if(cache1==-1):
                cache1=col[1]
                cache2=col[2]
            if len(col)==3 or len(col)==4:
                #print ("sharp corner")
                vert = Vert(111,col[1],col[2])
                poly.verts.append(vert)
            if len(col)==5:
                if col[1] == col[3] and col[2] == col[4]:
                    #print ("sharp corner redundant")
                    vert = Vert(111,col[1],col[2])
                else:
                    #print ("true bezier rounded corner")
                    vert = Vert(112,col[1],col[2],col[3],col[4])
                poly.verts.append(vert)
        if line.startswith("END_WINDING"):
            green=False
            x=len(poly.verts)-1
            if x>=1:
                if cache1==poly.verts[x].x1 and cache2==poly.verts[x].y1:
                     poly.verts.pop(x)
                     cache1=-1
                     cache2=-1
                     x=x-1
                poly.verts[x].style=poly.verts[x].style+2
        if line.startswith("END_POLYGON"):
            #last vert
            #  vert.style =vert.style+2
            #  ID+=1
            
            # whitelist: Garage, hangar, modern, Warehouse, Terminal , Office...
            # 
            whitelist=['Building','modern','urban', 'Garage','Hangars','pavement','Fenced_Parking','line']
            if any(x in text for x in whitelist):
            #if text.find("Building") >=0 or text.find("pavement") >=0 or text.find("Fenced_Parking") >=0:
                #print (text)
                #poly.out()
                polys.append(poly)
            #else:
                #print ("ignoring: " + text)
           
    return (polys)
        
def write_aptdat(polys,icao):
    """
    modify the ICAO.dat file inplace, write the original version to NAME.dat.bak
    no "print" for debugging allowed in this loop
    because stdout is written to the ICAO.dat
    """
    #print (header +  runways)
    count = 0
    pcount = 0
    datfilename = icao + ".dat"
    for line in fileinput.input(files=(datfilename),inplace=1, backup='.bak'):
        #sys.stderr.write(".")
        if line.startswith("100 "):
            #runway found
            sys.stdout.write(line)
            #sys.stderr.write(line)
            #insert my stuff
            for p in polys:
                if p.text.find("Building") >=0:
                    surface_type = "2"  #concrete,  gravel=5 did not work
                else:
                    surface_type = "1"  # asphalt   
                t=""
                if p.text.find("lib/airport/lines/") >=0:
                    l = "120  Line from DSF %s \r\n"%(p.text)
                    s=p.text.split("/")
                    s2=s[3].split("_")
                    t=s2[0]
                else:
                    l = "110  %s 0.00 0.0000 Polygon from DSF %s \r\n"%(surface_type, p.text)
                sys.stdout.write(l)
                pcount+=1
                for e in p.verts:
                    if e.style == 111:
                        l= "111  %s  %s %s\r\n"%(e.y1,e.x1,t)
                        sys.stdout.write(l)
                        #sys.stderr.write("111")
                        count+=1
                    if e.style == 112:
                        l= "112  %s  %s  %s  %s %s\r\n"%(e.y1,e.x1,e.y2,e.x2,t)
                        sys.stdout.write(l)
                        #sys.stderr.write("112")
                        count+=1
                    if e.style == 113:
                        l= "113  %s  %s\r\n"%(e.y1,e.x1)
                        sys.stdout.write(l)
                        #sys.stderr.write(l)
                        count+=1
                    if e.style == 114:
                        l= "114  %s  %s  %s  %s %s\r\n"%(e.y1,e.x1,e.y2,e.x2,t)
                        sys.stdout.write(l)
                        #sys.stderr.write(l)
                        count+=1
                    
        else:
            sys.stdout.write(line)
    return (count,pcount)

#example osm xml:
#-------------------
#<?xml version="1.0" encoding="UTF-8"?>
#<osm version="0.6" generator="CGImap 0.4.0 (8656 thorn-02.openstreetmap.org)" copyright="OpenStreetMap and contributors" attribution="http://www.openstreetmap.org/copyright" license="http://opendatacommons.org/licenses/odbl/1-0/">
# <bounds minlat="51.6634500" minlon="7.1888500" maxlat="51.6642800" maxlon="7.1904000"/>
#
#<node id="1096059121" visible="true" version="1" changeset="6923824" timestamp="2011-01-10T08:17:52Z" user="Frank Dengel" uid="66871" lat="51.6635189" lon="7.1893369"/>
#<way id="94334472" visible="true" version="1" changeset="6923824" timestamp="2011-01-10T08:17:58Z" user="Frank Dengel" uid="66871">
#  <nd ref="1096059064"/>
#  <nd ref="1096059024"/>
#  <nd ref="1096059117"/>
#  <nd ref="1096059078"/>
#  <nd ref="1096059064"/>
#  <tag k="building" v="yes"/>
# </way>
#</osm>
def write_osmxml(polys,icao):
    
    bcount=0
    osmfile = open(icao+'.osm', 'w')
 
    osmfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    osmfile.write('<osm version="0.6" generator="dsf2aptdat.py" copyright="scenery gateway contributors">\n')
    # do we need bounds ?
    #osmfile.write '<bounnds minlat="%d" minlon="%d" maxlat="%d51.6642800" maxlon="%d"/>>'
    
    whitelist=['Building','modern','Garage','Hangars','urban']
    for p in polys:  #all nodes for all buildings
        if any(x in p.text for x in whitelist):
            for v in p.verts:
                line='<node id="%d" visible="true" version="1"   lat="%s" lon="%s"/>\n'%(v.nodeid, v.y1, v.x1)
                osmfile.write(line)
    for p in polys:  #one way for each building
        if any(x in p.text for x in whitelist):
            #print (str(p.verts))
            bcount+=1
            line='<way id="%d" visible="true" version="1" >\n'%(p.ID)
            osmfile.write(line)
            first=True
            for v in p.verts:
                line='<nd ref="%d"/>\n'%(v.nodeid,)
                osmfile.write(line)
                if first:
                    lastline=line
                    first=False
                    
            #line='<nd ref="%d"/>\n'%(p.verts[0].nodeid,)   # close the loop: last node = first node
            osmfile.write(lastline)
            line='<tag k="building" v="yes"/>\n'
            osmfile.write(line)
            line='<tag k="building:height" v="%s"/>\n'%(p.b,)
            osmfile.write(line)
            line='<tag k="facade_file_name" v="%s"/>\n'%(p.text,)
            osmfile.write(line)
            osmfile.write("</way>\n")
    osmfile.write("</osm>\n")
    osmfile.close()
    print ("wrote %d buildings to %s.osm"%(bcount,icao))


def main(argv):
    icao="KMIA"
    counter = 0
   
    try:
        opts, args = getopt.getopt(argv,"hi:")
    except getopt.GetoptError:
        print (helptext)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print (helptext)
            sys.exit()
        elif opt == "-i":
            icao = arg
    
    inputfilename=icao+".txt"
    try:  
        infile = open(inputfilename, 'r')
    except:
        print ("input file " +  inputfilename + " not found")
        sys.exit()
    print ("reading...")
    pd = read_poly_def(infile)
    print (str(len(pd)) + " polygon type definitions found in " + inputfilename)
    
    infile.seek(0)
    polys = read_poly(infile,pd) 
    #print (len(polys) + "polygons in %s.txt"%(icao)) @  <-strange result ?
    print ("inserting into " + icao + ".dat  (please do this only once per file)")
    count, pcount = write_aptdat(polys,icao)
    #print
    print ("inserted %d polygons and %d nodes into %s.dat"%(pcount,count,icao))
    write_osmxml(polys,icao)
    print ("done.")

if __name__ == "__main__":
   main(sys.argv[1:])

#EOF
