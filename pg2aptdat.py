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

# usage:
#python pg2aptdat.py > apt.dat.out
#

import os, sys, getopt
import psycopg2
#from lxml import etree
from settings import *
helptext = 'pg2aptdat.py [-i ICAO]'


def fn_pgexec(cur,sql):
    try:
        cur.execute(sql)
    except psycopg2.Error, e:
        print e
        #print sql
    return cur

def main(argv):
    icao=""
    try:
        opts, args = getopt.getopt(argv,"hi:m:e:")
    except getopt.GetoptError:
        print helptext
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helptext
            sys.exit()
        elif opt == "-i":
            icao = arg
    
    try:
        conn = psycopg2.connect(**db_params)
    except:
        print "Cannot connect to database.", db_params
        sys.exit(2)
        
    cur = conn.cursor()

    if icao != "":
        sql = "SELECT DISTINCT icao,layout FROM apt_dat WHERE icao LIKE '%s' ORDER BY icao" % icao
    else:    
        sql = "SELECT DISTINCT icao,layout FROM apt_dat ORDER BY icao"
        
    fn_pgexec(cur,sql)
    
    #header
    print "I"
    print "1000 Version - data cycle 2013.10, build 20131335, metadata AptXP1000."  

    if cur.rowcount == 0:
        print icao ,"not found"
    else:
        db_result = cur.fetchall()
        for row in db_result:
            print
            icao = row[0]
            linearray= row[1]
            for line in linearray:
                print line
                
    #optional footer:            
    print "99"
                

if __name__ == "__main__":
   main(sys.argv[1:])            
#EOF
