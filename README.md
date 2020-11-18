# d-laser-fgtools

various tools for [Flightgear](http://www.flightgear.org) development

[contact me](http://wiki.flightgear.org/User:Laserman/)

required: Python 2.x

# managing apt.dat (the airports database)

## pg2aptdat
Read an airport from Postgres DB, write in apt.dat format to STDOUT

a single airport:

    ./pg2aptdat.py -i ICAO

all airports:

    ./pg2aptdat.py 

## gateway_pull
Download from gateway.x-plane, write to ICAO.dat file:

    ./gateway_pull.py -i <ICAO>
or 
    ./gateway_pull.py -s <sceneryId>

##aptdat2pg
insert/update one of more airports into Postgres DB:

    ./aptdat2pg.py -f INPUTFILE


# Generating many groundnet files
parking/startup locations for >7000 airports + groundnet including
pushBackRoutes Taxinodes and Taxiway Segments. read more details in the comment
at the beginning of the 2 python files

* Step 1:
    aptdat2sqlite.py

* Step 2:
    sqlite2xml.py

make_parkings.py is an older version of that tool. still ok,
but it cannot handle 30000 airports and it does only parking, no other ground network.

# from OpenStreetMap  to .stg file:

## gpx2stg.py
with josm or other tools you can mark many locations and export them as
.gpx file. I used it for fuel storage tanks.
the script writes to stdout.

    gpx2stg.py -i <inputfile.gpx> -m <path to shared model> -e <elevation>

## osm-center2stg
I used this to generate stg lines for hundreds of churches and castles. 
The input.osm  file is downloaded from http://overpass-turbo.eu
It will be good for churches, chimneys, wind-power generators, fuel tanks, ... because the
heading does not matter. It is not good for soccer fields of filling stations
which need correct heading/alignment.

here is an exampele query for overpass-turbo.eu
 
    [out:xml][timeout:25];
    // gather results
    (
      // query part for: "amenity=place_of_worship"
      node["amenity"="place_of_worship"]({{bbox}});
      way["amenity"="place_of_worship"]({{bbox}});
    );
    // print results
    out center;
    >;
    out skel qt;


SYNOPSIS:

    osm-center2stg.py -i <inputfile> -m <path to shared model> -e <elevation>'


## taxisigns2stg
reads X-plane/WED/Flightgear apt.dat lines with taxi-sign information 
(lines that begin with "20")
and writes stg lines for Flightgear scenery to stdout

known limitation :
* elevation is the same for all signs 

SYNOPSIS:

    taxisigns2stg.py -f <input apt.dat file> -i <ICAO> -e <elevation in meters above MSL>    >nnnnnn.stg


## taxisigns2aptdat
reads .stg lines with OBJECT_SIGN and merges them with apt.dat (of ONE airport) into output.dat
output.dat can then be imported and edited in WED and uploaded to the gateway

SYNOPSIS:

    taxisigns2aptdat.py -s <input .stg file> -a <input apt.dat file>




## parkingxml2aptdat
convert from Flightgear/TaxiDraw parking.xml or ICAO.groundnet.xml
to "1300" type lines in apt.dat format

SYNOPSIS:

    parkingxml2aptdat.py -i inputfile.xml



# working with AC3D models

## rename-textures.py
If you have many models with freely chosen names for the texture files,
then you cannot upload them to http://scenemodels.flightgear.org/
This script renames the texture files and also rewrites the "texture..."
lines inside the .ac file.
The result can be found int the "output" folder
The original .ac-file is saved as .ac.bak 

SYNOPSIS:

    rename-textures.py -i <inputfile>



## fix_xml_header.sh  
replaces the first line of all XML files of the currrent folder recursively
with this header:

    <?xml version="1.0" encoding="UTF-8" ?>

so that they can get accepted at   http://scenemodels.flightgear.org/  

## make_thumbnails.sh  
requirements: fgviewer, Image Magick

For all .ac files in the current folder the script starts the tool "fgviewer"
Move & Zoom and try different light(l) in fgviewer. Capture a picture with "c"  
and press "esc" to leave.

This is a very fast way to generate thumbnail images of many models with the 
correct size & filename.

## remove-empty-lines.sh  
The script removes empty lines from every .ac File in the current folder.
Some versions of the Blender import script crash on empty lines in .ac files.

## remove-textures.sh
The scrit removes every "texture" line from every .ac File in the current folder.
This way you can contribute models without their textures.
Why ? Maybe the License of the textures is not ok, or the file type or the size.



# using X-Plane's World Editor for precise object placement 
Placing scenery objects with the UFO is easy but not always the best choice.
If you want to place objects or group of objects with precise position and heading
you can also use the WorldEditor(WED) and use it's features like: top-down view, enter
exact values for lat,lon,heading, rubberband-select, copy & paste,...

In order to do that, you need the object in X-Plane's .obj format.
Blender can export that (but not import)
Here are a few flightgear shared models in .obj format: 
https://github.com/mherweg/objects

For WED you need a "fake" scenery folder, please read the [wiki article about WED](http://wiki.flightgear.org/WorldEditor)

Put jour objects into:  

    Custom Scenery/Your-Project/objects
Example:

    objects/Models/Airport/Jetway/jetway-movable.xml.obj
    objects/Models/Airport/Jetway/jetway-20.xml.obj
    objects/Models/Boundaries/Fence-20m-green.xml.obj
    objects/Models/Boundaries/Fence-20m-green.ac.obj
    objects/Models/Boundaries/Fence-50m-green.xml.obj
    objects/Models/Boundaries/Fence-10m-green.xml.obj

After placing your objects with WED, click "Save"
You will find the file:

    Custom Scenery/Your-Project/earth.wed.xml

earth.wed.xml is the input file for the converter script

wed2stg.py

SYNOPSIS:

    wed2stg.py -i <inputfile> -e <elevation>   > out.stg



[How to use (as an airport scenery creator)](http://wiki.flightgear.org/Project3000)
------------------------------------------

        git clone https://github.com/mherweg/d-laser-fgtools.git

or [Download zip](https://github.com/mherweg/d-laser-fgtools)

make sure that you have downloaded terrain of the airports that you want to make, otherwise elevation probing will fail and all objects will be at sea level.

Test if fgelev is working on your computer: (be patient, fgelev is slow )

        export FG_ROOT= YOUR FG_ROOT PATH
        export FG_SCENERY= YOUR TERRASYNC PATH
        time echo "foo 8.56256161 50.04758962 " | fgelev

a good result example: 107m above MSL

        foo: 107.910

a bad result example: approx 0m MSL

        foo: -0.34

prepare a custom scenery folder:

        mkdir -p /home/YOURUSERNAME/scenery/test/Objects
        cp -r Models /home/YOURUSERNAME/scenery/test/

write your paths into parameters.py:

        PATH_TO_SCENERY = "/home/YOURUSERNAME/.fgfs/TerraSync"
        PATH_TO_OUTPUT = "/home/YOURUSERNAME/scenery/test"

you might also have to change the fg_root in fgelev.py:

        fg_root = "/usr/share/games/flightgear"

data found at [dsf_txt_collection](https://github.com/FGMEMBERS-SCENERY/d-laser-fgtools/tree/master/dsf_txt_collection)

or download your own collection of ICAO.txt files; see below

populate 1 airport:

        ./dsf2stg.py -i dsf_txt_collection2000/EDDF.txt

populate all (2000+) airports (It takes a few hours and only makes sense if you have terrain for most of them). Before you do that it is a good idea to download the latest 3D scenery packages from the gateway:

        cd dsf_txt_collection
	wget -O airports http://gateway.x-plane.com/apiv1/airports
        ../find3d.py

Finally,

        ./populate.sh > populate.log

getting a new airport:

       cd dsf_txt_collection
       ../gateway_pull.py -i ICAO

testing the result (of running dsf2stg.py):

       fgfs --aircraft=ufo --airport=EDDF --fg-scenery=/home/YOURUSERNAME/scenery/test




