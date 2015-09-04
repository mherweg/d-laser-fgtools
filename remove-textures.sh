

# remove all textures from many .ac files
# known bug: the UV Mapping will not be removed
#http://stackoverflow.com/questions/5410757/delete-a-line-containing-a-specific-string-using-sed

#mkdir backup

for FILE in `ls *.ac`
do
	echo $FILE
    # if backup is empty then
        #cp $FILE backup
        
    sed -i '/texture/d' $FILE
    
    #remove empty lines
    sed -i '/^[[:space:]]*$/d' $FILE
    
    # other untested ways to do it:
    #sed -n '/texture/!p' $FILE
    #grep -v "pattern" file > temp && mv temp file
	
done
