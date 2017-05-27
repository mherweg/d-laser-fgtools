#!/usr/bin/python

# recalculates all elevations in a .stg file
# Reads the .stg file from standard input, writes to standard output
# Usage: cat 11223344.stg | python recalculate_elevation.py $FG_SCENERY > 11223344.stg.new

import sys
import subprocess
import math

# if an argument exists, use as the scenerydir. If not, use my directories
scenerydir='/home/juanvi/FlightGear/IBE/IBE:/home/juanvi/.fgfs/TerraSync'
if len(sys.argv) == 2:
	scenerydir = sys.argv[1]

# Open communication to fgelev
elev = subprocess.Popen(['fgelev', '--fg-scenery', scenerydir], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# Information about an object
class Position():
	lat = ''
	lng = ''
	type = ''
	ele = ''
	offset = 0.0
	repos = True
	roll = '0.0'
	pitch = '0.0'

# if this is set, the next object has an abolute elevation that shouldn't be calculated
noreposNext = False
# the offset of the next object
offsetNext = 0.0
# the identifier of the next object
id = 1
for l in sys.stdin.readlines():
	try:
		# if the line is an OBJECT or a commented OBJECT...
		if l.startswith('OBJECT') | l.startswith('#OBJECT'):
			# read the line
			items = l.strip().split()
			o = Position()
			# two types of lines: those that include pitch and rolling and those that don't
			if len(items) == 6:
				o.type, o.model, o.lng, o.lat, o.ele, o.hdg = items
			else:
				o.type, o.model, o.lng, o.lat, o.ele, o.hdg, o.roll, o.pitch = items
			# calculate elevation, if noreposNext is not set
			if noreposNext:
				noreposNext = False
				o.ele = float(o.ele)
			else:
				elev.stdin.write('%s %s %s\n' % (str(id), o.lng, o.lat))
				outs = elev.stdout.readline()
				o.ele = float(outs.strip().split()[1])
				id += 1
			# use offset
			o.offset = offsetNext
			offsetNext = 0.0
			# print the line
			print('{} {} {} {} {} {} {} {}'.format(o.type, o.model, o.lng, o.lat, o.ele + o.offset, o.hdg, o.roll, o.pitch))
		elif l.startswith('# norepos'):
			# if this line is found, the next object won't be recalculated
			noreposNext = True
			print(l.strip())
		elif l.startswith('# offset'):
			# if this line is found, the next object will have this offset
			offsetNext = float(l.strip().split()[2])
			print(l.strip())
		else:
			# any other line: just copy
			print(l.strip())
	except:
		print('Error processing line: {}'.format(l))
