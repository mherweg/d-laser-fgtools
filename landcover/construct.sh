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

date

WORKBASE=${HOME}/workdirs
OUTPUTDIR=${HOME}/scenery/Terrain
DEBUGDIR=${HOME}/scenery/Debug
SHAREDIR=${HOME}/scenery/Shared
NUDGE="--nudge=20"

mkdir -p ${OUTPUTDIR} ${DEBUGDIR}

#SHAREDOPTS="--no-write-shared-edges --use-own-shared-edges"
#SHAREDOPTS="--no-write-shared-edges"
#
# Allens
#SPAT=""  # this one doesn't work
#SPAT="--min-lon=-180 --max-lon=180 --min-lat=-90 --max-lat=90"
#SPAT="--lat=37.5 --lon=-122 --xdist=5 --ydist=5"
#SPAT="--lat=0 --lon=0 --xdist=170 --ydist=80"
# Base Package
#SPAT="--min-lon=-124 --max-lon=-120 --min-lat=36 --max-lat=39"
# Karibik
#SPAT="--min-lon=-64 --max-lon=-62 --min-lat=17 --max-lat=19"
# KDFW
#SPAT="--min-lon=-98 --max-lon=-96 --min-lat=32 --max-lat=33"
# EDDP
#SPAT="--min-lon=12 --max-lon=13 --min-lat=51 --max-lat=52"
#SPAT="--airport=EDDP"
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
# STAGE 2: Segfault in w010n40/w005n48
#SPAT="--tile-id=2876051"
# Diff With Accumulator returned FALSE
#SPAT="--tile-id=1789153"
# Diff With Accumulator returned FALSE
#SPAT="--tile-id=1040032"
# Hole at 11.38643/47.0058
SPAT="--min-lon=10 --min-lat=46 --max-lon=13 --max-lat=48"
#ZBAA
SPAT="--min-lon=116.5 --min-lat=40.02 --max-lon=116.7 --max-lat=40.15"


CONSTRUCT=/home/martin/terragear/bin/tg-construct
#CONSTRUCT=${HOME}/terragear.2011-08-28/bin/fgfs-construct
#CONSTRUCT=${HOME}/terragear/bin/fgfs-construct

#    SRTM2-VFP-3 \
#    SRTM2-Africa-3 \
#    SRTM2-Australia-3 \
#    SRTM2-Eurasia-3 \
#    SRTM2-Islands-3 \
#    SRTM2-North_America-3 \
#    SRTM2-South_America-3 \
#    DEM-USGS-3 \
#    SRTM-30 \
#    SRTM-30-PLUS \

#    Poly-LandMass \

LOADDIRS="AirportArea \
    AirportObj \
    SRTM2-VFP-3-NE \
    SRTM2-VFP-3-NW \
    SRTM2-VFP-3-SE \
    SRTM2-VFP-3-SW \
    Poly-City \
    Poly-Commercial \
    Poly-Floodland \
    Poly-Waterbody \
    Poly-Agro \
    Poly-Forest \
    Poly-LandCover \
    Poly-Ice \
    Poly-Watercourse \
    Poly-RoadCover \
    Line-Road \
    Line-Railroad \
    Line-Stream"

# --threads=4


${CONSTRUCT} \
    --output-dir=${OUTPUTDIR} \
    --work-dir=${WORKBASE} \
    --share-dir=${SHAREDIR} \
    --usgs-map=/home/martin/terragear/share/TerraGear/usgsmap.txt \
    --priorities=/home/martin/terragear/share/TerraGear/default_priorities.txt \
    ${NUDGE} ${SPAT} --ignore-landmass \
    ${LOADDIRS}

# EOF
