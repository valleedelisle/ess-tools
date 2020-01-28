import logging
import traceback
import time
import mysql.connector
from mysql.connector import errorcode

LOG = logging.getLogger("mysql")

class MysqlConnect():
  cnx = None
  cursor = None
  def __init__(self, user='root', password='q1w2e3', host=None, port=3306):
    while not self.cursor:
      try:
        self.cnx = mysql.connector.connect(user=user, password=password, host=host, port=port, charset="utf8", get_warnings=True, connect_timeout=1000)
        self.cursor = self.cnx.cursor()
      except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
          LOG.error("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
          LOG.error("Database does not exist")
        else:
          LOG.error("Error: %s Traceback: %s" % (err, traceback.format_exc()))
        time.sleep(1)
        pass
 
  def __del__(self):
    self.cnx.close()
