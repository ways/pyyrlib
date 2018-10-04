#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyYrLib
-------

PyYrLib is a simple python library for using Yr.no’s weather data API.

You are welcome to participate in this project!
"""

__version__ = '20180929'
__url__ = 'https://gitlab.com/larsfp/pyyrlib'
__license__ = 'BSD License'
__docformat__ = 'markdown'

import os, sys
import requests
import xml.dom.minidom
import traceback
import mysql.connector # sudo pip install mysql-connector
import pyofc

verbose = True

def get_location_url(location=False, hourly = False):
    """ This function returns the yr.no url of the weather data at a specific
        location. Postal code is easy, but name search has to connect to db.
    """

    if not location:
        if verbose:
            print("get_location_url called without location " + location)
        return False

    filename = "/varsel.xml"
    if hourly:
        filename = "/forecast_hour_by_hour.xml"

    if location.isdigit():
        result = "http://www.yr.no/sted/Norge/postnummer/" + location + filename
    else:
        conn, cursor = get_db_cursor ()
        result = get_xmlurl_by_name (cursor, sanitize_string(location))

    return result

def download_and_parse(url, location):
    """ Download the xml file
    """
    #print "download_and_parse",url
    # Download the xml data, cached
    ofc = pyofc.OfflineFileCache ('/tmp/pyyrlib-cache/', 1800, urlopenread,
      url, False)
    if not ofc:
        return False

    response, fromcache = ofc.get(location)

#  print " returned " \
#    + url\
#      .replace('http://www.yr.no/sted/', '')\
#      .replace('http://www.yr.no/place/', '')\
#      .replace('/forecast.xml','')\
#      .replace('/forecast_hour_by_hour.xml','') +\
#    " for keyword " + location +\
#    ", cached: " + str(fromcache)
    location += " cached: " + str(fromcache)

    #print (response)
    # Parse the xml data
    xmlobj = xml.dom.minidom.parseString(response)
    # Return xml object
    return xmlobj

def interpret(xmlobj):
    """ Interpret the xml data and return an array of dicts containing the data.

    The XML data typically looks like this:

    <weatherdata>
      <location></location>
      <credit></credit>
      <links></links>
      <meta></meta>
      <sun rise="2009-11-16T08:16:59" set="2009-11-16T15:45:46" />
      <forecast>
        <text>
          <location name="Tøyen">
            <time from="2009-11-16" to="2009-11-17">
              <title>mandag og tirsdag</title>
              <body>&lt;strong&gt;Oslo:&lt;/strong&gt; Skiftende bris, fra i
              ettermiddag østlig bris. For det meste skyet oppholdsvær. Lokal
              tåke. Fra natt til tirsdag litt regn av og til. Økende nedbør
              tirsdag formiddag, men minkende igjen om ettermiddagen.</body>
            </time>
            <time from="2009-11-18" to="2009-11-18"></time>
                <time from="2009-11-19" to="2009-11-22"></time>
              </location>
        </text>
        <tabular>
          <time from="2009-11-16T12:00:00" to="2009-11-16T18:00:00" period="2">
            <!-- Valid from 2009-11-16T12:00:00 to 2009-11-16T18:00:00 -->
            <symbol number="4" name="Skyet" />
            <precipitation value="0.0" />
            <!-- Valid at 2009-11-16T12:00:00 -->
            <windDirection deg="48.1" code="NE" name="Nordøst" />
            <windSpeed mps="2.8" name="Svak vind" />
            <temperature unit="celcius" value="4" />
            <pressure unit="hPa" value="1012.2" />
          </time>
          <time from="2009-11-16T18:00:00" to="2009-11-17T00:00:00" period="3">
          </time>
        </tabular>
      </forecast>
    </weatherdata>

    The array of dicts typically looks like this:

    weatherdata =
      {
        'location':    "Tøyen",
        'sunrise':    "2009-11-16T08:16:59",
         'sunset':    "2009-11-16T15:45:46",
        'text':    [
                {
                  'from':       "2009-11-16",
                  'to':        "2009-11-17",
                  'title':      "mandag og tirsdag",
                  'description':    "Oslo: Skiftende bris, fra i ettermiddag ..."
                },
                {
                  ...
                }
              ]
        'tabular':  [
                {
                  'from':       "2009-11-16T12:00:00",
                  'to':        "2009-11-16T18:00:00",
                  'period':      "2",
                  'symbolnumber':    "4",
                  'symbolname':    "Skyet",
                  'precipitation':  "0.0",
                  'windDirection':  {'degrees': "48.1", 'code': "NE", 'name': "Nordøst"}
                  'windSpeed':    {'mps': "2.8", 'name': "Svak vind"}
                  'temperature':    "4"      # Unit: Celcius
                  'pressure':      "1012.2"  # Unit: hPa
                },
                {
                  ...
                }
              ]
      }
    """

    # A simplifying function
    # def textInFirstTagWithName(aNode, aName):
    #   try:
    #     result = aNode.getElementsByTagName(aName)[0].nodeValue
    #   except:
    #     result = None

    # Initialize variables
    weatherdata = {
              'location':    "",
              'sunrise':    "",
               'sunset':    "",
              'text':      [],
              'tabular':    []
            }

    # Get the main element
    weatherdatanode = xmlobj.getElementsByTagName("weatherdata")[0]

    # Get sun rise and set
    try:
        sun = weatherdatanode.getElementsByTagName("sun")[0]
        weatherdata['sunrise'] = sun.attributes['rise'].nodeValue
        weatherdata['sunset'] = sun.attributes['set'].nodeValue
    except KeyError: #The sun somtimes never rise
        pass

    # Get the forecasts
    forecastnode = weatherdatanode.getElementsByTagName("forecast")[0]

    # Get the textnode and its child node 'location'
    try:
        textnode = forecastnode.getElementsByTagName("text")[0]
        locationnode = textnode.getElementsByTagName("location")[0]

        # Get the location name
        weatherdata['location'] = locationnode.attributes['name'].nodeValue

        # Loop through the time nodes in the text section
        for node in locationnode.getElementsByTagName("time"):

            # Initialize the minidict
            nodedict = {}

            # Get the attributes (from and to dates)
            nodedict['from'] = node.attributes['from'].nodeValue
            nodedict['to'] = node.attributes['to'].nodeValue

            # Get the title and body/description
            n = node.getElementsByTagName("title")[0]
            nodedict['title'] = \
              node.getElementsByTagName("title")[0].childNodes[0].nodeValue
            nodedict['description'] = \
              node.getElementsByTagName("body")[0].childNodes[0].nodeValue

            # Remove html markup
            nodedict['description'] = nodedict['description'].replace('<strong>', '')
            nodedict['description'] = nodedict['description'].replace('</strong>', '')

            # Add minidict to the text array in the weatherdata dict
            weatherdata['text'].append(nodedict)

    except IndexError:
        pass

    # Get the tabularnode
    tabularnode = forecastnode.getElementsByTagName("tabular")[0]

    # Loop through the time nodes in the tabular section
    for node in tabularnode.getElementsByTagName("time"):

        # Initialize the minidict
        nodedict = {}

        # Define a function to simplify
        def getAttribute(thisnode, attributename):
            try:
                return thisnode.attributes[attributename].nodeValue
            except KeyError:
                return None

        # Get the attributes (from and to dates, and period)
        nodedict['from'] = getAttribute(node, 'from')
        nodedict['to'] = getAttribute(node, 'to')
        nodedict['period'] = getAttribute(node, 'period')

        # Get the symbol data
        symbolnode = node.getElementsByTagName('symbol')[0]
        nodedict['symbolnumber'] = getAttribute(symbolnode, 'number')
        nodedict['symbolname'] = getAttribute(symbolnode, 'name')

        # Get the wind direction data
        windirectionnode = node.getElementsByTagName('windDirection')[0]
        wdDegrees = getAttribute(windirectionnode, 'degrees')
        wdCode = getAttribute(windirectionnode, 'code')
        wdName = getAttribute(windirectionnode, 'name')
        nodedict['windDirection'] = \
          {'degrees': wdDegrees, 'code': wdCode, 'name': wdName}

        # Get the wind speed data
        windspeednode = node.getElementsByTagName('windSpeed')[0]
        wdMps = getAttribute(windspeednode, 'mps')
        wdName = getAttribute(windspeednode, 'name')
        nodedict['windSpeed'] = {'mps': wdMps, 'name': wdName}

        # Get the other data
        precipitationnode = node.getElementsByTagName('precipitation')[0]
        nodedict['precipitation'] = precipitationnode.attributes['value'].nodeValue
        #Get max precipitation
        try:
            nodedict['precipitationmax'] = precipitationnode.attributes['maxvalue'].nodeValue
        except KeyError:
            pass

        temperaturenode = node.getElementsByTagName('temperature')[0]
        nodedict['temperature'] = temperaturenode.attributes['value'].nodeValue
        pressurenode = node.getElementsByTagName('pressure')[0]
        nodedict['pressure'] = pressurenode.attributes['value'].nodeValue

        # Add minidict to the tabular array in the weatherdata dict
        weatherdata['tabular'].append(nodedict)

    # Return dict
    return weatherdata

def printWeatherData(weatherdata):
    """ Function that outputs text formatted weather data
    """
    # Print location as title
    print('\n\033[01;32m%s\033[00m' % (weatherdata['location']))

    # Print first text description (for today)
    print('%s\n' % (weatherdata['text'][0]['description']))

    # Loops through the first three tabular info to print some numbers
    for item in weatherdata['tabular'][:]:
        # Format precipitation if there are any
        if item['precipitation'] != '0.0':
            precipitation = '(%s mm nedbor) ' % (item['precipitation'])
        else:
            precipitation = ''
        # Format windSpeed if it is higher than 5
        if item['windSpeed']['mps'] != '.' or int(item['windSpeed']['mps']) > 5:
            windSpeed = '(%s (%s mps)) ' % (item['windSpeed']['name'], \
              item['windSpeed']['mps'])
        else:
            windSpeed = ''
        # Print the line
        print('%s %2.2s grader %s%s' % (item['from'][11:16],
                        item['temperature'],
                        precipitation,
                        windSpeed))
#    print item
        # If this is the last period in a 24 hour period, add some whitespace
        if item['period'] == '3':
            print()

    # A little whitespace
    print()


def returnWeatherData(location, hourly = False):
    """ Function that combines getting, parsing and interpreting data.
        Returns False on failure.
    """
    locationurl = ''
    weatherdata = None

    # Try to get location url
    try:
        locationurl = get_location_url(location, hourly)
    except mysql.connector.Error as e:
        print("Error in retreiving a location url (no database available): " + location + str(e))
        return False, ""
    except AttributeError as e:
        if verbose:
            print("returnWeatherData AttributeError %s" % e)
        return False, "%s" % e
    except:
        print("returnWeatherData Error in retreiving a location url: " + location)

    if not locationurl: # No hits
        if verbose:
            print("No locationurl")
        return False, ""
    elif 1 < len(locationurl): # Multiple hits
        return False, locationurl
    else: # One hit
        # Try to download and parse data
        #try:
        xmlobj = download_and_parse(locationurl[0][0], location)
        #except Exception as e:
        #  print("Error in downloading and parsing xml data: ")
        #  print(e)
    #    traceback.print_exc()
        #return False, ""

        # Try to interpret xml object
        try:
            weatherdata = interpret(xmlobj)
        except:
            print("Error in interpreting xml data:")
            traceback.print_exc()
            sys.exit(1)

        # Return weather data
        return weatherdata, locationurl


def getAndPrint(location):
    """ A function that combines the getting and printing of data
    """
    # Get weather data
    weatherdata = returnWeatherData(location)

    if not weatherdata:
        if verbose:
            print("No weatherdata")
        return False

    # Try to print data
    try:
        printWeatherData(weatherdata)
    except:
        print("Error in printing xml data:")
        traceback.print_exc()
        sys.exit(1)
    return 0


def get_db_cursor ():
    conn = mysql.connector.connect(user='pyyrlib', password='pyyrlib',
                                host='10.223.68.17',
                                database='pyyrlib')
    # conn=MySQLdb.connect(host = "localhost",
    #                          user = "pyyrlib",
    #                          passwd = "ifoo3aeshahN",
    #                          db = "pyyrlib")
    return conn, conn.cursor ()


def get_xmlurl_by_name (cursor, name):
    # query = "SELECT xml " +\
    #   "FROM verda " +\
    #   "WHERE placename LIKE('" + name + "%') " +\
    #   "UNION " +\
    #   "SELECT xml " +\
    #   "FROM verda " +\
    #   "WHERE LOWER(xml) LIKE ('%" + name + "%') " +\
    #   "LIMIT 1"

    query = "SELECT DISTINCT xml " +\
      "FROM verda " +\
      "WHERE LOWER(xml) LIKE ('%" + name + "%') "

    cursor.execute(query)
    result = cursor.fetchall()
    return result


def sanitize_string (str):
    if len(str) > 30:
        str = str[:30]
    str = str.strip()\
      .replace('\\','')\
      .replace(';','')\
      .replace('*','')\
      .replace('&','')\
      .replace("'",'')\
      .replace(".",'')\
      .replace(":",'')\
      .replace('=','')
    return str


def urlopenread (url):
    #return urllib.request.urlopen(url).read()
    r = requests.get(url.strip(), headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'} )
    if 200 == r.status_code:
        return r.text
    else:
        if verbose:
            print("urlopenread %s error opening url %s" % (url, r.status_code))
        return False

# if __name__ == "__main__":
#     # Test if location is provided
#     if sys.argv[1] == []:
#         location = None
#     else:
#         location = sys.argv[1]
#     # Run simple print function
#     sys.exit(getAndPrint(location))
