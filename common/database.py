import os

import psycopg2


def get_connection():

  return psycopg2.connect(
    host=os.getenv("DB_HOST", "192.168.200.131"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "kernidata"),
    user=os.getenv("DB_USER", "kerni"),
    password=os.getenv("DB_PASSWORD", "kerni")
  )