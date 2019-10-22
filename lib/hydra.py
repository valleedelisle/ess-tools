"""
Class that maps to the hydra api
"""

from urllib.parse import urlencode
import json
import re
import logging
from datetime import datetime
from time import sleep
import urllib3
from db.models.cases import Case # pylint: disable=relative-beyond-top-level


LOG = logging.getLogger("root.hydra")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Hydra():
  """
  We need to pass the global config and the customer section's name
  """
  def __init__(self, conf, customer):
    self.username = conf.hydra['username']
    self.password = conf.hydra['password']
    self.api_url = conf.hydra['url']
    self.conf = conf
    self.customer = customer
    LOG.level = 10 if conf.notifierd.getboolean('debug') else 20

  def auth_string(self):
    """
    Returns a mix of the username and password
    """
    return urllib3.util.make_headers(basic_auth=self.username+":"+self.password)

  def get_conf(self):
    """
    Returns the customer's config section object
    """
    return getattr(self.conf, self.customer)

  def poll(self):
    """
    function that polls the hydra api and stores
    the data in the ZooDB
    """
    query = self.build_query()
    live_cases = self.get_cases(query)
    case_list = []
    customer_conf = self.get_conf()
    ignored_sbr_list = customer_conf['ignored_sbr'].split(";")
    included_sbr_list = customer_conf['included_sbr'].split(";")
    for case in live_cases:
      case['conf'] = self.conf
      case['conf_customer_name'] = self.customer
      hcase = Case(**case)
      last_update = datetime.now() - hcase.lastModifiedDate
      case_number = hcase.caseNumber
      if last_update.days > self.conf.notifierd.getint('expire'):
        LOG.debug("Ignoring case %s because %s days old", case_number, last_update.days)
        continue
      case_sbr_list = hcase.sbrGroup.split(";")
      if 'ignored_sbr' in customer_conf:
        if set(case_sbr_list).issubset(ignored_sbr_list):
          LOG.debug("Ignoring case %s because all its SBR (%s) are in the "
                    "ignored SBR list %s", case_number, case_sbr_list, ignored_sbr_list)
          continue
      if 'included_sbr' in customer_conf:
        if not any(x in case_sbr_list for x in included_sbr_list):
          LOG.debug("Ignoring case %s because none of its SBR (%s) are in the "
                    "included SBR list: %s", case_number, case_sbr_list, included_sbr_list)
          continue
      case_list.append(hcase)

    return case_list



  def build_query(self):
    """
    Function to build the query string sent to hydra
    """
    query = {}
    customer_conf = self.get_conf()
    if 'sfdc_accounts' in customer_conf:
      query['accounts'] = ', '.join(customer_conf['sfdc_accounts'].split(' '))
    if 'status' in customer_conf and customer_conf['status'] != 'all':
      query['status'] = customer_conf['status']
    query['orderBy'] = customer_conf['order_by']
    query['orderDirection'] = customer_conf['order_direction']
    query['limit'] = customer_conf.getint('limit')
    return query


  def request(self, verb, url, data=None):
    """
    Establishes the request and returns the data
    """
    if LOG.level < 20:
      urllib3.add_stderr_logger()
    retries = urllib3.Retry(connect=self.conf.http_request.getint('retry_connect'),
                            status=self.conf.http_request.getint('retry_status'),
                            read=self.conf.http_request.getint('retry_read'),
                            total=self.conf.http_request.getint('retry_total'),
                            backoff_factor=self.conf.http_request.getint('backoff_factor'),
                            status_forcelist=self.conf.http_request['status_forcelist'].split(','))
    timeout = urllib3.Timeout(connect=self.conf.http_request.getint('timeout_connect'),
                              read=self.conf.http_request.getint('timeout_read'))
    response = 0
    while response != 200:
      http = urllib3.PoolManager(timeout=timeout, retries=retries,
                                 cert_reqs='CERT_NONE')
      headers = self.auth_string()
      json_data = None
      if re.match('PUT|POST', verb):
        if data is None:
          raise Exception("InvalidData", "When PUT/POST, we need data")
        json_data = str(json.dumps(data)).encode('utf-8')

      LOG.debug("Header: %s", headers)
      LOG.info("Verb: %s URL: %s Data: %s", verb, url, json_data)
      req = http.request(verb, url, body=json_data, headers=headers)
      response = req.status
      LOG.info("Response Code : %s", req.status)
      resp_data = str(req.data).replace("\\n", "\n").replace("\\t", "\t")
      LOG.debug("Reponse Data %s", resp_data)
      if req.status == 401 or req.status == 403:
        LOG.error("AuthenticationError: Return Code %s\n%s", req.status, req.data)
      if req.status == 404:
        LOG.error("ObjectNotFound: Return Code %s\n%s", req.status, req.data)
      if req.status >= 500:
        LOG.error("ServerError: Return Code %s\n%s", req.status, req.data)
      if req.status >= 400:
        LOG.error("UnknownError: Return Code %s\n%s", req.status, req.data)
      if req.status != 200:
        LOG.error("Response not 200 (%s), sleeping for 10 seconds", req.status)
        sleep(10)
    return req.data.decode('utf-8')

  def get(self, endpoint, query):
    """
    Wrapper for the API call
    """
    url = self.api_url + "/" + endpoint + "?" + urlencode(query)
    LOG.debug("Getting Hydra on %s", url)
    return self.request('GET', url)

  def put(self, endpoint, data):
    """
    Function that sends a PUT request to the hydra API
    Used in case tagging
    """
    url = self.api_url + "/" + endpoint
    LOG.debug("Putting Hydra on %s Data: %s", url, data)
    return self.request('PUT', url, data)

  def get_cases(self, query):
    """
    Wrapper that gets all the cases and returns a json
    """
    return json.loads(self.get("cases", query))

  def set_tags(self, case_id, tags):
    """
    Adds a list of tags to a case
    /cases/{caseNumber}/tags
    "put" : {
      "tags" : [ "cases" ],
      "summary" : "Add tags to case",
      "consumes" : [ "application/json" ],
      "produces" : [ "application/json" ],
      "parameters" : [ {
        "name" : "caseNumber",
        "in" : "path",
        "description" : "Case Number",
        "required" : true,
        "type" : "string"
      }, {
        "in" : "body",
        "name" : "body",
        "description" : "Case tags to add",
        "required" : true,
        "schema" : {
          "$ref" : "#/definitions/CaseTags"
        }
      } ],
      "responses" : {
        "200" : {
          "description" : "The case to which tags were added",
          "schema" : {
            "$ref" : "#/definitions/Case"
          }
        }
      },
      "x-camelContextId" : "restRoutes",
      "x-routeId" : "DataServicesCaseAddTags"
    },

    """
    endpoint = "cases/" + case_id + "/tags"
    obj = {}
    obj["tags"] = tags
    self.put(endpoint, obj)
