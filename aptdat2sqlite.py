#!/usr/bin/python
# -*- coding: utf-8 -*-

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

#TODO: service -> radius
#      type -> type
# speedup by using more int and less TXT ?


#grep ^"1 " apt.dat | wc -l

import sqlite3 as lite
import sys, numpy
import re

#msg = "blöbber"
p = re.compile('[^a-zA-Z0-9]')
#p.subn('_', msg)
  # There are two lines that describe parkings: line 15 and line 1300
pattern15 = re.compile(r"^15\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
pattern1300 = re.compile(r"^1300\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\w|]*)\s*(.*)$")
      
infile = open("apt.dat.18.9.2015", 'r')

found = False


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
    
def calculate_distance(x1,y1,x2,y2):    
    a = numpy.array((x1 ,y1))
    b = numpy.array((x2, y2))
    dist = numpy.linalg.norm(a-b)
    return dist
    
def dumpall():
    # show content of all tables            
    cur = con.cursor()    
    cur.execute("SELECT * FROM Parkings")
    
    rows = cur.fetchall()
    for row in rows:
        print row
    print "------------nodes----------------------------"    
    cur.execute("SELECT * FROM Taxinodes")
    rows = cur.fetchall()
    for row in rows:
        print row

    print "------------arc----------------------------"    
    cur.execute("SELECT * FROM Arc")
    rows = cur.fetchall()
    for row in rows:
        print row
        
def connect_parkings(lid):   
    # connect  the parking spots to their nearest node
    # and add this node als pushback route for that spot
    cur = con.cursor()    
    cur.execute("SELECT * FROM Parkings WHERE Aid = ? ",(lid,))
    parkings = cur.fetchall()
    cur.execute("SELECT * FROM Taxinodes WHERE Aid = ? ",(lid,))
    nodes =  cur.fetchall()
    #Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TEXT, Lat TXT, Lon TXT, Heading TXT, NewId TXT)")
    #Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId TXT, NewId TXT, Lat TXT, Lon TXT, Type TXT, Name TXT)")
    countp =0
    for p in parkings:
        #print "connect_parkings: airportId", p[1]
        mindist=1.0
        bestnode=-1
        countp+=1
        for n in nodes:
            
            dist = calculate_distance(p[4],p[5], n[4],n[5])
            if dist < mindist:
                mindist=dist
                #print "new mindist" , dist
                bestnode = n
            #print p , bestnode
        if bestnode != -1:
            cur.execute("INSERT INTO Arc(Aid, OldId1, NewId1, OldId2, NewId2, onetwo, twrw, name,isPushbackRoute) VALUES (?,?,?,?,?,?,?,?,?)", (lid,"",p[7],"",bestnode[3],"twoway","taxiway", p[3],1))
            #print "parking primary key ",  bestnode[3], p[0]
            cur.execute("UPDATE Parkings SET pushBackRoute = ? WHERE NewId = ? AND Aid = ?;",(bestnode[3], p[7], lid ))
            cur.execute('UPDATE Taxinodes SET holdPointType = "PushBack" WHERE NewID = ? AND Aid = ?',(bestnode[3],lid))
        #else:
            #print "WARNING: no Taxinode found for ", p
    if countp > 0:
        print "Parking spots:", countp
            

def set_isOnRunway(lid):
 # convert edge "runway"   to node isOnRunway (and then remove them?)
    #Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 TXT, NewId1 TXT, OldId2 TXT, NewId2 TXT, onetwo TXT, twrw TXT, Name TXT)")
    cur.execute('SELECT * FROM Arc WHERE twrw LIKE "runway" AND Aid = ? ',(lid,))
    arcs =  cur.fetchall()    
    for a in arcs:
        print "on runway:" , a[3], a[5]
        cur.execute('UPDATE Taxinodes SET isOnRunway = "1" WHERE NewId = ? AND Aid = ?;',(a[3],lid))
        cur.execute('UPDATE Taxinodes SET isOnRunway = "1" WHERE NewId = ? AND Aid = ?;',(a[5],lid))
        # do not use runways for taxiing
        #cur.execute('DELETE FROM Arc WHERE twrw LIKE "runway" ')
        




# main apt.dat parsing loop
con = lite.connect('groundnets.db')
print "DB connected, ",
with con:
    
    cur = con.cursor()    
    cur.execute("DROP TABLE IF EXISTS Airports")
    cur.execute("CREATE TABLE Airports(Id INTEGER PRIMARY KEY, Name TEXT, Icao TXT)")
    cur.execute("DROP TABLE IF EXISTS Parkings")
    cur.execute("DROP TABLE IF EXISTS Taxinodes")
    cur.execute("DROP TABLE IF EXISTS Arc")
    cur.execute("CREATE TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TEXT, Lat TXT, Lon TXT, Heading TXT, NewId TXT, pushBackRoute TXT)")
    cur.execute("CREATE TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId TXT, NewId TXT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway TXT, holdPointType TXT)")
    cur.execute("CREATE TABLE Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 TXT, NewId1 TXT, OldId2 TXT, NewId2 TXT, onetwo TXT, twrw TXT, Name TXT,isPushBackRoute TXT)")
    print "tables created."    

    id = 0
    lid = -1
    for line in infile:
            line = line.strip()
            # 1 for airports, 16 for seaports
            if line.startswith("1 ") or line.startswith("16 ") or line.startswith("17 "):
                
                
                #process the previous airport
                if lid >= 0 :
                    connect_parkings(lid)
                    set_isOnRunway(lid)
              
                apt_header = line.split()
                icao = apt_header[4]
                name = ' '.join(apt_header[5:])
                name = p.sub('_', name)
                print ">" , icao , '<' , name ,
                
                try:
                    cur.execute("INSERT INTO Airports(Name,Icao) VALUES (?,?)", (name, icao))
                    lid = cur.lastrowid
                    print "lid:" , lid
                except lite.Error, e:
                    print "Error %s:" % e.args[0]
                    sys.exit(1)
                offset=0
            else:
                lat = -555                                                                                                                                             
                lon = -555
                heading = 0
                result = pattern15.match(line)
                # Match line 15
                if result:
                        lat = float(result.group(1))
                        lon = float(result.group(2))
                        heading = float(result.group(3))
                        pname = result.group(4).replace(' ', '_')
                        newid = offset
                        cur.execute("INSERT INTO Parkings(Aid, Icao, Pname, Lat, Lon, Heading, NewId) VALUES (?,?,?,?,?,?,?)", (lid,icao,pname,lat,lon,heading,newid))
                        offset=offset+1

                # Match line 1300
                result = pattern1300.match(line)
                if result:
                        lat = result.group(1)
                        lon = result.group(2)
                        heading = float(result.group(3))
                        # group 4 has the type of aircraft and group 5 is services available at the parking
                        # type: misc, tie-down, gate, hangar
                        #print "type:", result.group(4),
                        #service        -> radius
                        #heavy 
                        #jets
                        #turboprops
                        #props
                        #helos
                        #print "services:", result.group(5)
                        pname = result.group(6).replace(' ', '_')
                        #print icao, pname, lat, lon , heading
                        newid = offset
                        
                        cur.execute("INSERT INTO Parkings(Aid, Icao, Pname, Lat, Lon, Heading, NewId) VALUES (?,?,?,?,?,?,?)", (lid,icao,pname,lat,lon,heading,newid))
                        offset=offset+1
                        
                #print "offset", offset
                 # taxinode
                #                                      1              2            3      4       5   
                # 1201 = taxi node                   lat            lon          type    id       name
                pattern1201 = re.compile(r"^1201\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\-0-9\.]*)\s*(.*)$")
                result = pattern1201.match(line)
                if result:
                    #print result.group(1), result.group(2),  result.group(3) ,result.group(4), result.group(5)
                    lat = result.group(1)
                    lon = result.group(2)
                    nodetype = result.group(3)
                    nodeid = result.group(4)
                    newid = int(nodeid)+offset
                    #print nodeid , newid
                    nodename = result.group(5).replace(' ', '_')
                    
                    cur.execute("INSERT INTO Taxinodes(Aid, OldId, NewId, Lat, Lon, Type, Name,isOnRunway,holdPointType) VALUES (?,?,?,?,?,?,?,?,?)", (lid,nodeid,newid,lat,lon,nodetype, nodename,"0","none"))

        # TaxiWaySegments
                #1202 taxi edge   node-id1  node-id2 “twoway” or “oneway”  “taxiway” or “runway”  name
                #                                      1              2            3      4       5   
                # 1202 = taxi edge                    node         node        1/2way    tw/rw    name
                pattern1202 = re.compile(r"^1202\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*(\w*)\s*(.*)$")
                result = pattern1202.match(line)
                if result:
                    #print "TAXI EDGE"
                    #print result.group(1), result.group(2),  result.group(3) ,result.group(4), result.group(5)
                    n1 = result.group(1)
                    newid1 = int(n1)+offset
                    n2 = result.group(2)
                    newid2 = int(n2)+offset
                    onetwo = result.group(3)
                    twrw = result.group(4)
                    #print "TWRW", twrw
                    name = result.group(5)
                    #"CREATE TABLE Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId TXT, NewId TXT, n1 TXT, n2 TXT, onetwo TXT, twrw TXT)")
                    cur.execute("INSERT INTO Arc(Aid, OldId1, NewId1, OldId2, NewId2, onetwo, twrw, name,isPushBackRoute) VALUES (?,?,?,?,?,?,?,?,?)", (lid,n1,newid1,n2,newid2,onetwo,twrw, name, "0"))


    #process the last airport
    connect_parkings(lid)
    set_isOnRunway(lid)
              
    print "all data is stored in sqlite db"
         
   
        
        
    

        
        
