#!/usr/bin/python
# -*- coding: utf-8 -*-

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

#this script runs 15 minutes on a 
#Intel Core2 Duo CPU     P8600  @ 2.40GHz

# you can strip apd.dat before running this tool:
#time egrep '^1 |^16 |^17 |^100 |^101 |^102 |^14 |^15 |^1300 |^1201 |^1202 ' apt.dat.18.9.2015 > apt.stripped
#real	0m1.863s
#... but you win only 20 seconds ;-)

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
pattern1201 = re.compile(r"^1201\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\-0-9\.]*)\s*(.*)$")
pattern1202 = re.compile(r"^1202\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*(\w*)\s*(.*)$")

infile = open("apt.dat", 'r')
#infile = open("problematic.dat", 'r')

found = False


    
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
    #TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TXT, Lat TXT, Lon TXT, Heading TXT, NewId INT, pushBackRoute TXT, Type TXT, Radius INT )")
    #TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId INT, NewId INT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway INT, holdPointType TXT)")
    #TABLE Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 INT, NewId1 INT, OldId2 INT, NewId2 INT, onetwo TXT, twrw TXT, Name TXT,isPushBackRoute INT)")
  
    cur = con.cursor()    
    cur.execute("SELECT NewId,Lat,Lon,Pname,pushBackRoute FROM Parkings WHERE Aid = ? ",(lid,))
    parkings = cur.fetchall()
    cur.execute("SELECT NewId,Lat,Lon FROM Taxinodes WHERE Aid = ? ",(lid,))
    nodes =  cur.fetchall()
    countp =0
    for p in parkings:
        #print "connect_parkings: airportId", p[1]
        mindist=1.0
        bestnode_id=-1
        countp+=1
        for n in nodes:
            
            dist = calculate_distance(p[1],p[2], n[1],n[2])
            if dist < mindist:
                mindist=dist
                #print "new mindist" , dist
                bestnode_id = n[0]
            #print p , bestnode
        if bestnode_id != -1:
            cur.execute('INSERT INTO Arc(Aid, NewId1, NewId2, onetwo, twrw, name, isPushbackRoute) VALUES (?,?,?,?,?,?,"1")', (lid,p[0],bestnode_id,"twoway","taxiway", p[3]))
            #print "parking NewID ",  bestnode[3], p[0]
            cur.execute("UPDATE Parkings SET pushBackRoute = ? WHERE NewId = ? AND Aid = ?;",(bestnode_id, p[0], lid ))
            cur.execute('UPDATE Taxinodes SET holdPointType = "PushBack" WHERE NewID = ? AND Aid = ?',(bestnode_id,lid))
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
        # see sqlite2xml line 133
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
    cur.execute("CREATE TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TXT, Lat TXT, Lon TXT, Heading TXT, NewId INT, pushBackRoute TXT, Type TXT, Radius INT )")
    cur.execute("CREATE TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId INT, NewId INT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway INT, holdPointType TXT)")
    cur.execute("CREATE TABLE Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 INT, NewId1 INT, OldId2 INT, NewId2 INT, onetwo TXT, twrw TXT, Name TXT,isPushBackRoute INT)")
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
                print icao , name

                cur.execute("INSERT INTO Airports(Name,Icao) VALUES (?,?)", (name, icao))
                lid = cur.lastrowid
                    #print "lid:" , lid
                
                offset=0
            elif line.startswith("1300 "):
                #lat = -555                                                                                                                                             
                #lon = -555
                #heading = 0
               
                # Match line 1300
                result = pattern1300.match(line)
                if result:
                        lat = result.group(1)
                        lon = result.group(2)
                        heading = result.group(3)
                        # group 4 has the type of aircraft and group 5 is services available at the parking
                        # type: misc, tie-down, gate, hangar
                        #print "type:", result.group(4),
                        
                        xptype = result.group(4)
                        
                        if xptype == "tie-down":
                            fgtype = "ga"
                        else:
                            fgtype = "gate"
                       
                        #xp services    -> FG radius
                        #heavy              44
                        #jets               24
                        #turboprops         21
                        #props              10
                        #helos               8
                        
                        #FG types:                        
                        #ga (general aviation),
                        #cargo (cargo)
                        #gate (commercial passenger traffic)
                        #mil-fighter (military fighter)
                        #mil-cargo (military transport)
                        
                        services = result.group(5)
                        sl = services.split('|')
                        #print sl
                        if "heavy" in sl:
                            radius = 44
                        elif "jet" in sl:
                            radius = 24
                        elif "turboprops" in sl:
                            radius = 24
                        elif "props" in sl:
                            radius = 10
                            fgtype = "ga"
                        elif "helos" in sl:
                            radius = 8
                            fgtype = "ga"
                            
                        pname = result.group(6) 
                        newid = offset  
                        #print pname 
                        if pname:
                            pname = pname.replace(' ', '_')
                            pname = pname.replace('&','and')
                        else:
                            pname = newid
                        #print icao, pname, lat, lon , heading
                        
                        #TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TXT, Lat TXT, Lon TXT, Heading TXT, NewId INT, pushBackRoute TXT, Type TXT, Radius INT )")
                        cur.execute("INSERT INTO Parkings(Aid, Icao, Pname, Lat, Lon, Heading, NewId,Type,Radius) VALUES (?,?,?,?,?,?,?,?,?)", (lid,icao,pname,lat,lon,heading,newid,fgtype,radius))
                        offset=offset+1
                 
            elif line.startswith("15 "):
                result = pattern15.match(line)
                # Match line 15
                if result:
                    #print "PATTERN 15 found!"
                    lat = result.group(1)
                    lon = result.group(2)
                    heading = float(result.group(3))
                    pname = result.group(4)
                    newid = offset
                    if pname:
                            pname = pname.replace(' ', '_')
                            pname = pname.replace('&','_and_')
                    else:
                            pname = newid
                    
                    cur.execute("INSERT INTO Parkings(Aid, Icao, Pname, Lat, Lon, Heading, NewId,Type,Radius) VALUES (?,?,?,?,?,?,?,'gate',44)", (lid,icao,pname,lat,lon,heading,newid))
                    offset=offset+1
                    
            elif line.startswith("1201 "):
                #print "offset", offset
                #                                      1              2            3      4       5   
                # 1201 = taxi node                   lat            lon          type    id       name
               
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
                
            elif line.startswith("1202 "):
                # TaxiWaySegments
                #1202 taxi edge   node-id1  node-id2 “twoway” or “oneway”  “taxiway” or “runway”  name
                #                                      1              2            3      4       5   
                # 1202 = taxi edge                    node         node        1/2way    tw/rw    name
               
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


    #process the last airport?
    connect_parkings(lid)
    set_isOnRunway(lid)
              
    print "all data is stored in sqlite db"
         
   
        
        
    

        
        
