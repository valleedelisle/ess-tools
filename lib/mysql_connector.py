import logging
import mysql.connector
from mysql.connector import errorcode

LOG = logging.getLogger("mysql")

class MysqlConnect():

  def __init__(self, user='root', password='q1w2e3', host=None, port=3306):
    try:
      self.cnx = mysql.connector.connect(user=user, password=password,
                                         host=host, port=port)
      self.cursor = cnx.cursor()
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)

  def __del__(self):
    self.cnx.close()
