#!/usr/bin/python
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

#import socket
import json, base64
#import http.client
import httplib
import zipfile

icao="EDLN"
sids=[]
author =""

conn = httplib.HTTPConnection('gateway.x-plane.com')
#conn.request("GET", "/apiv1/releases")
conn.request("GET", "/apiv1/airport/" + icao)
r1 = conn.getresponse()
r2 = r1.read()
result = json.loads(r2)

for key, value in result["airport"].items():
    if key == "recommendedSceneryId":
        #print key,value
        recommendedSceneryId=value
        
for key, value in result["airport"].items():        
    if key == "scenery":
        for s in value:
            for k2, v2 in s.items():
                if k2 in ["dateDeclined","dateAccepted","DateAccepted","DateApproved","DateDeclined","userId","type"]:
                    pass
                else:
                    print k2, v2
            if s['Status']=="Approved":
                    sids.append(s['sceneryId'])
            if s["sceneryId"]  ==  recommendedSceneryId:
                author = s["userName"]
            print "-----------------"
            

print "approved scenery ids for ", icao, sids            
print "highest approved id:", max(sids)
print "recommendedSceneryId" , recommendedSceneryId , "by author:", author


conn.request("GET", "/apiv1/scenery/" + str(recommendedSceneryId))
r1 = conn.getresponse()
r2 = r1.read()
result = json.loads(r2)

#for key, value in result["scenery"].items(): 

encoded_zip = result["scenery"]["masterZipBlob"]

blob = base64.b64decode(encoded_zip)
file = open(icao + ".zip","wb")
file.write(blob)
file.close()

#newFileByteArray = bytearray(zipfile)
#newFile.write(blob)

myZip = zipfile.ZipFile(icao + ".zip","r")
myZip.extract(icao + ".dat")

#for zipContentFile in myZip.namelist():
#    data = myZip.read(zipContentFile)
#    #print zipContentFile
#    file = open(zipContentFile, 'w+b')
#    file.write(data)
#    file.close()

#myZip = zipfile.ZipFile(icao + "_Scenery_Pack.zip","r")
#myZip.extract(icao + "_Scenery_Pack/Earth nav data/apt.dat")


