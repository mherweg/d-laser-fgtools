#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016  Torsten Dreyer
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

from __future__ import print_function
import os, sys, io, errno
import hashlib

dirindex = ".dirindex"
DIRINDEXVERSION = 1

########################################################################

def fn_hash_of_file(fname):
    hash = hashlib.sha1()
    try:
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
    except:
        pass

    return hash.hexdigest()

########################################################################

def fn_create_directory_index( path, parent ):
    cwd = os.getcwd()

    try:
        os.chdir(path)
    except:
        print("cant chdir to " + path )
        return


    dirindexFile = open(dirindex, 'w')
    print( "version:" + str(DIRINDEXVERSION), file=dirindexFile )
    print( "path:" + parent, file=dirindexFile );

    # create dirindex first
    for child in os.listdir("."):
      if os.path.isfile(child) and child != dirindex:
        print( "f:" + child  + ":" + fn_hash_of_file(child) + ":" + str(os.stat(child).st_size), file=dirindexFile )
      elif os.path.isdir(child) and child != ".svn":
        print( "d:" + child + ":" + fn_create_directory_index(child,os.path.join(parent,child)), file=dirindexFile )

    dirindexFile.close()
    dirindexHash =  fn_hash_of_file(dirindex)
    os.chdir(cwd)
    return dirindexHash

########################################################################

if len(sys.argv) < 2:
    print("usage: " + sys.argv[0] + " path [parent]")
    sys.exit("terminated.");

print( fn_create_directory_index(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "") )

########################################################################
