#!/bin/sh

FILES=*.tif
for f in $FILES
do
    echo "$f"
    FULL_FILENAME=$f
    _FULL_FILENAME="_$FULL_FILENAME"    
    #append "_" to the beginning of FULL_FILENAME
    gdal_translate $FULL_FILENAME $_FULL_FILENAME
    mv $_FULL_FILENAME ../_train/11
done
