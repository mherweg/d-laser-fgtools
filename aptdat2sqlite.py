#!/usr/bin/python
# -*- coding: utf-8 -*-

#grep ^"1 " apt.dat | wc -l

import sqlite3 as lite
import sys
import sys
import re

#msg = "blöbber"
p = re.compile('[^a-zA-Z0-9]')
#p.subn('_', msg)
  # There are two lines that describe parkings: line 15 and line 1300
pattern15 = re.compile(r"^15\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
pattern1300 = re.compile(r"^1300\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\w|]*)\s*(.*)$")
      
infile = open("apt.dat", 'r')

found = False

con = lite.connect('test.db')

with con:
    
    cur = con.cursor()    
    cur.execute("DROP TABLE IF EXISTS Airports")
    cur.execute("CREATE TABLE Airports(Id INTEGER PRIMARY KEY, Name TEXT, Icao TXT)")
    cur.execute("DROP TABLE IF EXISTS Parkings")
    cur.execute("CREATE TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TEXT, Lat TXT, Lon TXT, Heading TXT)")
      

    id = 0
    for line in infile:
            line = line.strip()
            # 1 for airports, 16 for seaports
            if line.startswith("1 "):
                #print line
                icao = line[15:19]
                name = line[20:]
                name = p.sub('_', name)

                
                #print ">" , icao , '<' , name
                
                try:
                    cur.execute("INSERT INTO Airports(Name,Icao) VALUES (?,?)", (name, icao))
                    lid = cur.lastrowid
                except lite.Error, e:
                    print "Error %s:" % e.args[0]
                    sys.exit(1)
            
            else:
                lat = -555                                                                                                                                             
                lon = -555
                heading = 0
                result = pattern15.match(line)
                # Math line 15
                if result:
                        lat = float(result.group(1))
                        lon = float(result.group(2))
                        heading = float(result.group(3))
                        pname = result.group(4).replace(' ', '_')
                # Match line 1300
                else:
                        result = pattern1300.match(line)
                        if result:
                                lat = float(result.group(1))
                                lon = float(result.group(2))
                                heading = float(result.group(3))
                                # group 4 has the type of aircraft and group 5 is services available at the parking
                                pname = result.group(6).replace(' ', '_')
                # If found, convert values
                if lat != -555:
                        if lat < 0:
                                lat2 = "S%d %f"%(int(abs(lat)), (abs(lat) - int(abs(lat)) )* 60)
                        else:
                                lat2 = "N%d %f"%(int(abs(lat)), (abs(lat) - int(abs(lat)) )* 60)
                        if lon < 0:
                                lon2 = "W%d %f"%(int(abs(lon)), (abs(lon) - int(abs(lon)) )* 60)
                        else:
                                lon2 = "E%d %f"%(int(abs(lon)), (abs(lon) - int(abs(lon)) )* 60)
                        #parkings.append((lat2, lon2, heading, name),)
                        print icao, pname, lat, lon , heading
                        cur.execute("INSERT INTO Parkings(Aid, Icao, Pname, Lat, Lon, Heading) VALUES (?,?,?,?,?,?)", (lid,icao,pname,lat2,lon2,heading))

                
    print "all data is stored in sqlite db"
                
    cur = con.cursor()    
    cur.execute("SELECT * FROM Parkings")

    rows = cur.fetchall()

    for row in rows:
        print row
        
        
        
        
