"""
Class that maps to the bz api
"""

import logging
import traceback
import sys
import signal
from time import sleep
from datetime import datetime as dt
import bugzilla
import urllib3
from requests.exceptions import ChunkedEncodingError


LOG = logging.getLogger("root.bz")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def handler(signum, frame):
  """
  Handler function passed by signal
  """
  LOG.error("BZAPI request expired")
  try:
    raise BzRequestTimeout("Request timeout", "Bugzilla Timeout")
  except: # pylint: disable=bare-except
    LOG.error("BZ request Timeout returned another taceback: %s", traceback.format_exc())
    sys.exit(2)

class BzRequestTimeout(Exception):
  """
  Custom exception used when the BZ api returns nothing
  """
  def __init__(self, message, errors):
    # Call the base class constructor with the parameters it needs
    super().__init__(message)
    self.errors = errors

class Bzapi(): # pylint: disable=too-few-public-methods
  """
  Class used to wrap the bugzilla session
  """
  def __init__(self, CONF):
    self.session = bugzilla.Bugzilla('https://bugzilla.redhat.com',
                                     api_key=CONF.bugzilla['api_key'])

class Bz():
  """
  Bug Object returned by the Bzapi()
  """
  api = None

  def bug_dict(self):
    """
    Function that returns a dict of the Bug object
    This is passed to the Bug model
    """
    return self.bug.__dict__

  def get(self):
    """
    This function trigs an api call to download the content
    of bug self.bzid.
    """
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(60)
    while not self.bug:
      try:
        self.bug = self.api.getbug(self.bzid)
      except (BzRequestTimeout, ChunkedEncodingError):
        self.bug = None
        sleep(10)
    LOG.debug("BZ Object %s", ",\n\t".join(["%s=%r" % (key, getattr(self.bug, key))
                                            for key in sorted(self.bug.__dict__.keys())
                                            if not key.startswith('_')]))
    while not self.comments:
      try:
        self.comments = self.bug.getcomments()
      except ConnectionResetError:
        self.comments = None
        sleep(10)

    self.bug.last_comment_time = dt.strptime(str(self.comments[-1]['creation_time']),
                                             "%Y%m%dT%H:%M:%S")
    self.bug.last_change_time = dt.strptime(str(self.bug.last_change_time), "%Y%m%dT%H:%M:%S")
    self.bug.creation_time = dt.strptime(str(self.bug.creation_time), "%Y%m%dT%H:%M:%S")
    for flag in self.bug.flags:
      bool_flag = flag['status'] == "+"
      setattr(self.bug, flag['name'], bool_flag)


  def __init__(self, **kwargs):
    self.conf = kwargs['conf']
    LOG.level = 10 if self.conf.notifierd.getboolean('debug') else 20
    self.bug = None
    self.comments = None
    self.bzid = kwargs['bzid']
    self.api = kwargs['api']
    self.get()
