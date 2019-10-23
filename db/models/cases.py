# -*- coding: utf-8 -*-#
#!/usr/bin/env python
# pylint: disable=invalid-name,too-many-instance-attributes,import-outside-toplevel,cyclic-import
"""Case model"""

from datetime import datetime, timedelta
import logging

from db.models import sa, sao
from db.models import DeclarativeBase, session
from db.models.events import Event
import db.models as db_package


LOG = logging.getLogger("db.cases")

__all__ = ['Case']


class Case(DeclarativeBase):
  """
  Case DB Object
  """
  __tablename__ = 'cases'
  id = sa.Column(sa.String(32), primary_key=True)
  caseNumber = sa.Column(sa.String(8), unique=True)
  internalStatus = sa.Column(sa.String(32))
  severity = sa.Column(sa.String(32))
  accountName = sa.Column(sa.String(64))
  accountNumber = sa.Column(sa.Integer)
  caseOwnerName = sa.Column(sa.String(64))
  sbrGroup = sa.Column(sa.String(32))
  caseContact = sa.Column(sa.String)
  subject = sa.Column(sa.String)
  sbt = sa.Column(sa.Integer)
  remoteSessionCount = sa.Column(sa.Integer)
  numberOfBreaches = sa.Column(sa.Integer)
  lastUpdateDate = sa.Column(sa.DateTime)
  lastModifiedDate = sa.Column(sa.DateTime)
  createdDate = sa.Column(sa.DateTime)
  version = sa.Column(sa.String)
  critSit = sa.Column(sa.Boolean)
  isEscalated = sa.Column(sa.Boolean)
  fts = sa.Column(sa.Boolean)
  requestManagementEscalation = sa.Column(sa.Boolean)
  customerEscalation = sa.Column(sa.Boolean)
  conf_customer_name = sa.Column(sa.String(20))
  bugzillaNumber = sa.Column(sa.Integer)
  bugzillaSummary = sa.Column(sa.String(255))
  events = sao.relationship("Event", back_populates="case")

  def __init__(self, **kwargs):
    # Initializing some defaults
    self.caseOwnerName = 'unknown'
    self.sbt = 0
    self.sbrGroup = 'unknown' # pylint: disable=invalid-name
    self.accountName = 'unknown'
    self.accountNumber = 'unknown' # pylint: disable=invalid-name
    self.caseContact = 'unknown' # pylint: disable=invalid-name
    # We update the case model object
    self.__dict__.update(kwargs)
    try:
      self.accountName = kwargs['account']['name']
    except KeyError:
      pass
    # Converting the dates to datetime objects
    self.lastUpdateDate = datetime.strptime(self.lastUpdateDate, "%Y-%m-%dT%H:%M:%SZ")
    self.lastModifiedDate = datetime.strptime(self.lastModifiedDate, "%Y-%m-%dT%H:%M:%SZ")
    self.createdDate = datetime.strptime(self.createdDate, "%Y-%m-%dT%H:%M:%SZ")

    # More formatting
    if hasattr(self, 'ownerIRCNickname'):
      self.caseOwnerName = self.ownerIRCNickname
    elif hasattr(self, 'caseOwner'):
      self.caseOwnerName = self.caseOwner['name']
    elif hasattr(self, 'caseOwnerId'):
      self.caseOwnerName = self.caseOwnerId
    self.sfdc_url = self.conf.notifierd['sfdc_url'] + self.caseNumber
    self.ascension_url = self.conf.notifierd['ascension_url'].format(**self.__dict__)
    self.customer_portal_url = self.conf.notifierd['customer_portal_url'].format(**self.__dict__)

  def html(self):
    """
    Returns the html template for notification
    """
    return """
      <table border=1>
      <tbody>  
              <tr><th>Case</th><td><a href='{sfdc_url}'>{caseNumber}</a></td></tr>
              <tr><th>Status</th><td>{status} / {internalStatus}</td></tr>
              <tr><th>Severity</th><td>{severity}</td></tr>
              <tr><th>Account</th><td>{accountName} ({accountNumber})</td></tr>
              <tr><th>Owner</th><td>{caseOwnerName}</td></tr>
              <tr><th>SBR</th><td>{sbrGroup}</td></tr>
              <tr><th>Contact</th><td>{caseContact}</td></tr>
              <tr><th>Subject</th><td>{subject}</td></tr>
              <tr><th>SBT</th><td>{sbt}</td></tr>
              <tr><th># Breaches</th><td>{numberOfBreaches}</td></tr>
              <tr><th>Remote Sessions</th><td>{remoteSessionCount}</td></tr>
              <tr><th>Last Update</th><td>{lastUpdateDate}</td></tr>
              <tr><th>Modified Date</th><td>{lastModifiedDate}</td></tr>
              <tr><th>Created Date</th><td>{createdDate}</td></tr>
              <tr><th>Product Version</th><td>{version}</td></tr>
              <tr><th>FTS</th><td>{fts}</td></tr>
              <tr><th>RME</th><td>{requestManagementEscalation}</td></tr>
              <tr><th>Escalated</th><td>{isEscalated}</td></tr>
              <tr><th>Critical Situation</th><td>{critSit}</td></tr>
              <tr><th>Customer Escalaction</th><td>{customerEscalation}</td></tr>
          </tbody>
      </table> 
    """.format(**self.__dict__)

  def store_event(self, variable, text, notify=False, cooldown=1440): # pylint: disable=inconsistent-return-statements
    """
    store the events in a list for future reference
    variable: name of the case attribute to trigger an event on
    text: Text to be included in the event
    notify: Wether or not we trigger a notification
    cooldown: Number of minute before we re-trigger an event for a variable.
    """
    #from db.models.events import Event
    notification_time = self.conf.notifierd.getint('notification_time')
    notification_date = datetime.now() - timedelta(minutes=min(notification_time, cooldown))
    previous_events = session.query(Event, Case).join(Case)\
                             .filter(sa.and_(Case.caseNumber == self.caseNumber,
                                             Event.event_time >= notification_date,
                                             Event.variable == variable)).count()
    LOG.info("store_event (%s) text %s cooldown %s previous_events %s notification_date %s",
             variable, text, cooldown, previous_events, notification_date) # pylint: disable=logging-too-few-args
    if previous_events > 0:
      notify = False
      if cooldown < notification_time:
        LOG.debug("Skipping event")
        return False
    db_package.session.add(Event(case_id=self.id,
                                 variable=variable,
                                 text=text,
                                 notify=notify,
                                 conf=self.conf,
                                 case_object=self))
    db_package.session.flush()

  def validate_case(self, old_case):
    """
    Function that compares 2 cases and
    generates events for each discrepancy
    """
    case = old_case[0]
    self.severity_num = self.severity[0] # pylint: disable=attribute-defined-outside-init
    case.severity_num = case.severity[0]
    customer_conf = getattr(self.conf, self.conf_customer_name)
    if self.caseOwnerName != case.caseOwnerName:
      self.store_event('caseOwnerName', 'Case was chowned from {} to {}'
                       .format(case.caseOwnerName, self.caseOwnerName))
    if self.sbrGroup != case.sbrGroup:
      self.store_event('sbrGroup', 'SBR changed from {} to {}'
                       .format(case.sbrGroup, self.sbrGroup))
    if self.internalStatus != case.internalStatus:
      self.store_event('internalStatus',
                       'Internal Status went from {} to {}'
                       .format(case.internalStatus, self.internalStatus))
    if self.numberOfBreaches != case.numberOfBreaches:
      self.store_event('numberOfBreache', 'Case breached {} times'
                       .format(case.numberOfBreaches))
    if self.severity_num != case.severity_num:
      notify = self.severity_num < case.severity_num
      self.store_event('severity', 'Severity changed from {} to {}'
                       .format(case.severity, self.severity), notify)
    if self.requestManagementEscalation and not case.requestManagementEscalation:
      self.store_event('requestManagementEscalation', 'Case RME\'d', notify=True)
    if self.isEscalated and not case.isEscalated:
      self.store_event('isEscalated', 'Case escalated (isEscalated)', notify=True)
    if self.critSit and not case.critSit:
      self.store_event('critSit', 'Case is now critical (critSit)', notify=True)
    if self.customerEscalation and not case.customerEscalation:
      self.store_event('customerEscalation', 'Customer Escalation', notify=True)
    if self.fts and not case.fts:
      self.store_event('fts', 'Follow the sun flag activated (24x7)', notify=True)
    if int(self.sbt) <= int(customer_conf['min_sbt']) and int(self.sbt) != 0:
      self.store_event('sbt', 'Case {}breached. {} minutes{}'
                       .format('nearly ' if self.sbt > 0 else '',
                               int(self.sbt),
                               ' remaining' if self.sbt >= 0 else ''),
                       notify=True, cooldown=60)
