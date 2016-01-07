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

# api documentation:
# http://gateway.x-plane.com/api#get-scenery

# download the airports file (10MB) before running this script:
# wget http://gateway.x-plane.com/apiv1/airports

# this tool tries to download all "3D" airport sceneries from gateway.x-plane.com
# the ICAO.txt for each airport is saved into the current folder.
# you can use those files as input for  xplane2fg  or dsf2stg

from StringIO import StringIO
import os, sys, io
import json, base64, getopt
import httplib
import zipfile


inputfilename="airports"
htconn = httplib.HTTPConnection("gateway.x-plane.com")

def download_stgtxt(sid,icao):
      
    htconn.request("GET", "/apiv1/scenery/%s" % str(sid))
    r1 = htconn.getresponse()
    r2 = r1.read()
    try:
        result = json.loads(r2)
    except:
        print "Cannot download",icao, "recommended Scenery ID:", sid, "- no json?"
        return
    zip_base64 = result["scenery"]["masterZipBlob"]
    zip_blob = base64.b64decode(zip_base64)
    #print("writing %s.zip" % icao)
#    file = open("%s.zip" % icao, "wb")
#    file.write(zip_blob)
#    file.close()
    zip_bytearray = io.BytesIO(zip_blob)
    zip_fhandle = zipfile.ZipFile(zip_bytearray)

    print("reading", icao, sid)
#    myZip = zipfile.ZipFile("%s.zip" % icao, "r")
    #datstring = zip_fhandle.read("%s.dat" % icao)
    try:
        txtstring = zip_fhandle.read("%s.txt" % icao)
    except:
        print "(2D)"
    else:
        print " 3D :-)"
        zip_fhandle.extract(icao + ".txt")
        zip_fhandle.extract(icao + ".dat")
        




# main
c=0
threedee=0
try:  
    infile = open(inputfilename, 'r')
except:
    print "input file ", inputfilename, "not found"
    sys.exit()
    
r2 = infile.read()    
result = json.loads(r2)
airports =  result["airports"]
for a in airports:
    if a['SceneryType'] == 0:
        pass
    else:
        threedee+=1
        print threedee,
        icao = a['AirportCode']
        sid = a['RecommendedSceneryId']
        # only download if we do not have it
        
        if os.path.isfile(icao + ".txt"):
            print "not downloading" , icao
        else:
            download_stgtxt(sid,icao)
    c+=1
    
print "total:", c


        



