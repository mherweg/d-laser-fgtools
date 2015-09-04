

for FILE in `ls *.ac`
do
	echo $FILE
    #remove empty lines
    sed -i '/^[[:space:]]*$/d' $FILE
done

