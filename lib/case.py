"""
Module for the case objects
"""

import logging
from datetime import datetime
import persistent
from .event import Event # pylint: disable=relative-beyond-top-level

LOG = logging.getLogger("root.hydra")


class Case(persistent.Persistent): # pylint: disable=too-many-instance-attributes
  """
  Module for the case objects
  """
  def __init__(self, **kwargs):
    self.notified = persistent.dict.PersistentDict()
    self.events = persistent.list.PersistentList()
    self.case_owner = 'unknown'
    self.sbt = 0
    self.sbrGroup = 'unknown' # pylint: disable=invalid-name
    self.account = {}
    self.account['name'] = 'unknown'
    self.caseContact = 'unknown' # pylint: disable=invalid-name
    self.accountNumber = 'unknown' # pylint: disable=invalid-name
    for key, value in kwargs.items():
      setattr(self, key, value)
    self.severity_num = self.severity[0]
    self._p_changed = True
    if hasattr(self, 'ownerIRCNickname'):
      self.case_owner = self.ownerIRCNickname
    elif hasattr(self, 'caseOwner'):
      self.case_owner = self.caseOwner['name']
    elif hasattr(self, 'caseOwnerId'):
      self.case_owner = self.caseOwnerId
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
              <tr><th>Account</th><td>{account[name]} ({accountNumber})</td></tr>
              <tr><th>Owner</th><td>{case_owner}</td></tr>
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
              <tr><th>Notifications</th><td>{notified}</td></tr>
              <tr><th>FTS</th><td>{fts}</td></tr>
              <tr><th>RME</th><td>{requestManagementEscalation}</td></tr>
              <tr><th>Escalated</th><td>{isEscalated}</td></tr>
              <tr><th>Critical Situation</th><td>{critSit}</td></tr>
              <tr><th>Customer Escalaction</th><td>{customerEscalation}</td></tr>
          </tbody>
      </table>
    """.format(**self.__dict__)

  def store_event(self, variable, text, notify=False): # pylint: disable=inconsistent-return-statements
    """
    store the events in a list for future reference
    """
    self.events.append(Event(self, variable, text,
                             time=datetime.now(), notify=notify, conf=self.conf))

  def validate_case(self, case):
    """
    Function that generates compares 2 cases and
    generates events for each discrepancy
    """
    if self.case_owner != case.case_owner:
      self.store_event('case_owner', 'Case was chowned from {} to {}'
                       .format(case.case_owner, self.case_owner))
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
      self.store_event('requestManagementEscalation', 'Case RME\'d', True)
    if self.isEscalated and not case.isEscalated:
      self.store_event('isEscalated', 'Case escalated (isEscalated)', True)
    if self.critSit and not case.critSit:
      self.store_event('critSit', 'Case is now critical (critSit)', True)
    if self.customerEscalation and not case.customerEscalation:
      self.store_event('customerEscalation', 'Customer Escalation', True)
    if self.fts and not case.fts:
      self.store_event('fts', 'Follow the sun flag activated (24x7)', True)
    if int(self.sbt) <= int(getattr(self.conf, self.customer)['min_sbt']) and int(self.sbt) != 0:
      self.store_event('sbt', 'Case {}breached. {} minutes{}'
                       .format('nearly ' if self.sbt > 0 else '',
                               int(self.sbt),
                               ' remaining' if self.sbt >= 0 else ''),
                       True)

  def __repr__(self):
    args = ['{} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
    return self.__class__.__name__ + '({})'.format(', '.join(args))
