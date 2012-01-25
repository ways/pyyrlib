#!/usr/bin/env python
# -*- coding: UTF-8; -*-

'''
Put verda2.txt in mysql db
'''

import string, MySQLdb

def get_mysql_handle ():
  db=MySQLdb.connect(host = "localhost",
                           user = "pyyrlib",
                           passwd = "ifoo3aeshahN",
                           db = "pyyrlib")
  c = conn.cursor ()
  c.execute ("SELECT VERSION()")
  row = c.fetchone ()
  print row
  return
  c.execute("""SELECT spam, eggs, sausage FROM breakfast
          WHERE price < %s""", (max_price,))
  c.fetchone()
  c.executemany(
      """INSERT INTO breakfast (name, spam, eggs, sausage, price)
      VALUES (%s, %s, %s, %s, %s)""",
      [
      ("Spam and Sausage Lover's Plate", 5, 1, 8, 7.95 ),
      ("Not So Much Spam Plate", 3, 2, 0, 3.95 ),
      ("Don't Wany ANY SPAM! Plate", 0, 4, 3, 5.95 )
      ] )

def process_file ():
  fd = open( "verda2.txt" )
  content = fd.readline()
  while (content != "" ):
    fields = string.split(content, ',')
    print fields
    break


get_mysql_handle ()
process_file ()
