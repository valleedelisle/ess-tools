"""
Class that manages the JWT
"""

import sys
from os import environ
import logging
from datetime import datetime, timedelta
from lib.req import Req

LOG = logging.getLogger("root.jwt")

class Jwt():
  """
  This class will interact with the IAM
  examples with curl:
  curl -d "username=$RHN_USER&password=$RHN_PASS&grant_type=password&client_id=hydra-client-cli" \
   https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token
  curl -X POST -d "refresh_token=xxx&grant_type=refresh_token&client_id=hydra-client-cli" \
    https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token

  returns: {
            "access_token":"xxx",
            "expires_in":900,
            "refresh_expires_in":36000,
            "refresh_token":"xxx",
            "token_type":"bearer",
            "not-before-policy":0,
            "session_state":"xxx"
          }
  """
  def __init__(self, conf):
    self.url = conf.DEFAULT['openid_url']
    self.expiration_time = None
    self.token = None
    try:
      self.refresh_token = environ['JWT_REFRESH_TOKEN']
    except NameError:
      LOG.error("Missing refresh_token: %s", environ)
      sys.exit(1)
    self.conf = conf
    LOG.level = 10 if conf.notifierd.getboolean('debug') else 20

  def refresh(self):
    """
    Function that refreshes an access_token
    using the existing refresh_token
    """
    data = {'refresh_token': '%s' % self.refresh_token,
            'grant_type': 'refresh_token',
            'client_id': 'hydra-client-cli'}
    now = datetime.now()
    req = Req(verb='POST', url=self.url, data=data, conf=self.conf)
    LOG.debug("Response from refresh: %s", req.resp_data)
    self.token = req.resp_data['access_token']
    self.refresh_token = req.resp_data['refresh_token']
    environ['JWT_REFRESH_TOKEN'] = self.refresh_token
    environ['JWT_REFRESH_TIME'] = now
    self.expiration_time = now + timedelta(seconds=req.resp_data['expires_in'])

  def get_token(self):
    """
    Returns the current access_token
    and calls for a refresh if necessary
    """
    if not self.expiration_time or datetime.now() > self.expiration_time - timedelta(minutes=5):
      LOG.info("Refreshing token. Expiration time: %s", self.expiration_time)
      self.refresh()
    return {"Authorization": "Bearer %s" % self.token}
