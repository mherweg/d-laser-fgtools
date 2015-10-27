

#cd dsf_txt_collection2000
for FILE in `ls dsf_txt_collection2000/*.txt`
do
    
	echo $FILE
    #echo ${FILE%.*}_thumbnail.jpg
   time ./dsf2stg.py -i $FILE
   mv $FILE done.d
   ls -l dsf_txt_collection2000 | wc -l
   ls -l done.d | wc -l
   
done
