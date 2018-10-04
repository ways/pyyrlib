#!/usr/bin/env python
# -*- coding: UTF-8; -*-

'''
Put verda2.txt in mysql db
'''

import string, sys # MySQLdb
import mysql.connector # sudo pip install mysql-connector

def get_db_cursor ():
  conn=mysql.connector.connect(host = "10.223.68.17",
                           user = "pyyrlib",
                           passwd = "pyyrlib",
                           db = "pyyrlib")
  return conn, conn.cursor ()


def clear_db (cursor, table):
  query = "delete from " + table
  cursor.execute(query)


def insert_row_countries (cursor, table, fields):
  query = "INSERT INTO " + table + " (countrycode, countryname) VALUES ( "
  
  for i in range(0, 2):
    if 0 != i:
      query += ", "
    query += "'" + all_lower(fields[i]) + "'"

  query += " ) ON DUPLICATE KEY UPDATE countryname = '" + fields[1] + "' ;"

  print (query)
  return cursor.execute(query)


def insert_row_verda (cursor, conn, table, fields):
  query = "INSERT INTO " + table + " (countryid, placename, xml) VALUES ( "
  
  for i in [0, 1, 3]:
    if 0 != i:
      query += ", "
    if 0 == i:
      query += " (select countryid from countries where countrycode = '" + all_lower(fields[0]) + "' ) "
    elif 2 == i:
      continue
    else:
      #query += "'" + conn.fields[i].replace(' ', '') + "'"
      query += '"' + fields[i].replace(' ', '') + '"'

  query += " ) ;"

  print (query)
  return cursor.execute(query)


def process_file_countries (cursor):
  fd = open( "/home/larsfp/git/pyyrlib/countries.txt" )
  content = fd.readline()
  while (content != "" ):
    fields = str.split(content, ',')
    insert_row_countries(cursor, 'countries', fields)
    content = fd.readline()


def process_file_verda (cursor, conn):
  fd = open( "/home/larsfp/git/pyyrlib/verda2.txt" )
  #content = fd.readline() #header
  content = fd.readline()
  while (content != "" ):
    fields = str.split(content, ',')
    insert_row_verda(cursor, conn, 'verda', fields)
    content = fd.readline()


def all_lower (str):
  return str.strip().lower().replace('Æ', 'æ').replace('Ø', 'ø').replace('Å', 'å')


conn, c = get_db_cursor ()
clear_db (c, 'countries')
process_file_countries (c)
clear_db (c, 'verda')
process_file_verda(c, conn)
