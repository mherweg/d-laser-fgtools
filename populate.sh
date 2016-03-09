
# before running this script for the first time:

# download the airports file (10MB) before running find3d.py:
# wget https://gateway.x-plane.com/apiv1/airports


# mkdir dsf_txt_collection2000 done.d
# cd dsf_txt_collection2000
# ../find3d.py


for FILE in `ls dsf_txt_collection2000/*.txt`
do
    
	echo $FILE
    #echo ${FILE%.*}_thumbnail.jpg
   time ./dsf2stg.py -i $FILE
   mv $FILE done.d
   #ls -l dsf_txt_collection2000 | wc -l
   #ls -l done.d | wc -l
   
done
