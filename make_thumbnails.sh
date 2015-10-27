
# crate thubnails for all *.ac files in the current directory
# requires bash, fgviewer and imagemagick

# in fgviewer:
#  * rotate & zoom
#  * press c
#  * press esc and wait for the next object

#echo `ls $1`
for FILE in `ls *.ac`
#for FILE in `ls $1`
do
    
	echo $FILE
    echo ${FILE%.*}_thumbnail.jpg
    fgviewer $FILE
    convert screen_shot_0_0.jpg    -resize 320x240\! ${FILE%.*}_thumbnail.jpg
    rm  screen_shot_0_0.jpg
done

