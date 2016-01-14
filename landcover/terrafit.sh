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

TERRAFIT=${HOME}/terragear/bin/terrafit
WORKDIR=${HOME}/workdirs/world_scenery

OPTIONS="-x 20000 -e 10"

#SRTMDIRS=`find ${WORKDIR} -maxdepth 1 -type d -name SRTM\* -not -name \*ASCII\* | sed -e "s|${WORKDIR}\/||g" | sort`
#SRTMDIRS=`find ${WORKDIR} -maxdepth 1 -type d -name SRTM2-VFP-3-?? | sed -e "s|${WORKDIR}\/||g" | sort`
SRTMDIRS=`find ${WORKDIR}/SRTM2-VFP-3-?? -maxdepth 1 -mindepth 1 -type d | sed -e "s|${WORKDIR}\/||g" | sort`

for FITDIR in ${SRTMDIRS}; do
    echo "### ----------------------- ${FITDIR} -----------------------"
    ${TERRAFIT} ${OPTIONS} ${WORKDIR}/${FITDIR}
    RETURN=${?}
    echo "### ------------ ${FITDIR} return code ${RETURN} --------------------"
done
