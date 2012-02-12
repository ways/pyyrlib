#!/usr/bin/env python
# -*- coding: UTF-8; -*-

import pyofc, subprocess, re, sys, string, math
import os, sys
import urllib, urllib2, urlparse
import xml.dom.minidom
import traceback, codecs, pyyrlib
import datetime

#file="/tmp/pyyrlib-cache/newyork"

#with codecs.open(file, 'r') as f:
#  filetime = f.readline()
#  print "Filetime ", filetime
#  print "Returning cached data for", id
#  weatherdata = f.read()

weatherdata, source = pyyrlib.returnWeatherData("newyork", True)
tabular = []
print weatherdata

for item in weatherdata['tabular']:
  print item['from']

tabular.append(weatherdata['tabular'][0])

for i in range (1, 22):
  weather = dict()

  #2012-02-13T01:00:00
  fromtime = datetime.datetime.strptime(weatherdata['tabular'][0]['from'], "%Y-%m-%dT%H:%M:%S") \
    + datetime.timedelta(hours=i)
  weather['from'] = fromtime.strftime("%Y-%m-%dT%H:%M:%S")

  #check if we have real data for this hour
  if weatherdata['tabular']

  #temperature '-3'
  weather['temperature'] = ( float(weatherdata['tabular'][i-1]['temperature']) \
  + float(weatherdata['tabular'][i]['temperature']) ) / 2.0

  #'precipitation': u'0'
  weather['precipitation'] = ( float(weatherdata['tabular'][i-1]['precipitation']) + \
    float(weatherdata['tabular'][i]['precipitation']) ) / 2.0

  tabular.append(weather)

new = dict()
new["tabular"] = tabular
print "new"
print new
