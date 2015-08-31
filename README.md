# d-laser-fgtools

Read from Postgres, write to STDOUT

./pg2aptdat.py -i LFHU

Download from gateway.x-plane, write to ICAO.dat file:

./gateway_pull.py -i <ICAO> 
./gateway_pull.py -s <sceneryId>

insert/update one of more airports in the DB:

./aptdat2pg.py -f INPUTFILE

