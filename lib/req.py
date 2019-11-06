"""
Class that maps to the hydra api
"""

from urllib.parse import urlencode
import json
import re
import logging
from time import sleep
import http
import urllib3

LOG = logging.getLogger("root.req")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Req(): # pylint: disable=too-many-instance-attributes
  """
  Class to wrap around request
  """
  def __init__(self, **kwargs):
    self.data = None
    self.headers = {}
    self.token = None
    self.verb = kwargs['verb']
    self.url = kwargs['url']
    if 'headers' in kwargs:
      self.headers = kwargs['headers']
    if 'data' in kwargs:
      self.data = kwargs['data']
    if 'token' in kwargs:
      self.token = kwargs['token']
    LOG.level = 10 if conf.notifierd.getboolean('debug') else 20

    self.conf = kwargs['conf']
    if LOG.level < 20:
      urllib3.add_stderr_logger()
      http.client.HTTPConnection.debuglevel = 5

    self.retries = urllib3.Retry(connect=self.conf.http_request.getint('retry_connect'),
                                 status=self.conf.http_request.getint('retry_status'),
                                 read=self.conf.http_request.getint('retry_read'),
                                 total=self.conf.http_request.getint('retry_total'),
                                 backoff_factor=self.conf.http_request.getint('backoff_factor'),
                                 status_forcelist=self.conf.http_request['status_forcelist']\
                                                           .split(','))
    self.timeout = urllib3.Timeout(connect=self.conf.http_request.getint('timeout_connect'),
                                   read=self.conf.http_request.getint('timeout_read'))
    if self.token:
      self.headers.update(self.token)

    # We need the conf object to generate the retries and timeout config
    # But we can undefine it after.
    self.conf = None
    self.http = urllib3.PoolManager(timeout=self.timeout, retries=self.retries,
                                    cert_reqs='CERT_NONE')
    self.response = 0
    self.send()

  def send(self):
    """
    Function that sends the http request to destination
    """
    while self.response != 200:
      data = None
      if re.match('PUT|POST', self.verb):
        if not self.data:
          raise Exception("InvalidData", "When PUT/POST, we need data")
        if self.token:
          data = json.dumps(self.data).encode('utf-8')
          self.headers.update({'Content-Type': 'application/json'})
        else:
          # Apparently, the openid iam thing doesn't like application/json content-type,
          # we need to pass a form
          self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
          data = urlencode(self.data)

      LOG.debug("Header: %s", self.headers)
      LOG.info("Verb: %s URL: %s Data: %s", self.verb, self.url, data)
      req = self.http.request(self.verb, self.url, body=data, headers=self.headers)
      self.response = req.status
#      LOG.debug("Raw response data: %s" % req.data)
      try:
        self.resp_data = json.loads(req.data.decode('utf-8'))
      except json.decoder.JSONDecodeError:
        self.resp_data = req.data
      self.validate_response()

  def validate_response(self):
    """
    Function to validate the http response
    and act accordingly
    """
    LOG.info("Response Code : %s", self.response)
    LOG.debug("Reponse Data %s", self.resp_data)
    if self.response == 401 or self.response == 403:
      LOG.error("AuthenticationError: Return Code %s\n%s", self.response, self.resp_data)
    if self.response == 404:
      LOG.error("ObjectNotFound: Return Code %s\n%s", self.response, self.resp_data)
    if self.response >= 500:
      LOG.error("ServerError: Return Code %s\n%s", self.response, self.resp_data)
    if self.response >= 400:
      LOG.error("UnknownError: Return Code %s\n%s", self.response, self.resp_data)
    if self.response != 200:
      LOG.error("Response not 200 (%s), sleeping for 10 seconds", self.response)
      sleep(10)
