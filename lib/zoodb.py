"""
ZoDB Class
"""

import logging
import time
import sys
import os
from datetime import datetime, timedelta
import persistent
import transaction
import zc.lockfile
import ZODB
import ZODB.FileStorage
from ZODB.FileStorage import fsdump # pylint: disable=unused-import
from ZODB.PersistentMapping import PersistentMapping # pylint: disable=no-name-in-module,import-error, unused-import
LOG = logging.getLogger("root.zodb")

class Zoo():
  """
  ZoDB object
  """
  # pylint: disable=too-many-instance-attributes
  def __init__(self, dbname, conf):
    self.dbname = dbname
    self.case_db_folder = os.path.join(sys.path[0], "db")
    if os.path.isdir(self.case_db_folder) is False:
      try:
        os.mkdir(self.case_db_folder)
      except Exception as exc: # pylint: disable=broad-except
        LOG.error("Unable to create directory: %s", exc)
        exit(1)
    self.case_db_path = os.path.join(self.case_db_folder, self.dbname + ".fs")
    for i in range(1, conf.zodb.getint('retry')):
      try:
        self.storage = ZODB.FileStorage.FileStorage(self.case_db_path)
      except zc.lockfile.LockError as error:
        LOG.warning("ZoDB locked: %s", error)
        if i >= conf.zodb.getint('retry') - 2:
          raise SystemError("ZoDB locked for too long")
        time.sleep(1)
        continue
      else:
        break
    self.db = ZODB.DB(self.storage) # pylint: disable=invalid-name
    self.connection = self.db.open()
    self.root = self.connection.root()
    self.file_handlers = [self.storage._file, # pylint: disable=protected-access
                          self.storage._lock_file, # pylint: disable=protected-access
                          self.storage._tfile, # pylint: disable=protected-access
                          self.storage._files] # pylint: disable=protected-access
    if "cases" not in self.root:
      self.root["cases"] = persistent.dict.PersistentDict()

  def expire(self, expire):
    """
    Function that expires cases in the database
    """
    case_db = self.root["cases"]
    for case in list(case_db):
      case_mod_date = datetime.strptime(case_db[case].lastModifiedDate, '%Y-%m-%dT%H:%M:%SZ')
      if case_mod_date <= datetime.now() - timedelta(days=expire):
        LOG.debug("Expiring case %s: Modified date: %s", case, case_db[case].lastModifiedDate)
        del self.root["cases"][case]

  def close(self):
    """
    Cleanly close the DB file handles
    """
    transaction.commit()
    self.connection.close()
    self.db.close()
    self.storage.close()
