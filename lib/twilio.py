"""
Twilio notification class
"""

import logging
from twilio.rest import Client # pylint: disable=no-name-in-module,import-error

LOG = logging.getLogger("twilio")

class Twilio():
  """
  Twilio notification class
  """
  # pylint: disable=too-few-public-methods
  def __init__(self, conf):
    self.account_sid = conf.notif_twilio['account_id']
    self.auth_token = conf.notif_twilio['auth_token']
    self.from_number = conf.notif_twilio['from']
    self.client = Client(self.account_sid, self.auth_token)

  def sms(self, dst, msg):
    """
    Send an sms via the twilio api
    """
    msg_out = None
    try:
      msg_out = self.client.messages.create(
        to="+" + dst,
        from_="+" + self.from_number,
        body=msg
      )
    except Exception as exc: # pylint: disable=broad-except
      LOG.error("Unable to send SMS to %s: Out: %s Exception: %s", dst, msg_out, exc)
