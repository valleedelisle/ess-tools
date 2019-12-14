"""
Class that manages the JWT
"""

import sys
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
  curl --data "grant_type=client_credentials&client_id=ess-automation&client_secret={secret}" \
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
    self.refresh_token = None
    self.token = None
    self.conf = conf
    LOG.level = 10 if conf.notifierd.getboolean('debug') else 20
    self.hydra_username = None
    self.hydra_password = None
    try:
      self.hydra_username = conf.hydra['username']
      self.hydra_password = conf.hydra['password']
    except KeyError:
      LOG.error("No credentials defined for hydra in config")
      sys.exit(1)


  def refresh(self):
    """
    Function that refreshes an access_token
    using the existing refresh_token
    """
    data = {'grant_type': 'client_credentials',
            'client_id': self.hydra_username,
            'client_secret': self.hydra_password
           }
    now = datetime.now()
    req = Req(verb='POST', url=self.url, data=data, conf=self.conf)
    LOG.debug("Response from refresh: %s", req)
    if req.response != 200:
      LOG.error("Unable to refresh token: %s", req)
      sys.exit(1)
    self.token = req.resp_data['access_token']
    self.refresh_token = req.resp_data['refresh_token']
    self.expiration_time = now + timedelta(seconds=req.resp_data['expires_in'])
    LOG.info("Refreshed token, good until %s", self.expiration_time)

  def get_token(self):
    """
    Returns the current access_token
    and calls for a refresh if necessary
    """
    if not self.expiration_time or datetime.now() > self.expiration_time - timedelta(minutes=5):
      LOG.info("Refreshing token. Expiration time: %s", self.expiration_time)
      self.refresh()
    return {"Authorization": "Bearer %s" % self.token}
