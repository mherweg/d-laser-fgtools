#!/bin/bash
# Export scenemodels database to terrascenery svn repository
# Started January 2016 by Torsten Dreyer
# based on work
# Copyright (C) 2004 - 2014  Jon Stockill, Martin Spott
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



DBNAME=scenemodels
DBUSER=updateuser
DBHOST=localhost
PSQL="/usr/bin/psql -d ${DBNAME} -U ${DBUSER} -h ${DBHOST}"

FGELEV="/home/terrascenery/bin/fgelev"
export FG_ROOT="/home/terrascenery/data"
export FG_SCENERY="/home/terrascenery/checkout/"
export LD_LIBRARY_PATH="/home/terrascenery/lib64/"

function finish {
    popd
}
trap finish EXIT

TIMESTAMP="$(date '+%Y%m%d %H:%M')"

pushd "$FG_SCENERY"
# Objects without valid tile numbers are ignored upon export
${PSQL} --quiet  << EOF
UPDATE fgs_objects SET ob_tile = fn_GetTileNumber(wkb_geometry)
    WHERE ob_tile < 1 OR ob_tile IS NULL;
UPDATE fgs_signs SET si_tile = fn_GetTileNumber(wkb_geometry)
    WHERE si_tile < 1 OR si_tile IS NULL;
UPDATE fgs_objects SET ob_elevoffset = NULL 
    WHERE ob_elevoffset = 0;
EOF

test $? == 0 || exit $?

#update ground elevations
echo "Number of ground elevation updates:"
${PSQL}  --tuples-only --quiet --no-align << EOF
SELECT count(*)
    FROM fgs_objects
    WHERE ob_valid IS true AND ob_gndelev = -9999
EOF

${PSQL}  --tuples-only --quiet --no-align --field-separator=' ' << EOF |
SELECT ob_id, ST_X(wkb_geometry), ST_Y(wkb_geometry)
    FROM fgs_objects
    WHERE ob_valid IS true AND ob_gndelev = -9999
    ORDER BY ob_tile;
EOF
$FGELEV | (
  IFS=:
  while read -ra result; do cat << EOF
    UPDATE fgs_objects
      SET ob_gndelev = ${result[1]}
      WHERE ob_id = ${result[0]} AND ob_gndelev = -9999;
EOF
done
) | ${PSQL} --quiet

echo "Running Export.py"
`dirname $0`/Export.py

echo "creating directory index files"
`dirname $0`/CreateDirectoryIndexes.py Models Models
`dirname $0`/CreateDirectoryIndexes.py Objects Objects

echo "version:1" > .dirindex
echo "path:" >> .dirindex
echo "d:Airports:$(sha1sum Airports/.dirindex|cut -f1 -d' ')" >> .dirindex
echo "d:Models:$(sha1sum Models/.dirindex|cut -f1 -d' ')" >> .dirindex
echo "d:Objects:$(sha1sum Objects/.dirindex|cut -f1 -d' ')" >> .dirindex
echo "d:Terrain:$(sha1sum Terrain/.dirindex|cut -f1 -d' ')" >> .dirindex

echo "Fixing permissions"
find Objects/ Models/ -type d -not -perm 755 -exec chmod 755 {} \;
find Objects/ Models/ -type f -not -perm 644 -exec chmod 644 {} \;

echo "Adding new files to svn"
svn add --force --parents --depth infinity Objects Models || exit $?

echo "committing to svn"
svn ci -m "$TIMESTAMP" Models Objects || exit $?

echo "rsyncing to SF"
rsync -a --checksum --delete .dirindex Models Objects web.sourceforge.net:htdocs/scenery/

`dirname $0`/pack.sh

exit 0
