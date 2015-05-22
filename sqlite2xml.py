#!/usr/bin/python
# -*- coding: utf-8 -*-

#grep ^"1 " apt.dat | wc -l
#
# 27486 airports
#
# find Airports -type f  | wc -l
# 6412 with parking



import sqlite3 as lite
import sys
import os
import re

#Umlaute entfernen
p = re.compile('[^a-zA-Z0-9]')

# There are two lines that describe parkings: line 15 and line 1300
pattern15 = re.compile(r"^15\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
pattern1300 = re.compile(r"^1300\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\w|]*)\s*(.*)$")
      
infile = open("apt.dat", 'r')

found = False

con = lite.connect('test.db')

with con:
    
    cur = con.cursor()   
    #cur.execute("SELECT Id,Icao FROM Airports WHERE (Icao='HI13')")
    #cur.execute("SELECT Id,Icao FROM Airports WHERE (Icao='EKVL')")    
    cur.execute("SELECT Id,Icao FROM Airports")
    rows = cur.fetchall()
    for row in rows:
        #print row
        aid = row[0]
        icao = row[1]
        icao=str(icao).strip()
        #icao=icao.strip()
        #mkpath
        path="Airports"
        
        cur.execute("SELECT Pname,Lat,Lon,Heading FROM Parkings WHERE Aid=:Aid", {"Aid": aid}) 
        prows = cur.fetchall()
        #print prows, type(prows)
        if prows:
            #print "parkings found"
       
            for i in range(len(icao)-1):
                path = os.path.join(path, icao[i])
                if os.path.exists(path):
                    pass
                    #print os.listdir(path)
                else:
                    os.mkdir(path)
            
            #open file for writing
            gf = '.'.join([icao, 'groundnet.xml'])
            path = os.path.join(path, gf)
            print path
            f = open(path, 'w')
            #write head
            f.write('<?xml version="1.0"?>\n<groundnet>\n    <parkingList>\n')
            
            #cur.execute("SELECT Pname,Lat,Lon,Heading FROM Parkings WHERE Aid=:Aid", {"Aid": aid}) 
            #prows = cur.fetchall() 
            i=0
            for prow in prows:
                #print prow
                #write parkings to XML
                f.write('        <Parking index="%d" type="gate" name="%s" lat="%s" lon="%s" heading="%s" />\n'%(i, prow[0], prow[1][:12], prow[2][:12], prow[3]))
                i=i+1
            #write foot
            f.write("    </parkingList>\n</groundnet>\n")
            #close file
            f.close()
        
        
        
        
        
        
