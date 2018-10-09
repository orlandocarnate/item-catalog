# "Database code" for the DB Forum.

import datetime
import psycopg2, bleach

DBNAME = "forum"

def get_posts():
  db = psycopg2.connect(database=DBNAME)
  c = db.cursor()
  c.execute("SELECT content, time FROM posts ORDER BY time desc")
  posts = c.fetchall()
  db.close()
  return posts


def add_post(content):
  db = psycopg2.connect(database=DBNAME)
  c = db.cursor()
  c.execute("INSERT INTO posts VALUES (%s)", (bleach.clean(content),))
  db.commit()
  db.close()
  
