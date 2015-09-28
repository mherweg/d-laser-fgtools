

#BAD="<?xml version="1.0"?>"
#GOOOD="<?xml version="1.0" encoding="UTF-8" ?>"

for FILE in `find . -name "*.xml"`
do
	echo -n $FILE
    sed -i 's/<?xml version="1.0"?>/<?xml version="1.0" encoding="UTF-8" ?>/' $FILE
    grep ^"<?xml" $FILE
done

