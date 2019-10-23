# -*- coding: utf-8 -*-#
#!/usr/bin/env python
""" Notification model """
# get all the SA stuff
import logging
import requests
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from lib.gchat import Gchat
from lib.twilio import Twilio
from lib.mail import Email

LOG = logging.getLogger("root.notification")

class Notification():
  """
  Notification object
  """

  def __init__(self, case, event, conf):
    self.case = case
    self.event = event
    self.conf = conf
    self.customer_conf = getattr(self.conf, case.conf_customer_name)

  def send_sms(self):
    """
    Send sms with case data
    """
    if (self.conf.notif_twilio.getboolean('enabled') is True and
        'sms_list' in self.customer_conf):
      msg = ("Case {caseNumber} - {severity} - {account[name]} - "
             "{sbrGroup} - {text}\n{subject}\n{sfdc_url}")
      LOG.info("SMS to %s: %s", self.customer_conf['sms_list'],
               str(msg.format(**self.case.__dict__)))
      twilio = Twilio(self.conf)
      for phone in self.customer_conf['sms_list'].split(' '):
        twilio.sms(phone, msg.format(**self.case.__dict__))

  def send_gchat(self):
    """
    Send gchat notification with the case data
    """
    if (self.conf.notif_gchat.getboolean('enabled') and
        'gchat_room' in self.customer_conf):
      credentials = ServiceAccountCredentials.from_json_keyfile_name(
        self.conf.notif_gchat['credentials'], self.conf.notif_gchat['scopes'])
      chat = build('chat', 'v1', http=credentials.authorize(Http()), cache_discovery=False)
      gchat = Gchat(self.event)
      room_name = 'spaces/' + self.customer_conf['gchat_room']
      LOG.info("Gchat card %s", gchat.card)
      resp = chat.spaces().messages().create(  # pylint: disable=no-member
        parent=room_name,
        threadKey=self.case.caseNumber,
        body=gchat.card).execute()
      LOG.info("Gchat response: %s", resp)

  def send_smtp(self):
    """
    Send notification by email using a SMTP server
    """

    if (self.conf.notif_email.getboolean('enabled') and
        'mailing_list' in self.customer_conf):
      LOG.info("Sending email to %s", self.customer_conf['mailing_list'])
      Email(self.conf, self.customer_conf['mailing_list'], self.event.subject,
            str(self.case.__dict__), self.case.html())

  def send_mailgun(self):
    """
    Send notification using the mailgun API
    """
    if (self.conf.notif_mailgun.getboolean('enabled') and
        'mailing_list' in self.customer_conf):
      LOG.info("EMAIL to %s", self.customer_conf['mailing_list'])
      LOG.debug("HTML Content: %s", self.case.html())
      mailresponse = requests.post(
        "https://api.mailgun.net/v3/{0}/messages".format(self.conf.notif_mailgun['domain']),
        auth=("api", self.conf.notif_mailgun['api_key']),
        data={"from": self.conf.notif_mailgun['from'],
              "to": self.customer_conf['mailing_list'],
              "subject": self.event.subject,
              "text": str(self.case.__dict__),
              "html": "<html>" + self.case.html() + "</html>"
             })
      LOG.info("Mailgun response: %s", mailresponse)
      if mailresponse != 200:
        LOG.error("Error sending email")


  def notify_users(self):
    """
    Send a notification with the event
    """
    if (self.customer_conf.getint('min_severity') > int(self.case.severity[0]) or
        self.customer_conf.getint('max_severity') < int(self.case.severity[0])):
      LOG.warning("Skipping notification for %s "
                  "because it's off severity range (%s <= %s <= %s)",
                  self.case.caseNumber,
                  self.customer_conf.getint('min_severity'),
                  self.case.severity,
                  self.customer_conf.getint('max_severity'))
      return
    if 'Closed' in self.case.status:
      LOG.warning("Skipping notification for %s because case is closed",
                  self.case.caseNumber)
      return

    LOG.info("Sending notification for case %s%s: %s",
             self.conf.notifierd['sfdc_url'], self.case.caseNumber, self.event.subject)

    self.send_sms()
    self.send_gchat()
    self.send_mailgun()
    self.send_smtp()

  def __repr__(self):
    args = ['{} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
    return self.__class__.__name__ + '({})'.format(', '.join(args))
