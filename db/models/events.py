# -*- coding: utf-8 -*-#
#!/usr/bin/env python
# pylint: disable=cyclic-import
""" Event model """
import hashlib
import logging
from datetime import datetime
from db.models import sa, sao
from db.models import DeclarativeBase
from lib.notifications import Notification

LOG = logging.getLogger("db.event")

class Event(DeclarativeBase): # pylint: disable=too-few-public-methods
  """
  Event table
  """
  __tablename__ = 'events'
  id = sa.Column(sa.String(32), primary_key=True) # pylint: disable=invalid-name
  case_id = sa.Column(sa.String(32), sa.ForeignKey('cases.id', ondelete='CASCADE'))
  event_time = sa.Column(sa.DateTime, default=datetime.utcnow)
  variable = sa.Column(sa.String(48))
  subject = sa.Column(sa.String(250))
  text = sa.Column(sa.String(250))
  notify = sa.Column(sa.Boolean)
  case = sao.relationship("Case", back_populates="events")

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)
    self.event_time = datetime.now()
    newid = str(self.case_id) + str(self.event_time) + kwargs.pop('variable')
    case = self.case_object
    self.id = str(hashlib.md5(newid.encode('UTF-8')).hexdigest()) # pylint: disable=invalid-name
    self.customer_conf = getattr(self.conf, case.conf_customer_name)
    self.subject = "[{0}] {1} {2} ({3}) {4} {5}".format(self.customer_conf['mail_tag'],
                                                        case.caseNumber,
                                                        case.accountName,
                                                        case.accountNumber,
                                                        case.severity,
                                                        self.text)
    # Boolean to validate if the event should be ignored
    # It's added below to the if
    no_ignored_events = (('ignored_events' in self.customer_conf and
                          self.variable not in self.customer_conf['ignored_events']) or
                         'ignored_events' not in self.customer_conf)
    if no_ignored_events:
      if self.notify:
        notification = Notification(case=case, event=self, conf=self.conf)
        notification.notify_users()
