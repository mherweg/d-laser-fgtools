#!/usr/bin/python
# -*- coding: utf-8 -*-

# work in progress
# 


import sys, numpy


filename="EDLM.dat"
airport="EDLM"

#airport = sys.argv[2]
#filename = sys.argv[1]

infile = open(filename, 'r')

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
    
def calculate_distance(p,n):    
    a = numpy.array((p[0] ,p[1]))
    b = numpy.array((n[1], n[2]))
    dist = numpy.linalg.norm(a-b)
    return dist
    
    
for line in infile:
            line = line.strip()
            # 1 for airports, 16 for seaports
            if line.startswith("1 "):
                    if " %s "%airport in line:
                            found = True
                            break

if not found:
            print("Airport not found")
            sys.exit(1)

    # Here, we are at the airport

import re
    # There are two lines that describe parkings: line 15 and line 1300
pattern15 = re.compile(r"^15\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)$")
pattern1300 = re.compile(r"^1300\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\w|]*)\s*(.*)$")
# 1201 = taxi node                   lat            lon          type    id       name
pattern1201 = re.compile(r"^1201\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(.*)\s*([\-0-9\.]*)\s*(.*)$")
      
i=0                                                                                                                                                                
parkings = []   
taxinodes=[]   
taxiedges=[]                                                                                                                                             
for line in infile:                                                                                                                                             
            line = line.strip()                                                                                                                                     
            # If the airport description ends, break                                                                                                               
            if line.startswith("1 "):                                                                                                                               
                    break                                                                                                                                           
                                                                                                                                                                
            lat = -555                                                                                                                                             
            lon = -555
            heading = 0
            result = pattern15.match(line)
            # Match line 15
            if result:
                    lat = float(result.group(1))
                    lon = float(result.group(2))
                    heading = float(result.group(3))
                    name = result.group(4).replace(' ', '_')
            # Match line 1300
            else:
                    result = pattern1300.match(line)
                    if result:
                            lat = float(result.group(1))
                            lon = float(result.group(2))
                            heading = float(result.group(3))
                            # group 4 has the type of aircraft and group 5 is services available at the parking
                            name = result.group(6).replace(' ', '_')
                            
            # If found, convert values
            if lat != -555:
		parkings.append([lat, lon, heading, name, -1, -1])                

            # taxinode
            #                                      1              2            3      4       5   
            # 1201 = taxi node                   lat            lon          type    id       name
            pattern1201 = re.compile(r"^1201\s*([\-0-9\.]*)\s*([\-0-9\.]*)\s*(\w*)\s*([\-0-9\.]*)\s*(.*)$")
            result = pattern1201.match(line)
            if result:
		#print result.group(1), result.group(2),  result.group(3) ,result.group(4), result.group(5)
		lat = float(result.group(1))
		lon = float(result.group(2))
		nodetype = result.group(3)
		nodeid = result.group(4)
		nodename = result.group(5).replace(' ', '_')
		taxinodes.append((nodeid, lat, lon),)
#        N51 38.894557 E7 9.686969 both 1 _start
		#print nodeid , lat2, lon2, nodetype
		nodeid_int = int(result.group(4))
		#print nodeid_int, type(nodeid_int)
		if (nodeid_int > i):
		    i = nodeid_int+1
		    
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
		n2 = result.group(2)
		onetwo = result.group(3)
		rwtw = result.group(4)
		name = result.group(5)
		taxiedges.append((n1, n2, "0", name ),)
           
infile.close()


# connect  the parking spots to their nearest node
i=900
for p in parkings:
    i = i + 1
    p[4]=i     # parking index number: 901...
    mindist=1.0
    bestnode=-1
    for n in taxinodes:
	    dist = calculate_distance(p,n)
	    if dist < mindist:
		mindist=dist
		#print "new mindist" , dist
		bestnode = n
    #print p , bestnode
    if bestnode != -1:
	taxiedges.append((p[4], bestnode[0], "1", "toGate" ),)
    else:
	print "no node for ", p
    


print('<?xml version="1.0"?>\n<groundnet>\n   <parkingList>')
for p in parkings:

    print('        <Parking index="%d" type="gate" name="%s" lat="%s" lon="%s" heading="%6.2f" />'%(p[4], p[3], convert_lat(p[0]), convert_lon(p[1]), p[2]))
            
print("   </parkingList>")

print "   <TaxiNodes>"
for n in taxinodes:
    nodeid_int=int(n[0])
	# <node index="552" lat="N52 18.513" lon="E04 46.375" isOnRunway="0" holdPointType="PushBack" />
    print('        <node index="%d" lat="%s" lon="%s" isOnRunway="0" holdPointType="none" />'%(nodeid_int, convert_lat(n[1]), convert_lon(n[2])))

print "   </TaxiNodes>"



print "   <TaxiWaySegments>"

 #   <arc begin="0" end="315" isPushBackRoute="1" name="Route" />
for e in taxiedges:
    print('        <arc begin="%s" end="%s" isPushBackRoute="%s" name="%s"  />'%(e[0], e[1], e[2], e[3]))

print "   </TaxiWaySegments>"
print "\n</groundnet>"



