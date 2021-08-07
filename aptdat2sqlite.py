#!/usr/bin/python3
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
#Intel Core2 Duo CPU	 P8600  @ 2.40GHz

# you can strip apd.dat before running this tool:
#time egrep "^1 |^16 |^17 |^100 |^101 |^102 |^14 |^15 |^1300 |^1201 |^1202 " apt.dat.18.9.2015 > apt.stripped
#... but you win only 20 seconds ;-)

# don"t forget to run  sqlite2xml.py after this script
# run both together like this:
# ./aptdat2sqlite.py && ./sqlite2xml.py

#grep ^"1 " apt.dat | wc -l

import sqlite3 as lite
import sys
import re
import math
import argparse
import os

import natbool

argp = argparse.ArgumentParser(description="aptdat2sqlite.py - convert an apt.dat file to a SQLite3 database")

argp.add_argument(
	"-i", "--input",
	metavar="APTDAT",
	dest="aptdat",
	help="path to the apt.dat file which should be processed (default: %(default)s)",
	default="apt.dat"
)

argp.add_argument(
	"-p", "--park-only",
	type=natbool.natbool,
	help="process only parkings (default: %(default)s)",
	default="no",
	choices=["yes", "no"]
)

argp.add_argument(
	"-d", "--database",
	default="groundnets.db",
	help="path to the groundnet database (default: %(default)s)"
)

args = argp.parse_args()

park_only = args.park_only

if not os.path.isfile(args.aptdat):
	print("ERROR: The apt.dat file you provided (%s) does not exist. Exiting." % args.aptdat)
	sys.exit(1)

infile = open(args.aptdat, "r")

# lenght of straight pushback route in lat degree
#at the equator, one latitudinal second measures 30.715 metres, one latitudinal minute is 1843 metres and
# one latitudinal degree is 110.6 kilometres
# 1 deg  = 110600m 
push_dist = float(50.0 * (1.0 / 110600))
#also not bad:
#push_dist=float(100.0*(1.0/110600))

# parking location from X-plane tend to be too much forward
park_dist = float(16.0 * (1.0 / 110600))
#list of airports where the parking locations will not be changed
biggest_airport = ""
used = []


p = re.compile("[^a-zA-Z0-9]")
#p.subn("_", msg)
# There are two lines that describe parkings: line 15 and line 1300
pattern15 = re.compile(r"^15\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
pattern1300 = re.compile(r"^1300\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\w|]*)\s*(.*)$")

#gate details:					size	type	 airlines
pattern1301 = re.compile(r"^1301\s*(\w*)\s*(\w*)\s*([\w ]*)\s*(.*)$")




# TaxiNode
pattern1201 = re.compile(r"^1201\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\-0-9\.]*)\s*(.*)$")
# TaxiWay Segment  / "Arc"
pattern1202 = re.compile(r"^1202\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*(\w*)\s*(.*)$")

def find_pushback_node(lon, lat, heading):
	xp = float(lon) - (math.sin(math.radians(heading)) * push_dist)
	yp = float(lat) - (math.cos(math.radians(heading)) * push_dist)
	return xp, yp
	

def move_back(lon, lat, heading):
	heading = float(heading)
	newlon = float(lon) - (math.sin(math.radians(heading)) * park_dist)
	newlat = float(lat) - (math.cos(math.radians(heading)) * park_dist)
	return newlon, newlat

def calc_dist_lazy(x1, y1, x2, y2):
	dx = abs(x1 - x2)
	dy = abs(y1 - y2)
	return dx + dy

def dumpall():
	# show content of all tables			
	cur = con.cursor()
	
	print("Parkings:")
	cur.execute("SELECT * FROM Parkings")
	rows = cur.fetchall()
	print("\n".join(list(map(str, rows))))
	
	print("Nodes")	
	cur.execute("SELECT * FROM Taxinodes")
	rows = cur.fetchall()
	print("\n".join(list(map(str, rows))))

	print("Arcs:")	
	cur.execute("SELECT * FROM Arc")
	rows = cur.fetchall()
	print("\n".join(list(map(str, rows))))

def set_isOnRunway(lid):
 # convert edge "runway"   to node isOnRunway (and then remove them?)
	#Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 TXT, NewId1 TXT, OldId2 TXT, NewId2 TXT, onetwo TXT, twrw TXT, Name TXT)")
	cur.execute("SELECT * FROM Arc WHERE twrw LIKE 'runway' AND Aid = ? ", (lid,))
	arcs =  cur.fetchall()	
	for a in arcs:
		cur.execute("UPDATE Taxinodes SET isOnRunway = '1' WHERE NewId = ? AND Aid = ?;", (a[3], lid))
		cur.execute("UPDATE Taxinodes SET isOnRunway = '1' WHERE NewId = ? AND Aid = ?;", (a[5], lid))
		# do not use runways for taxiing
		# see sqlite2xml line 133
		# cur.execute("DELETE FROM Arc WHERE twrw LIKE "runway" ")
		
		
def add_pushback_routes(lid, newid):
	# add a straight part, then connet to taxiway
	cur = con.cursor()	
	cur.execute("SELECT NewId, Lat, Lon, Pname, Heading FROM Parkings WHERE Aid = ? ", (lid, ))
	parkings = cur.fetchall()	
	cur.execute("SELECT NewId, Lat, Lon FROM Taxinodes WHERE Aid = ? ", (lid, ))
	nodes =  cur.fetchall()

	for p in parkings:
		newid += 1
		heading = p[4]
		lon = p[2]
		lat = p[1] 
		lonp, latp = find_pushback_node(lon, lat, heading)
		 #TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId INT, NewId INT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway INT, holdPointType TXT)")
		cur.execute("INSERT INTO Taxinodes(Aid, NewId, Lat, Lon, isOnRunway, holdPointType) VALUES (?,?,?,?,0,'none')", (lid, newid, latp, lonp))
	   
		cur.execute("INSERT INTO Arc(Aid, NewId1, NewId2, onetwo, twrw, name, isPushbackRoute) VALUES (?,?,?,?,?,?,'1')", (lid, p[0], newid, "twoway", "taxiway", p[3]))
		
		## connect the new node to the groundnet
		mindist = 1.0
		bestnode_id -= 1
		#countp += 1
		for n in nodes:
			#TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId INT, NewId INT, Lat TXT, Lon TXT, Type TXT, Name TXT, isOnRunway INT, holdPointType TXT)")
			# lat, lon
			dist = calc_dist_lazy(latp, lonp, n[1], n[2])
			#dist = calculate_distance(p[1], p[2], n[1], n[2])
			if dist < mindist:
				mindist = dist
				bestnode_id = n[0]
		
		if bestnode_id != -1:
			cur.execute("INSERT INTO Arc(Aid, NewId1, NewId2, onetwo, twrw, name, isPushbackRoute) VALUES (?,?,?,?,?,?,'1')", (lid, newid, bestnode_id, "twoway", "taxiway", p[3]))
			cur.execute("UPDATE Parkings SET pushBackRoute = ? WHERE NewId = ? AND Aid = ?;", (bestnode_id, p[0], lid))
			cur.execute("UPDATE Taxinodes SET holdPointType = 'PushBack' WHERE NewID = ? AND Aid = ?", (bestnode_id, lid))
		else:
			print("WARNING: no Taxinode found for ", p)
		
		
groundnet_counter = 0
#parking_counter=0		
count_arc = 0	 
max_parkings = 0
  
		
# main apt.dat parsing loop
con = lite.connect(args.database)
print("Connected to database", args.database)

with con:
	cur = con.cursor()	
	cur.execute("DROP TABLE IF EXISTS Airports")
	cur.execute("CREATE TABLE Airports(Id INTEGER PRIMARY KEY, Name TEXT, Icao TXT)")
	cur.execute("DROP TABLE IF EXISTS Parkings")
	cur.execute("DROP TABLE IF EXISTS Taxinodes")
	cur.execute("DROP TABLE IF EXISTS Arc")
	cur.execute("CREATE TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TXT, Lat FLOAT, Lon FLOAT, Heading TXT, NewId INT, pushBackRoute TXT, Type TXT, Radius INT, Airlines TXT )")
	cur.execute("CREATE TABLE Taxinodes(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId INT, NewId INT, Lat FLOAT, Lon FLOAT, Type TXT, Name TXT, isOnRunway INT, holdPointType TXT)")
	cur.execute("CREATE TABLE Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 INT, NewId1 INT, OldId2 INT, NewId2 INT, onetwo TXT, twrw TXT, Name TXT, isPushBackRoute INT)")
	print("Created database tables.")	

	id = 0
	lid = -1
	newid = 0
	has_groundnet = False
	for line in infile:
			line = line.strip()
			# 1 for airports, 16 for seaports
			if line.startswith("1 ") or line.startswith("16 ") or line.startswith("17 "):
				#process the previous airport
				if not park_only and has_groundnet:
					if lid >= 0 :
						groundnet_counter += 1
						add_pushback_routes(lid, newid)
						set_isOnRunway(lid)
						print(icao, "parks, arcs:", offset, count_arc)
						if offset > max_parkings:
							max_parkings = offset
							biggest_airport = icao
						if count_arc < 1:
							print("WARNING count_arc=", count_arc)
						has_groundnet = False
						count_arc = 0
					else:
						print("WARNING lid:" , lid, icao)
				
				apt_header = line.split()
				#previous = icao
				icao = apt_header[4]
				name = " ".join(apt_header[5:])
				name = p.sub("_", name)
			   
				cur.execute("INSERT INTO Airports(Name, Icao) VALUES (?, ?)", (name, icao))
				lid = cur.lastrowid
				used = []
				offset = 0
			elif line.startswith("1300 "):
				# Match line 1300
				result = pattern1300.match(line)
				if result:
						lat = result.group(1)
						lon = result.group(2)
						heading = result.group(3)
						# group 4 has the type of aircraft and group 5 is services available at the parking
						# type: misc, tie-down, gate, hangar
						
						xptype = result.group(4)
						radius = 10
						if xptype == "tie-down":
							fgtype = "ga"
						else:
							fgtype = "gate"
						#http://wiki.flightgear.org/Aircraft_radii
						# a320, b737 : 19
						# fokker100  : 18
						
						#xp services	-> FG radius
						#heavy			  44
						#jets			   24
						#turboprops		 19
						#props			  10
						#helos			   8
						
						#FG types:						
						#ga (general aviation),
						#cargo (cargo)
						#gate (commercial passenger traffic)
						#mil-fighter (military fighter)
						#mil-cargo (military transport)
						
						services = result.group(5)
						sl = services.split("|")
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
						if pname:
							pname = pname.replace(" ", "_")
							pname = pname.replace("&", "and")
						else:
							pname = newid
						#TABLE Parkings(Id INTEGER PRIMARY KEY, Aid INTEGER, Icao TXT, Pname TXT, Lat TXT, Lon TXT, Heading TXT, NewId INT, pushBackRoute TXT, Type TXT, Radius INT )")
						
						# move parking spot backwards compared to x-plane
						if fgtype == "gate":
							lon, lat = move_back(lon, lat, heading)
						
						if newid in used:
							print(newid, "reused", icao)
							exit(1)
						else:
							cur.execute("INSERT INTO Parkings(Aid, Icao, Pname, Lat, Lon, Heading, NewId, Type, Radius) VALUES (?,?,?,?,?,?,?,?,?)", (lid, icao, pname, lat, lon, heading, newid, fgtype, radius))
							offset += 1
							used.append(newid)
							
					   
			elif line.startswith("1301 "):
				result = pattern1301.match(line)
				#	 size(A-F)		type: general_aviation, none, airline	  space-seperated airlines
				
				sizecode = result.group(1)
				sizelist= ["A", "B", "C", "D", "E", "F"]
				sizedict = {"A" : 10, "B" : 18, "C" : 20, "D": 32, "E": 36, "F": 40}
				if sizecode in sizelist:
					radius = sizedict[sizecode]
					cur.execute("UPDATE Parkings SET Radius = ? WHERE NewId = ? AND Aid = ?;", ( radius, newid, lid))
				else:
					print("WARNING sizecode:", sizecode)
					
				#radius = get_radius(result.group(1))
				
				airlines = result.group(3).upper()
				airlines = airlines.replace(" ", ", ")
				#airline_list=airlines.split()
				#print(airline_list)
				if airlines:
					cur.execute("UPDATE Parkings SET Airlines = ? WHERE NewId = ? AND Aid = ?;", (airlines, newid, lid))
			elif line.startswith("15 "):
				result = pattern15.match(line)
				# Match line 15
				if result:
					lat = result.group(1)
					lon = result.group(2)
					heading = float(result.group(3))
					pname = result.group(4)
					newid = offset
					if pname:
							pname = pname.replace(" ", "_")
							pname = pname.replace("&", "_and_")
					else:
							pname = newid
							
					# TODO? move old parking spot backwards compared to x-plane?
					if newid in used:
						print(newid, "reused", icao)
						exit(1)
					else:
						cur.execute("INSERT INTO Parkings(Aid, Icao, Pname, Lat, Lon, Heading, NewId, Type, Radius) VALUES (?, ?, ?, ?, ?, ?, ?, 'gate', 17)", (lid, icao, pname, lat, lon, heading, newid))
						offset += 1
				  
					
			elif line.startswith("1201 ") and park_only == False:
				result = pattern1201.match(line)
				if result:
					lat = result.group(1)
					lon = result.group(2)
					nodetype = result.group(3)
					nodeid = result.group(4)
					newid = int(nodeid) + offset
					nodename = result.group(5).replace(" ", "_")
					
					cur.execute("INSERT INTO Taxinodes(Aid, OldId, NewId, Lat, Lon, Type, Name, isOnRunway, holdPointType) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (lid, nodeid, newid, lat, lon, nodetype, nodename, "0", "none"))
				
			elif line.startswith("1202 ") and not park_only:
				result = pattern1202.match(line)
				if result:
					has_groundnet = True
					n1 = result.group(1)
					newid1 = int(n1) + offset
					n2 = result.group(2)
					newid2 = int(n2) + offset
					onetwo = result.group(3)
					twrw = result.group(4)
					name = result.group(5)
					cur.execute("INSERT INTO Arc(Aid, OldId1, NewId1, OldId2, NewId2, onetwo, twrw, name, isPushBackRoute) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (lid, n1, newid1, n2, newid2, onetwo, twrw, name, "0"))
					count_arc += 1

	#process the last airport:
	if park_only:
		dumpall()
	else:
		if has_groundnet:
			add_pushback_routes(lid, newid)
			set_isOnRunway(lid)
			groundnet_counter += 1
				  
	print("Number of AI ground networks:", groundnet_counter)
	print("Airport with most parking locations:", biggest_airport, max_parkings)
	print("All data is stored in", args.database)
	print("Now run ./sqlite2xml.py to create the groundnet.xml files for the airports that were found in the provided apt.at file.")

