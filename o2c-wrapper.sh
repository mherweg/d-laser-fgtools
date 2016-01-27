#!/bin/bash


# w130n30/w123n37/942058.stg


IFS='/' read -ra ADDR <<< $1

TOP="${ADDR[0]}"
MED="${ADDR[1]}"
STG=${ADDR[2]%.stg}
#echo $STG

#1.) batch  $MED
python ./batch_processing/build_tiles.py -t $MED -f params.ini -o params.ini
python ./batch_processing/build_tiles.py -t $MED -f roads.ini -o roads.ini

#2.) download OSM data

#ls $TOP/$MED/$STG/buildings.osm
if [ -e "$TOP/$MED/$STG/buildings.osm" ]
then
  echo "using existing buildings.osm"
else
  dline=`grep  $STG $TOP/download_$MED.sh`
  `$dline`
fi



#3.) run osm2city
dline=`grep  $STG $TOP/osm2city_$MED.sh`
echo $dline
#sleep 10
`$dline`

#4) run roads.py
dline=`grep  $STG $TOP/roads_$MED.sh`
echo $dline
#sleep 10
`$dline`

#5 ln txt
#echo ln -s /mh/download/osm2city/osm2city-data/tex /mh/myscenery/Objects/$TOP/$MED
ln -s /mh/download/osm2city/osm2city-data/tex /mh/myscenery/Objects/$TOP/$MED
ln -s /mh/download/osm2city/osm2city-data/tex /mh/scenery/roads/Objects/$TOP/$MED





