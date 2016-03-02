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

# this program reads AI ground networks from X-Plane/WED apt.dat file
# adds index numbers to the parking positiouns (0...n) and renumbers the
# taxinodes (n+1...m)
# adds one additional taxi node per parking position for a straight line pushback
# and 2 TaxiwaySegments(arc) that connect the parking to the new node and the new node
# to the nearest node of the groundnet(bestnode_id).
# both of those TaxiwaySegments are bi-directional and marked as "pushBackRoute"
# bestnode_id is maked as holdPointType = "PushBack"
# the parking gets a pushBackRoute= entry that is bestnode_id
#
# the result is written into a sqlite DB "groundnets.de"
# which  can be read by the tool sqlite2xml.py

#this script runs 3 minutes on a 
#Intel Core2 Duo CPU     P8600  @ 2.40GHz

# you can strip apd.dat before running this tool:
#time egrep '^1 |^16 |^17 |^100 |^101 |^102 |^14 |^15 |^1300 |^1201 |^1202 ' apt.dat.18.9.2015 > apt.stripped
#... but you win only 20 seconds ;-)

# don't forget to run  sqlite2xml.py after this script
# run both together like this:
# ./aptdat2sqlite.py && ./sqlite2xml.py

#grep ^"1 " apt.dat | wc -l

import sqlite3 as lite
import sys, numpy
import re, math


# only parking, without AI-groundnet: 17 seconds
#park_only=True
park_only=False

input_filename = "EGTG.dat"
#input_filename = "EGLL.dat"
infile = open(input_filename, 'r')

# lenght of straight pushback route in lat degree
#at the equator, one latitudinal second measures 30.715 metres, one latitudinal minute is 1843 metres and
# one latitudinal degree is 110.6 kilometres
# 1 deg  = 110600m 
push_dist=float(50.0*(1.0/110600))
#also not bad:
#push_dist=float(100.0*(1.0/110600))

# parking location from X-plane tend to be too much forward
park_dist=float(16.0*(1.0/110600))
#list of airports where the parking locations will not be changed
move_back_blacklist = ['EGLL',]
blacklist= []




p = re.compile('[^a-zA-Z0-9]')
#p.subn('_', msg)
# There are two lines that describe parkings: line 15 and line 1300
pattern15 = re.compile(r"^15\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
pattern1300 = re.compile(r"^1300\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\w|]*)\s*(.*)$")
# TaxiNode
pattern1201 = re.compile(r"^1201\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\-0-9\.]*)\s*(.*)$")
# TaxiWay Segment  / "Arc"
pattern1202 = re.compile(r"^1202\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*(\w*)\s*(.*)$")


found = False


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
        
    print len(blacklist) , "entries in blacklist"
          


def find_pusback_node(lon,lat,heading):
    #print push_dist
    xp= float(lon) - (math.sin(math.radians(heading))*push_dist)
    yp =float(lat) - (math.cos(math.radians(heading))*push_dist)
    return xp,yp
    
   
def move_back(lon,lat,heading):
    heading = float(heading)
    newlon= float(lon) - (math.sin(math.radians(heading))*park_dist)
    newlat= float(lat) - (math.cos(math.radians(heading))*park_dist)
    return(newlon,newlat)
     
def calculate_distance(x1,y1,x2,y2):    
    a = numpy.array((x1 ,y1))
    b = numpy.array((x2, y2))
    dist = numpy.linalg.norm(a-b)
    return dist

def calc_dist_lazy(x1,y1,x2,y2):
    dx=abs(x1-x2)
    dy=abs(y1-y2)
    return dx+dy

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
    # !!! depricated !!!
    # connect  the parking spots to their nearest node
    # and add this node als pushback route for that spot
    # -------- not used any more. see: add_pushback_routes
   
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
            dist=calc_dist_lazy(p[1],p[2], n[1],n[2])
            #dist = calculate_distance(p[1],p[2], n[1],n[2])
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
    #if countp > 0:
    #    print "Parking spots:", countp
            

def set_isOnRunway(lid):
 # convert edge "runway"   to node isOnRunway (and then remove them?)
    #Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 TXT, NewId1 TXT, OldId2 TXT, NewId2 TXT, onetwo TXT, twrw TXT, Name TXT)")
    cur.execute('SELECT * FROM Arc WHERE twrw LIKE "runway" AND Aid = ? ',(lid,))
    arcs =  cur.fetchall()    
    for a in arcs:
        #print "on runway:" , a[3], a[5]
        cur.execute('UPDATE Taxinodes SET isOnRunway = "1" WHERE NewId = ? AND Aid = ?;',(a[3],lid))
        cur.execute('UPDATE Taxinodes SET isOnRunway = "1" WHERE NewId = ? AND Aid = ?;',(a[5],lid))
        # do not use runways for taxiing
        # see sqlite2xml line 133
        #cur.execute('DELETE FROM Arc WHERE twrw LIKE "runway" ')
        
        
def add_pushback_routes(lid,newid):
    # add a straight part, then connet to taxiway
    cur = con.cursor()    
    cur.execute("SELECT NewId,Lat,Lon,Pname,Heading FROM Parkings WHERE Aid = ? ",(lid,))
    parkings = cur.fetchall()    
    cur.execute("SELECT NewId,Lat,Lon FROM Taxinodes WHERE Aid = ? ",(lid,))
    nodes =  cur.fetchall()

    for p in parkings:
        newid+=1
        heading = p[4]
        lon = p[2]
        lat = p[1] 
        lonp,latp = find_pusback_node(lon,lat,heading)
        #print "park", lon,lat 
        #print "pb  ", lonp,latp
         #TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId INT, NewId INT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway INT, holdPointType TXT)")
        cur.execute('INSERT INTO Taxinodes(Aid, NewId,Lat, Lon,isOnRunway,holdPointType) VALUES (?,?,?,?,0,"none")',(lid,newid,latp,lonp ))
       
        cur.execute('INSERT INTO Arc(Aid, NewId1, NewId2, onetwo, twrw, name, isPushbackRoute) VALUES (?,?,?,?,?,?,"1")', (lid,p[0],newid,"twoway","taxiway", p[3]))
        
        ## connect the new node to the groundnet
        mindist=1.0
        bestnode_id=-1
        #countp+=1
        for n in nodes:
            #TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId INT, NewId INT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway INT, holdPointType TXT)")
            # lat, lon
            dist=calc_dist_lazy(latp,lonp, n[1],n[2])
            #dist = calculate_distance(p[1],p[2], n[1],n[2])
            if dist < mindist:
                mindist=dist
                #print "new mindist" , dist
                bestnode_id = n[0]
            #print p , bestnode
        if bestnode_id != -1:
            cur.execute('INSERT INTO Arc(Aid, NewId1, NewId2, onetwo, twrw, name, isPushbackRoute) VALUES (?,?,?,?,?,?,"1")', (lid,newid,bestnode_id,"twoway","taxiway", p[3]))
            cur.execute("UPDATE Parkings SET pushBackRoute = ? WHERE NewId = ? AND Aid = ?;",(bestnode_id, p[0], lid ))
            cur.execute('UPDATE Taxinodes SET holdPointType = "PushBack" WHERE NewID = ? AND Aid = ?',(bestnode_id,lid))
        #else:
            #print "WARNING: no Taxinode found for ", p
        
        
groundnet_counter=0
parking_counter=0        
     
     
read_blacklist('legacy-groundnets-icao.lst')     
     
        
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
    newid=0
    has_groundnet=False
    for line in infile:
            line = line.strip()
            # 1 for airports, 16 for seaports
            if line.startswith("1 ") or line.startswith("16 ") or line.startswith("17 "):
                
                
                #process the previous airport
                
                if park_only == False and has_groundnet:
                    #print "OK"
                    if lid >= 0 :
                        groundnet_counter+=1
                        add_pushback_routes(lid,newid)
                        connect_parkings(lid)
                        set_isOnRunway(lid)
                        print icao
                        has_groundnet=False
                #else:
                #    print "."
                
                
                apt_header = line.split()
                #previous = icao
                icao = apt_header[4]
                name = ' '.join(apt_header[5:])
                name = p.sub('_', name)
                
                if icao in blacklist:
                    print icao ,"in blacklist - skipped"
                else:
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
                        radius = 10
                        if xptype == "tie-down":
                            fgtype = "ga"
                        else:
                            fgtype = "gate"
                        #http://wiki.flightgear.org/Aircraft_radii
                        # a320, b737 : 19
                        # fokker100  : 18
                        
                        #xp services    -> FG radius
                        #heavy              44
                        #jets               24
                        #turboprops         19
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
                            radius = 19
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
                        
                        # move parking spot backwards compared to x-plane
                        if ( fgtype=="gate" ) and (not(fgtype=="ga")):
                            #print "before", lat,lon,heading
                            if icao in move_back_blacklist:
                                print icao , "- using original parking location for", pname
                            else:
                                (lon,lat) = move_back(lon,lat,heading)
                            
                            #print "after ", lat,lon
                        
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
                            
                    # TODO? move old parking spot backwards compared to x-plane?
                    
                    cur.execute("INSERT INTO Parkings(Aid, Icao, Pname, Lat, Lon, Heading, NewId,Type,Radius) VALUES (?,?,?,?,?,?,?,'gate',17)", (lid,icao,pname,lat,lon,heading,newid))
                    offset=offset+1
                  
                    
            elif line.startswith("1201 ") and park_only == False:
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
                
            elif line.startswith("1202 ") and park_only == False:
                # TaxiWaySegments
                #1202 taxi edge   node-id1  node-id2 “twoway” or “oneway”  “taxiway” or “runway”  name
                #                                      1              2            3      4       5   
                # 1202 = taxi edge                    node         node        1/2way    tw/rw    name
               
                result = pattern1202.match(line)
                if result:
                    
                    has_groundnet = True
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


    #process the last airport:
    #connect_parkings(lid)
    if park_only:
        dumpall()
    else:
        add_pushback_routes(lid,newid)
        set_isOnRunway(lid)
        groundnet_counter+=1
                  
    print "number of AI ground networks:", groundnet_counter
    print "all data is stored in groundnets.db"
    print "now you can run sqlite2xml.py"

           
   
        
        
    

        
        
