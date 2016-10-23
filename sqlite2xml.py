#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#(c) 2015 d-laser  http://wiki.flightgear.org/User:Laserman
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

# use aptdat2sqlite.py before running this program!
# mkdir Airports  
    
# This program reads airport ground networks from the sqlite DB file "groundnets.db"
# and writes Flightgear-compatible ICAO.groundnet files into the Airports folder structure,
# e.g. Airports/E/D/D/EDDF.groundnet.xml

# used together with aptdat2sqlite.py it  generates >7000 airport ground networks
# with parking locations and >900 ground networks for AI ground traffic.

# I suggest that you not overwrite the 90 ground networks that already exist in
# Flightgear
# http://wiki.flightgear.org/Airports_with_ground_networks

#grep ^"1 " apt.dat | wc -l
#
# 27486 airports
#
# find Airports -type f  | wc -l
# 7900 with parking

# running time: approx. 6 minutes

#grep -R -l "<arc" Airports | wc -l
#920
#grep -R -l Park Airports | wc -l
#7970

# january 2016
#number of airports with parking locations: 8473
#number of AI ground networks: 1140

# minus 90 blacklisted airports:
#number of airports with parking locations: 8439
#number of AI ground networks: 1139


import sqlite3 as lite
import sys
import os
import re

park_only=False




# list of 90 airports that have groundnets in FG
# that shall not be overwritten
# see:  read_blacklist(filename) and legacy-groundnets-icao.lst
blacklist= []

def read_blacklist(filename):
    try:  
        fp = open(filename, 'r')
    except:
        print "blacklist file ", filename, "not found"
        sys.exit()
    for line in fp:
        line = line.strip()
        if line.startswith("#"):
            pass
        else:
			blacklist.append(line)
        
    #print len(blacklist) , "entries in blacklist"
          


def convert_lat(lat):
    if lat < 0:
		    lat2 = "S%d %f"%(int(abs(lat)), (abs(lat) - int(abs(lat)) )* 60)
    else:
		    lat2 = "N%d %f"%(int(abs(lat)), (abs(lat) - int(abs(lat)) )* 60)
    return(lat2)
    
def convert_lon(lon):
    if lon < 0:
		    lon2 = "W%d %f"%(int(abs(lon)), (abs(lon) - int(abs(lon)) )* 60)
    else:
		    lon2 = "E%d %f"%(int(abs(lon)), (abs(lon) - int(abs(lon)) )* 60)
    return (lon2)


def find_dups(cur):
    acout=0
    #cur.execute("SELECT Aid,Pname,Lat,Lon,COUNT(*) FROM Parkings GROUP BY Lat,Lon HAVING COUNT(*) > 1")
      #TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId TXT, NewId TXT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway TXT)")
    #cur.execute("SELECT Aid,NewId,Lat,Lon,Name,COUNT(*) FROM Taxinodes GROUP BY Lat,Lon HAVING COUNT(*) > 1")
       #TABLE Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 TXT, NewId1 TXT, OldId2 TXT, NewId2 TXT, onetwo TXT, twrw TXT, Name TXT)")   
    #cur.execute("SELECT Aid,OldId1,OldId2,Name,COUNT(*) FROM Arc GROUP BY Aid,OldId1,OldId2 HAVING COUNT(*) > 1")
    #cur.execute("SELECT Aid,OldId1,OldId2,Name,COUNT(*) FROM Arc GROUP BY Aid,OldId1,OldId2 HAVING COUNT(*) > 1")
    
    
    rows = cur.fetchall()
    for row in rows:
        aid = row[0]
        cur.execute("SELECT Id,Icao FROM Airports WHERE Id=:Aid", {"Aid": aid})
        ap_rows = cur.fetchall()
        for ap in ap_rows:
            print ap[1] ,
        print row
    

#Umlaute entfernen
p = re.compile('[^a-zA-Z0-9]')

      
found = False
parking_counter=0
groundnet_counter=0



   
read_blacklist('legacy-groundnets-icao.lst')     
#main loop
con = lite.connect('groundnets.db')
with con:
    cur = con.cursor() 
    
    #find_dups(cur)
    #exit(0)
      
    #cur.execute("SELECT Id,Icao FROM Airports WHERE (Icao='HI13')")
    #cur.execute("SELECT Id,Icao FROM Airports WHERE (Icao='EKVL')")
    #cur.execute("SELECT Id,Icao FROM Airports WHERE Icao BETWEEN 'E' AND 'F' ")
    #cur.execute("SELECT Id,Icao FROM Airports WHERE Icao BETWEEN 'EDD' AND 'EDE' ")
    print "cur.execute..."
    cur.execute("SELECT Airports.Id,Airports.Icao FROM Airports  WHERE EXISTS (SELECT 1 FROM Parkings WHERE Airports.Id=Parkings.Aid)")
    print "cur.fetchall()..."
    rows = cur.fetchall()
    print "main loop..."
    for row in rows:
        #print row
        aid = row[0]
        icao = row[1]
        icao=str(icao).strip()
        #icao=icao.strip()
        #mkpath
        path="Airports"
        
<<<<<<< HEAD
        cur.execute("SELECT Pname,Lat,Lon,Heading,NewId,pushBackRoute,Type,Radius FROM Parkings WHERE Aid=:Aid", {"Aid": aid}) 
        prows = cur.fetchall()
        #print prows, type(prows)
        if prows:
            #print "parkings found"
            parking_counter+=1
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
            #print aid,path
            f = open(path, 'w')
            #write head
            f.write('<?xml version="1.0"?>\n<groundnet>\n  <version>1</version>\n')
            #f.write(' <icao="%s">\n'%(icao))
            #f.write(' <aid="%s">\n'%(aid))
            f.write('  <parkingList>\n')
            print "aid,icao:", aid, icao
            #  <Parking index="0"
            # type="cargo"
            # name="R"
            # number="02"
            # lat="N52 17.655"
            # lon="E04 44.492"
            # heading="328.8"
            # radius="43"
            # pushBackRoute="616" 
            # airlineCodes="" />
            for prow in prows:
                #print prow
                #write parkings to XML
                #TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TXT, Lat TXT, Lon TXT, Heading TXT, NewId INT, pushBackRoute TXT, Type TXT, Radius INT )")
    
                lat = convert_lat(prow[1])
                lon = convert_lon(prow[2])
                if (prow[5] != None ):
                    f.write('        <Parking index="%d" type="%s" name="%s" lat="%s" lon="%s" heading="%s"  radius="%s" pushBackRoute="%s" airlineCodes="" />\n'%(prow[4],prow[6], prow[0], lat, lon, prow[3],prow[7],prow[5]))
                else:
                    #print icao, prow[0]
                    f.write('        <Parking index="%d" type="%s" name="%s" lat="%s" lon="%s" heading="%s"  radius="%s" airlineCodes="" />\n'%(prow[4],prow[6], prow[0], lat, lon, prow[3],prow[7]))
=======
        if icao in blacklist:
            print icao ,"in blacklist - skipped"
        else:
        
            cur.execute("SELECT Pname,Lat,Lon,Heading,NewId,pushBackRoute,Type,Radius FROM Parkings WHERE Aid=:Aid", {"Aid": aid}) 
            prows = cur.fetchall()
            #print prows, type(prows)
            if prows:
                #print "parkings found"
                parking_counter+=1
                for i in range(len(icao)-1):
                    path = os.path.join(path, icao[i])
                    if os.path.exists(path):
                        pass
                        #print os.listdir(path)
                    else:
                        os.mkdir(path)
>>>>>>> d66fe7499197bcbdc8f22c6dcedd7d4a526b3555
                
                #open file for writing
                gf = '.'.join([icao, 'groundnet.xml'])
                path = os.path.join(path, gf)
                #print aid,path
                f = open(path, 'w')
                #write head
                f.write('<?xml version="1.0"?>\n<groundnet>\n  <version>1</version>\n')
                #f.write(' <icao="%s">\n'%(icao))
                #f.write(' <aid="%s">\n'%(aid))
                f.write('  <parkingList>\n')
                print "aid,icao:", aid, icao
                #  <Parking index="0"
                # type="cargo"
                # name="R"
                # number="02"
                # lat="N52 17.655"
                # lon="E04 44.492"
                # heading="328.8"
                # radius="43"
                # pushBackRoute="616" 
                # airlineCodes="" />
                for prow in prows:
                    #print prow
                    #write parkings to XML
                    #TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TXT, Lat TXT, Lon TXT, Heading TXT, NewId INT, pushBackRoute TXT, Type TXT, Radius INT )")
        
                    lat = convert_lat(prow[1])
                    lon = convert_lon(prow[2])
                    if (prow[5] != None ):
                        f.write('        <Parking index="%d" type="%s" name="%s" lat="%s" lon="%s" heading="%s"  radius="%s" pushBackRoute="%s" airlineCodes="" />\n'%(prow[4],prow[6], prow[0], lat, lon, prow[3],prow[7],prow[5]))
                    else:
                        #print icao, prow[0]
                        f.write('        <Parking index="%d" type="%s" name="%s" lat="%s" lon="%s" heading="%s"  radius="%s" airlineCodes="" />\n'%(prow[4],prow[6], prow[0], lat, lon, prow[3],prow[7]))
                    
                #write foot
                f.write(" </parkingList>\n")
                
<<<<<<< HEAD
                cur.execute('SELECT NewId1,NewId2,onetwo,Name,isPushBackRoute FROM Arc WHERE Aid=:Aid AND twrw NOT LIKE "runway"', {"Aid": aid}) 
                arcs = cur.fetchall()
                if arcs:
                    f.write(' <TaxiWaySegments>\n')
                    for a in arcs:
                        print (a[0],a[1],a[4],a[3] )
                        f.write('        <arc begin="%s" end="%s" isPushBackRoute="%s" name="%s"  />\n'%(a[0],a[1],a[4],a[3]  ))
                        if a[2]=="twoway":
                            f.write('        <arc begin="%s" end="%s" isPushBackRoute="%s" name="%s"  />\n'%(a[1],a[0],a[4],a[3]  ))
=======
                #write nodes
                #TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId TXT, NewId TXT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway TXT)")
                if not park_only:
                    cur.execute("SELECT Lat,Lon,NewId,isOnRunway,holdPointType FROM TaxiNodes WHERE Aid=:Aid", {"Aid": aid}) 
                    nodes = cur.fetchall()
                    if nodes:
                        groundnet_counter+=1
                        f.write(' <TaxiNodes>\n')
                        for n in nodes:
                            #TODO  holdPointType
                            lat = convert_lat(n[0])
                            lon = convert_lon(n[1])
                            #<node index="632" lat="N52 17.840" lon="E04 45.904" isOnRunway="0" holdPointType="PushBack" />
                            #<node index="633" lat="N52 17.491" lon="E04 46.832" isOnRunway="0" holdPointType="none" />
                            f.write('        <node index="%d" lat="%s" lon="%s" isOnRunway="%s" holdPointType="%s"  />\n'%(n[2], lat, lon, n[3],n[4] ))
>>>>>>> d66fe7499197bcbdc8f22c6dcedd7d4a526b3555
                            
                        
                        f.write(' </TaxiNodes>\n')
                    
                    # write arc
                    # but only taxiways, not runways       WHERE Aid=:Aid AND twrw LIKE "taxiway"
                    #TABLE Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 TXT, NewId1 TXT, OldId2 TXT, NewId2 TXT, onetwo TXT, twrw TXT, Name TXT)")        
                    # <arc begin="26" end="329" isPushBackRoute="0" name="Route" />
                    
                    cur.execute('SELECT NewId1,NewId2,onetwo,Name,isPushBackRoute FROM Arc WHERE Aid=:Aid AND twrw NOT LIKE "runway"', {"Aid": aid}) 
                    arcs = cur.fetchall()
                    if arcs:
                        f.write(' <TaxiWaySegments>\n')
                        for a in arcs:
                            print (a[0],a[1],a[4],a[3] )
                            f.write('        <arc begin="%s" end="%s" isPushBackRoute="%s" name="%s"  />\n'%(a[0],a[1],a[4],a[3]  ))
                            if a[2]=="twoway":
                                f.write('        <arc begin="%s" end="%s" isPushBackRoute="%s" name="%s"  />\n'%(a[1],a[0],a[4],a[3]  ))
                                
                        
                        f.write(' </TaxiWaySegments>\n')
                    else:
                        print len(prows), "parking locations but no taxi network:" , icao
                f.write("</groundnet>\n")
                #close file
                f.close()
            else:
                pass
                #print ".",

print "number of airports with parking locations:", parking_counter            
print "number of AI ground networks:", groundnet_counter
        
        
        
        
        
        
