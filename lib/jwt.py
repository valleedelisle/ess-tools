"""
Class that manages the JWT
"""

import sys
from os import environ
import logging
from datetime import datetime, timedelta
from lib.req import Req

LOG = logging.getLogger("root.jwt")

class RefreshToken():
  """
  refresh_token object
  """
  def __init__(self, conf):
    self.token_file = conf.DEFAULT['jwt_refresh_token_path']
    self.file = None
    self.env = None
    self.get()

  def get(self):
    """
    Find refresh_token
    """
    try:
      with open(self.token_file, "r") as token_file:
        self.file = token_file.read()
    except: # pylint: disable=bare-except
      self.file = None
      LOG.warning("No token in file %s", self.token_file)
    try:
      self.env = environ['JWT_REFRESH_TOKEN']
    except NameError:
      LOG.error("Missing refresh_token in environment: %s", environ)
      sys.exit(1)

  def save(self, token):
    """
    Function to save a new refresh token to a file
    """
    with open(self.token_file, "w") as token_file:
      token_file.write(token)

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
    self.refresh_token = None
    self.token = None
    self.conf = conf
    LOG.level = 10 if conf.notifierd.getboolean('debug') else 20

  def refresh(self):
    """
    Function that refreshes an access_token
    using the existing refresh_token
    """
    refresh_tokens = RefreshToken(self.conf)
    for method in ['file', 'env']:
      refresh_token = getattr(refresh_tokens, method)
      data = {'refresh_token': '%s' % refresh_token,
              'grant_type': 'refresh_token',
              'client_id': 'hydra-client-cli'}
      now = datetime.now()
      req = Req(verb='POST', url=self.url, data=data, conf=self.conf)
      LOG.debug("Response from refresh: %s", req)
      if req.response != 200:
        LOG.error("Unable to refresh token: %s", req)
        continue
      self.token = req.resp_data['access_token']
      self.refresh_token = req.resp_data['refresh_token']
      self.expiration_time = now + timedelta(seconds=req.resp_data['expires_in'])
      # We need to keep a persistent copy of the refresh_token for rebuilds
      refresh_tokens.save(self.refresh_token)
      LOG.info("Refreshed token, good until %s saved in %s", self.expiration_time,
               refresh_tokens.token_file)
      return
    if req.response != 200:
      LOG.error("Failed to refresh_token, update JWT_REFRESH_TOKEN in environment")
      #sys.exit(1)

  def get_token(self):
    """
    Returns the current access_token
    and calls for a refresh if necessary
    """
    if not self.expiration_time or datetime.now() > self.expiration_time - timedelta(minutes=5):
      LOG.info("Refreshing token. Expiration time: %s", self.expiration_time)
      self.refresh()
    return {"Authorization": "Bearer %s" % self.token}
