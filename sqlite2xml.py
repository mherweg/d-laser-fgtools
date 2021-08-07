#!/usr/bin/python3
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
import argparse
import natbool

park_only = False

argp = argparse.ArgumentParser(description="sqlite2xml.py - convert a groundnet SQlite database to groundnet.xml files")

argp.add_argument(
	"-b", "--blacklist-icao",
	metavar="ICAO",
	help="add ICAO to the list of blacklisted airports"
)

argp.add_argument(
	"--use-blacklist",
	help="whether to skip blacklisted airports (default: %(default)s)",
	default="yes",
	choices=["yes", "no"],
)

argp.add_argument(
	"-p", "--parkings-only",
	help="process only parkings, no taxiways (default: %(default)s)",
	default="no",
	choices=["yes", "no"]
)

argp.add_argument(
	"-f", "--blacklist-file",
	metavar="FILE",
	help="path to the blacklist file (default: %(default)s)",
	default="./groudnet-blacklist.lst"
)

argp.add_argument(
	"-i", "--input-database",
	metavar="DATABASE",
	help="database the groundnets are stored in (default: %(default)s)",
	default="./groundnets.db"
)

argp.add_argument(
	"-o", "--output-directory",
	help="folder to put Airports/I/C/A/ICAO.groundnet.xml into (default: %(default)s)",
	default="./"
)
args = argp.parse_args()
args.use_blacklist = natbool.natbool(args.use_blacklist)

# list of 90 airports that have groundnets in FG
# that shall not be overwritten
# see:  read_blacklist(filename) and legacy-groundnets-icao.lst
blacklist = []

def read_blacklist(filename):
	f = open(filename, "r")
	
	for line in f:
		line = line.strip()
		if line.startswith("#"):
			continue
		else:
			blacklist.append(line)

def convert_lat(lat):
	if lat < 0:
		lat2 = "S%d %f" % (int(abs(lat)), (abs(lat) - int(abs(lat))) * 60)
	else:
		lat2 = "N%d %f"%(int(abs(lat)), (abs(lat) - int(abs(lat)))* 60)
	return lat2
	
def convert_lon(lon):
	if lon < 0:
		lon2 = "W%d %f"%(int(abs(lon)), (abs(lon) - int(abs(lon)) )* 60)
	else:
		lon2 = "E%d %f" % (int(abs(lon)), (abs(lon) - int(abs(lon))) * 60)
	return (lon2)


def find_dups(cur):
	acout = 0
	
	rows = cur.fetchall()
	for row in rows:
		aid = row[0]
		cur.execute("SELECT Id,Icao FROM Airports WHERE Id=:Aid", {"Aid": aid})
		ap_rows = cur.fetchall()
		
		for ap in ap_rows:
			print(ap[1])
		print(row)
	

#remove ä, ö ,ü, ß etc.
p = re.compile("[^a-zA-Z0-9]")

	  
found = False
parking_counter = 0
groundnet_counter = 0

if args.use_blacklist:
	if not os.path.isfile(args.blacklist_file):
		print("WARNING: not using blacklist file", args.blacklist_file, "beause it does not exist")
	else:
		read_blacklist(args.blacklist_file)
		print("INFO: using blacklist file", args.blacklist_file)
else:
	print("INFO: not using blacklist file")

if args.parkings_only:
	print("WARNING: processing only parkings, skipping taxiways !")

con = lite.connect(args.input_database)

with con:
	cur = con.cursor() 
	
	print("Selecting airports …")
	cur.execute("SELECT Airports.Id,Airports.Icao FROM Airports  WHERE EXISTS (SELECT 1 FROM Parkings WHERE Airports.Id=Parkings.Aid)")
	print("Reading airports (this can take some time) …")
	rows = cur.fetchall()
	print("Processing airports …")
	for row in rows:
		aid = row[0]
		icao = row[1]
		icao = str(icao).strip()
		path = os.path.join(args.output_directory, "Airports")
		
		if icao in blacklist:
			print("WARNING:", icao ,"in blacklist - skipped")
		else:		
			cur.execute("SELECT Pname,Lat,Lon,Heading,NewId,pushBackRoute,Type,Radius,Airlines FROM Parkings WHERE Aid=:Aid", {"Aid": aid}) 
			prows = cur.fetchall()
			if prows:
				parking_counter += 1
				for letter in icao[:-1]:
					path = os.path.join(path, letter)
				print(path)
				if not os.path.exists(path):
					os.makedirs(path)
				
				gf = ".".join([icao, "groundnet.xml"])
				path = os.path.join(path, gf)
				f = open(path, "w")

				f.write("<?xml version=\"1.0\"?>\n<groundnet>\n  <version>1</version>\n")
				f.write("<parkingList>\n")
				
				for prow in prows:
					lat = convert_lat(prow[1])
					lon = convert_lon(prow[2])
					
					if (prow[8] == None):
						airlines = ""
					else:
						airlines = prow[8]
					
					if prow[5]:
						f.write('		<Parking index="%d" type="%s" name="%s" lat="%s" lon="%s" heading="%s"  radius="%s" pushBackRoute="%s" airlineCodes="%s" />\n' % (prow[4], prow[6], prow[0], lat, lon, prow[3], prow[7], prow[5], airlines))
					else:
						f.write('		<Parking index="%d" type="%s" name="%s" lat="%s" lon="%s" heading="%s"  radius="%s" airlineCodes="%s" />\n' % (prow[4], prow[6], prow[0], lat, lon, prow[3], prow[7], airlines))
					
				#write foot
				f.write("</parkingList>\n")
				
				#write nodes
				if not park_only:
					cur.execute("SELECT Lat,Lon,NewId,isOnRunway,holdPointType FROM TaxiNodes WHERE Aid=:Aid", {"Aid": aid}) 
					nodes = cur.fetchall()
					if nodes:
						groundnet_counter += 1
						f.write(" <TaxiNodes>\n")
						for n in nodes:
							#TODO  holdPointType
							lat = convert_lat(n[0])
							lon = convert_lon(n[1])
							f.write('		<node index="%d" lat="%s" lon="%s" isOnRunway="%s" holdPointType="%s"  />\n' % (n[2], lat, lon, n[3], n[4]))
						f.write(" </TaxiNodes>\n")
					
					# write arc
					# but only taxiways, not runways	   WHERE Aid=:Aid AND twrw LIKE "taxiway"
					#TABLE Arc(Id INTEGER PRIMARY KEY, Aid INTEGER, OldId1 TXT, NewId1 TXT, OldId2 TXT, NewId2 TXT, onetwo TXT, twrw TXT, Name TXT)")		
					# <arc begin="26" end="329" isPushBackRoute="0" name="Route" />
					
					cur.execute('SELECT NewId1,NewId2,onetwo,Name,isPushBackRoute FROM Arc WHERE Aid=:Aid AND twrw NOT LIKE "runway"', {"Aid": aid}) 
					arcs = cur.fetchall()
					if arcs:
						f.write(" <TaxiWaySegments>\n")
						
						for a in arcs:
							f.write('		<arc begin="%s" end="%s" isPushBackRoute="%s" name="%s"  />\n' % (a[0], a[1], a[4], a[3]))
							if a[2]=="twoway":
								f.write('		<arc begin="%s" end="%s" isPushBackRoute="%s" name="%s"  />\n' % (a[1], a[0], a[4], a[3]))
						
						f.write(" </TaxiWaySegments>\n")
					else:
						print("WARNING:", len(prows), "parking locations but no taxi network:", icao)
						
				f.write("</groundnet>\n")
				f.close()
			else:
				pass

print("INFO: Number of airports with parking locations:", parking_counter)			
print("INFO: Number of AI ground networks:", groundnet_counter)

