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
import json, base64, os, getopt, sys
#import http.client
import httplib
import zipfile

helptext = 'gateway_pull.py -i <ICAO> \ngateway_pull.py -s <sceneryId>'


def main(argv):
    
    icao="XXXX"
    sid = ""
    sids=[]
    author =""

    try:
        opts, args = getopt.getopt(argv,"hi:s:")
    except getopt.GetoptError:
        print helptext
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helptext
            sys.exit()
        elif opt == "-i":
            icao = arg
        elif opt == "-s":
            sid = arg
    conn = httplib.HTTPSConnection('gateway.x-plane.com')
    
    if sid == "":
        
        conn.request("GET", "/apiv1/airport/" + icao)
        r1 = conn.getresponse()
        r2 = r1.read()
        result = json.loads(r2)
        sid=result["airport"]["recommendedSceneryId"]

        sceneries =  result["airport"]["scenery"] 
        for s in sceneries:
            for k2, v2 in s.items():
                if k2 in ["dateDeclined","dateAccepted","DateAccepted","DateApproved","DateDeclined","userId","type"]:
                    pass
                else:
                    print k2, v2
            if s['Status']=="Approved":
                    sids.append(s['sceneryId'])
            if s["sceneryId"]  ==  sid:
                author = s["userName"]
            print "-----------------"
            
        print "approved scenery ids for " + icao + ":", sids            
        #print "highest approved id:", max(sids)
        print "recommended SceneryId:" , sid , "by author:", author


    conn.request("GET", "/apiv1/scenery/" + str(sid))
    r1 = conn.getresponse()
    r2 = r1.read()
    result = json.loads(r2)
    #print result
    encoded_zip = result["scenery"]["masterZipBlob"]

    blob = base64.b64decode(encoded_zip)

    #print "writing ", icao + ".zip"
    file = open(icao + ".zip","wb")
    file.write(blob)
    file.close()

    #print "reading ", icao + ".zip"
    myZip = zipfile.ZipFile(icao + ".zip","r")
    

    print "writing ", icao + ".dat",
    myZip.extract(icao + ".dat")
    try:
        #print "writing ", icao + ".txt"
        myZip.extract(icao + ".txt")
    except:
        print "(2D)"
    else:
        print " 3D :-)"

    #print "deleting ", icao + ".zip"
    os.remove(icao + ".zip")





#newFileByteArray = bytearray(zipfile)
#newFile.write(blob)

#for zipContentFile in myZip.namelist():
#    data = myZip.read(zipContentFile)
#    #print zipContentFile
#    file = open(zipContentFile, 'w+b')
#    file.write(data)
#    file.close()

#myZip = zipfile.ZipFile(icao + "_Scenery_Pack.zip","r")
#myZip.extract(icao + "_Scenery_Pack/Earth nav data/apt.dat")



if __name__ == "__main__":
   main(sys.argv[1:])


