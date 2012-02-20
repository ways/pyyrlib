#!/bin/bash

#This file is used to parse location data with yr.no-URLs.
#We will end up with countries.txt, verda2.txt. Import in db with 02-import-data.py

#world
cut -f1,11 --output-delimiter=, verda.txt |sort |uniq > countries.txt
cut -f1,4,11,18 --output-delimiter=, verda.txt > verda2.txt

#norway
cut -f 2,14 --output-delimiter=, noreg.txt |awk 'BEGIN { FS = ":" } {print "NO,",$0 }' > verda2.txt

