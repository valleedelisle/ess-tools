"""
Class that maps to the hydra api
"""

from urllib.parse import urlencode
import logging
from datetime import datetime
from db.models.cases import Case # pylint: disable=relative-beyond-top-level
from lib.req import Req


LOG = logging.getLogger("root.hydra")

class Hydra():
  """
  We need to pass the global config and the customer section's name
  """
  def __init__(self, conf, customer, jwt):
    self.username = conf.hydra['username']
    self.password = conf.hydra['password']
    self.api_url = conf.hydra['url']
    self.conf = conf
    self.customer = customer
    self.token = jwt.get_token()
    LOG.level = 10 if conf.notifierd.getboolean('debug') else 20

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

  def get(self, endpoint, query):
    """
    Wrapper for the API call
    """
    url = self.api_url + "/" + endpoint + "?" + urlencode(query)
    LOG.debug("Getting Hydra on %s", url)
    return Req(verb='GET', url=url, conf=self.conf, token=self.token).resp_data

  def put(self, endpoint, data):
    """
    Function that sends a PUT request to the hydra API
    Used in case tagging
    """
    url = self.api_url + "/" + endpoint
    LOG.debug("Putting Hydra on %s Data: %s", url, data)
    return Req(verb='PUT', url=url, data=data, token=self.token).resp_data

  def get_cases(self, query):
    """
    Wrapper that gets all the cases and returns a dict
    """
    return self.get("cases", query)

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
