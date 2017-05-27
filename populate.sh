
# before running this script for the first time:

# download the airports file (10MB) before running find3d.py:
# wget https://gateway.x-plane.com/apiv1/airports
# mkdir dsf_txt_collection done.d
# cd dsf_txt_collection
# ../find3d.py

# script running time: several hours without *elev.pkl files
#                      5 minutes when *elev.pkl exist already 


for FILE in `ls dsf_txt_collection/*.txt`
do
    
	echo $FILE
    #echo ${FILE%.*}_thumbnail.jpg
   time ./dsf2stg.py -i $FILE
   mv $FILE done.d
   #ls -l dsf_txt_collection | wc -l
   #ls -l done.d | wc -l
   
done
echo "populate.sh finished"

#grep ^no populate-3-2017.log | sort | uniq -c | sort -n | tac

#grep wrote populate-3-2017.log | cut -d " " -f 2- |sort -n

