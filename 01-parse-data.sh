#!/bin/bash

#This file is used to parse location data with yr.no-URLs.
#We will end up with countries.txt, verda2.txt. Import in db with 02-import-data.py

echo "parse world"
cut -f1,11 --output-delimiter=, verda.txt |sort |uniq > countries.txt
cut -f1,4,11,18 --output-delimiter=, verda.txt > verda2.txt

echo "parse norway"
tail -n+2 noreg.txt |cut -f 2,14 --output-delimiter=, |awk 'BEGIN { FS = "," } {print "NO,",$1,",Norway,",$2 }' >> verda2.txt
echo "NO,Norway" >> countries.txt
