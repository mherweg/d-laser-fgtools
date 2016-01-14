#!/bin/bash -x
#
# Copyright (C) - 2006  FlightGear scenery team
# Copyright (C) 2006 - 2014  Martin Spott
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

WORKBASE=${HOME}/flightgear/terrain/workdirs
NUDGE="--nudge=20"

SPAT=""
# Base Package
#SPAT="--min-lon=-124 --max-lon=-120 --min-lat=36 --max-lat=39"
# Karibik
#SPAT="--min-lon=-64 --max-lon=-62 --min-lat=17 --max-lat=19"
# KDFW
#SPAT="--min-lon=-98 --max-lon=-96 --min-lat=32 --max-lat=33"
# EDDP
#SPAT="--min-lon=12 --max-lon=13 --min-lat=51 --max-lat=52"
#SPAT="--airport=KSFO"
# LFLJ
#SPAT="--min-lon=6 --max-lon=7 --min-lat=45 --max-lat=46"
# EDEN
#SPAT="--min-lon=9 --min-lat=50 --max-lon=10 --max-lat=51"
# Diego Garcia
#SPAT="--min-lon=72 --min-lat=-8 --max-lon=73 --max-lat=-7"
# Netherlands / FSweekend
#SPAT="--min-lon=2.8 --min-lat=49.8 --max-lon=8.2 --max-lat=54.2"
# Rheinland
#SPAT="--min-lon=6.5 --min-lat=50.5 --max-lon=7.5 --max-lat=51.5"
# EPBY
#SPAT="--min-lon=17.5 --min-lat=52.5 --max-lon=18.5 --max-lat=53.5"
# KEDW
#SPAT="--min-lon=-120.5 --min-lat=32.5 --max-lon=-115.5 --max-lat=37.5"
# Berlin / LinuxTag
#SPAT="--min-lon=12.5 --min-lat=51.5 --max-lon=14.5 --max-lat=53.5"
# KOSH
#SPAT="--min-lon=-91 --min-lat=42 --max-lon=-86 --max-lat=46"
# Grand Canyon
#SPAT="--min-lon=-116 --min-lat=35 --max-lon=-109 --max-lat=38"
# WSAC
#SPAT="--min-lon=101 --min-lat=0 --max-lon=106 --max-lat=3"
# Switzerland
#SPAT="--min-lon=6 --min-lat=46 --max-lon=10 --max-lat=49"
# T3r
#SPAT="--min-lon=0 --min-lat=50 --max-lon=20 --max-lat=60"
# CLC2000
#SPAT="--min-lon=-25.25 --min-lat=27.25 --max-lon=45 --max-lat=71.5"
# France (including Corsica)
#SPAT="--min-lon=-5.20 --min-lat=41.31 --max-lon=8.4 --max-lat=51.12"

#APTDAT=${HOME}/live/airfield/apt.helidat.gz
#APTDAT=${HOME}/live/airfield/apt.dat-fsweekend
#APTDAT=${HOME}/live/airfield/v9.00/apt.dat
#APTDAT=${HOME}/live/airfield/testapt.dat.gz
#APTDAT=${HOME}/landcover/EDKA.dat.gz

#APTDAT="/home/martin/live/airfield/v10+/apt.dat"
APTDAT="/home/mherweg/ksfo.gravel.dat"

APTDAT=$1

#DEM="--clear-dem-path --dem-path=SRTM2-VFP-3 --dem-path=SRTM2-Africa-3 \
#--dem-path=SRTM2-Australia-3 --dem-path=SRTM2-Eurasia-3 \
#--dem-path=SRTM2-Islands-3 --dem-path=SRTM2-North_America-3 \
#--dem-path=SRTM2-South_America-3 --dem-path=DEM-USGS-3 --dem-path=SRTM-30"

#DEM="--clear-dem-path --dem-path=SRTM2-VFP-3-NE --dem-path=SRTM2-VFP-3-NW \
DEM="--dem-path=SRTM2-VFP-3-NE --dem-path=SRTM2-VFP-3-NW \
     --dem-path=SRTM2-VFP-3-SE --dem-path=SRTM2-VFP-3-SW"

GENAPTS=/home/martin/terragear/bin/genapts850

echo ${APTDAT}
ls -l ${APTDAT}

#${GENAPTS} --threads --input=${APTDAT} --work=${WORKBASE} ${DEM} ${NUDGE} ${SPAT}
${GENAPTS} --input=${APTDAT} --work=${WORKBASE} ${DEM} ${NUDGE} ${SPAT}

# EOF
