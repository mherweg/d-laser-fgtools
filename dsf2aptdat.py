#!/usr/bin/env python
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

# work in progress 

#convert fcade polygons from dsf-txt files into taxiway polygons for apt.dat

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



import os, sys, getopt
helptext = './dsf2aptdat.py -i ICAO'

class Polygon(object):
    def __init__(self, ID, a,b,c):
        self.edges=[]
        self.ID = ID
        self.a = a
        self.b = b
        self.c = c
    def out(self):
        print(self.ID, self.a,self.b,self.c)
        for e in self.edges:
            print e
        
        
class Edge(object):
    def __init__(self,style,x1,y1,x2=None,y2=None):
        self.style=style
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
    def __str__(self):
        return "%s / %s %s %s %s" % (self.style, self.x1,self.y1,self.x2,self.y2)
        

def read_poly_def(infile):
    pd=[]
    for line in infile:
        #line = line.strip()
        #print line
        if line.startswith("POLYGON_DEF"):
            cols = line.split()
            xpath = cols[1]
            pd.append(xpath)
     
    return pd
    
def read_poly(infile):
    polys=[]
    ID=0
    for line in infile:
        if line.startswith("BEGIN_POLYGON"):
            col = line.split()
            poly=Polygon(ID,col[1],col[2],col[3])
        if line.startswith("BEGIN_WINDING"):
            green=True
        if line.startswith("POLYGON_POINT") and green:
            col = line.split()
            if len(col)==3:
                #sharp edge
                #print "sharp edge"
                edge = Edge(111,col[1],col[2])
                poly.edges.append(edge)
            if len(col)==5:
                if col[1] == col[3] and col[2] == col[4]:
                    #print "sharp edge redundant"
                    edge = Edge(111,col[1],col[2])
                else:
                    #print "true bezier edge"
                    edge = Edge(112,col[1],col[2],col[3],col[4])
                poly.edges.append(edge)
        if line.startswith("END_WINDING"):
            green=False
        if line.startswith("END_POLYGON"):
            #last edge
            edge.style =edge.style+2
            ID+=1
            #poly.out()
            polys.append(poly)
    return (polys)
        
def write_aptdat(polys):
    #print header, runways
    for p in polys:
        print "110 1 0.00 162.0000 Asphalt Taxiway from DSF"
        for e in p.edges:
            if e.style == 111:
                print "111  %s  %s"%(e.y1,e.x1)
            if e.style == 112:
                print "112  %s  %s  %s  %s"%(e.y1,e.x1,e.y2,e.x2)
            if e.style == 113:
                print "113  %s  %s"%(e.y1,e.x1)
            if e.style == 114:
                print "114  %s  %s  %s  %s"%(e.y1,e.x1,e.y2,e.x2)
    #print all the rest + 99
            

def main(argv):
    icao="foo"
    counter = 0
   
    try:
        opts, args = getopt.getopt(argv,"hi:")
    except getopt.GetoptError:
        print helptext
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helptext
            sys.exit()
        elif opt == "-i":
            icao = arg
    
    inputfilename=icao+".txt"
    try:  
        infile = open(inputfilename, 'r')
    except:
        print "input file ", inputfilename, "not found"
        sys.exit()
    pd = read_poly_def(infile)
    #print len(pd) , "polygon definitions found in ", inputfilename
    
    infile.seek(0)
    polys = read_poly(infile) 
    #for p in polys:
    #    p.out()
    
    write_aptdat(polys)
    
    
    
            

if __name__ == "__main__":
   main(sys.argv[1:])

#EOF


                





