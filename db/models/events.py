# -*- coding: utf-8 -*-#
#!/usr/bin/env python
""" Event model """
import hashlib
import logging
from datetime import datetime, timedelta

LOG = logging.getLogger("root.event")

from db.models import sa, sao, sasql, sad, hybrid_property, session
from db.models import DeclarativeBase, metadata
from lib.notifications import Notification
 
 
class Event(DeclarativeBase):
  __tablename__ = 'events'
  id = sa.Column(sa.String(32), primary_key=True)
  case_id = sa.Column(sa.String(32), sa.ForeignKey('cases.id', ondelete='CASCADE'))
  event_time = sa.Column(sa.DateTime, default=datetime.utcnow)
  variable = sa.Column(sa.String)
  subject = sa.Column(sa.String)
  text = sa.Column(sa.String)
  notify = sa.Column(sa.Boolean)
  case = sao.relationship("Case", back_populates="events")

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)
    self.event_time = datetime.now()
    newid = str(self.case_id) + str(self.event_time) + kwargs.pop('variable')
    LOG.info("New Event: %s %s" % (kwargs, self.case))
    case = self.case_object
    self.id = str(hashlib.md5(newid.encode('UTF-8')).hexdigest())
    self.customer_conf = getattr(self.conf, case.conf_customer_name)
    notification_date = self.event_time - timedelta(hours=self.conf.notifierd.getint('notification_time'))
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
      from db.models.cases import Case
      previous_events = session.query(Event, Case).join(Case).filter(sa.and_(Case.caseNumber==case.caseNumber,
                                                                  Event.event_time>=notification_date,
                                                                  Event.variable==self.variable)).count()
      LOG.info("Storing event for case %s -> %s: %s", case.caseNumber, self.variable, self.text)
      if self.notify and previous_events == 0:
        notification = Notification(case, self, self.conf)
        notification.notify_users()
