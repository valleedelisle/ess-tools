"""
Class that maps to the hydra api
"""

from urllib.parse import urlencode
import logging
from datetime import datetime, timedelta
from db.models.cases import Case # pylint: disable=relative-beyond-top-level
from db.models.attachments import Attachment # pylint: disable=relative-beyond-top-level
from lib.req import Req
from lib.jwt import Jwt


LOG = logging.getLogger("hydra")

class Hydra():
  """
  We need to pass the global config and the customer section's name
  """
  def __init__(self, conf, customer=None, jwt=None):
    self.cases_api_url = conf.hydra['cases_url']
    self.attachments_api_url = conf.hydra['attachments_url']
    self.attachment_time = int(conf.hydra['attachment_time'])
    self.conf = conf
    self.customer = customer
    if not jwt:
      jwt = Jwt(conf)
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
      hcase.last_update = datetime.now() - hcase.lastModifiedDate
      case_number = hcase.caseNumber
      if hcase.last_update > timedelta(days=self.conf.notifierd.getint('expire')):
        LOG.debug("Ignoring case %s because %s days old", case_number, hcase.last_update.days)
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

  def get_url(self, attachment=False):
    """
    Returns the right url, wether we want to poke at the attachment API or the normal
    case API.
    """
    return self.cases_api_url if not attachment else self.attachments_api_url

  def get(self, endpoint, query=None, attachment=False):
    """
    Wrapper for the API call
    """
    url = self.get_url(attachment) + "/" + endpoint
    if query:
      url += "?" + urlencode(query)
    LOG.debug("Getting Hydra on %s", url)
    return Req(verb='GET', url=url, conf=self.conf, token=self.token).resp_data

  def put(self, endpoint, data, attachment=False):
    """
    Function that sends a PUT request to the hydra API
    Used in case tagging
    """
    url = self.get_url(attachment) + "/" + endpoint
    LOG.debug("Putting Hydra on %s Data: %s", url, data)
    return Req(verb='PUT', url=url, data=data, token=self.token).resp_data

  def get_cases(self, query):
    """
    Wrapper that gets all the cases and returns a dict
    """
    return self.get("cases", query=query)

  def get_attachments(self, case_id):
    """
    Wrapper that gets all the cases and returns a dict
    {
      "caseNumber": "xxx",
      "uuid": "dbef0421-6e6b-483b-a77a-db3fac4175f0",
      "checksum": "7d516d267a95860258173b3ead707da83c5df31cc76c7d99aa7433c0d459f5d5",
      "createdDate": "2020-01-17T22:15:55Z",
      "createdBy": "Customer Name",
      "fileName": "sosreport-director-xxx-ifenxhh.tar.xz",
      "fileType": "application/x-xz",
      "id": "blabla",
      "isArchived": false,
      "isDeprecated": false,
      "isPrivate": false,
      "lastModifiedDate": "2020-01-17T22:15:55Z",
      "link": "https://access.redhat.com/hydra/rest/cases/xxx/attachments/xxx",
      "modifiedBy": "Customer Name",
      "size": 431430364,
      "sizeKB": 421318.71,
      "downloadRestricted": false
    },
    """
    endpoint = "cases/" + case_id + "/attachments"
    return self.get(endpoint, query=None, attachment=True)

  def filter_new_attachments(self, attachment):
    """
    Function to filter attachments from list based on specific criteria
    """
    if (datetime.now() - attachment.createdDate > timedelta(minutes=self.attachment_time) and
        ".sql" in attachment.fileName):
      return True
    return False

  def find_attachments(self, case_id, uuid=None):
    """
    Returns a list of filtered attachments
    """
    all_att = list()
    for hatt in self.get_attachments(case_id):
      att = Attachment(**hatt)
      if uuid and uuid == att.uuid:
        return att
      all_att.append(att)
    if uuid:
      return None
    attachments = list(filter(self.filter_new_attachments, all_att))
    LOG.debug("Filtered Attachments: %s", attachments)
    return attachments

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
