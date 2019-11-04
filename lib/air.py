"""
Class that maps to the bz api
"""

import logging
import urllib3
from airtable import Airtable


LOG = logging.getLogger("root.airtable")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Air():
  """
  Object to interact with the airtable api
  """
  def __init__(self, **kwargs):
    self.conf = kwargs['conf']
    self.bug = None
    self.airtable = Airtable(self.conf.airtable['base_id'], "Bugs",
                             api_key=self.conf.airtable['api_key'])
    LOG.level = 10 if self.conf.notifierd.getboolean('debug') else 20

  def get(self, bug_id):
    """
    Method to pull a row based on bug_id
    """
    return self.airtable.search('Bug ID', bug_id)

  def add(self, **kwargs):
    """
    Method to add a new row
    """
    self.bug = kwargs['bug']
    acks = list()
    for flag in self.bug.bool_flags:
      if getattr(self.bug, flag):
        acks.append(flag)
    row = {'Bug ID': self.bug.id,
           'BZ Link': "https://bugzilla.redhat.com/%s" % self.bug.id,
           'Summary': self.bug.summary,
           'Priority': self.bug.priority,
           'Severity': self.bug.severity,
           'Status': self.bug.status,
           'Resolution': self.bug.resolution,
           'Assigned to': self.bug.assigned_to,
           'Opened Date': str(self.bug.creation_time),
           'Last Comment': str(self.bug.last_comment_time),
           'Last Modification': str(self.bug.last_change_time),
           'Product': self.bug.product,
           'Component': self.bug.component,
           'Version': self.bug.version,
           'Creator': self.bug.creator,
           'Ack': acks,
           'Cases': ','.join([key.caseNumber for key in self.bug.cases])
          }
    record = self.get(self.bug.id)
    if not record:
      LOG.info("Adding row to table")
      return self.airtable.insert(row)
    LOG.info("Updating row in table")
    return self.airtable.update(record[0]['id'], row)
