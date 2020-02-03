#!/usr/bin/env python3.6
"""
encoding: utf-8
Copyright (C) 2019 David Vallee Delisle <me@dvd.dev>
Notification tool for Red Hat's hydra API

"""

from __future__ import print_function
from lib.log import Log
from lib.config import Config
from lib.bz import Bzapi, Bz
from lib.air import Air
from lib.argparser import bug_report_parse_args
import db.models as db_package

from db.models.cases import Case
from db.models.bugs import Bug

def get_bug_cases():
  """
  Wrapper that will download the bz info from api,
  update table and airtable
  """
  if args.get_bz:
    bzapi = Bzapi(CONF)
  air_table = Air(conf=CONF, customer=args.customer)
  cases = db_package.session.query(Case).filter(Case.bugzillaNumber > 0)\
                                        .filter(Case.conf_customer_name == args.customer)
  for case in cases:
    bug = db_package.session.query(Bug).get(case.bugzillaNumber)
    LOG.info("Case %s" % (case.caseNumber))
    if args.get_bz:
      bug_from_api = Bz(conf=CONF, api=bzapi.session, bzid=case.bugzillaNumber)
      if bug:
        LOG.info("Found bug %s in the DB" % bug.id)
        bug.update(**bug_from_api.bug_dict())
      else:
        LOG.info("BZ %s is a new bug" % case.bugzillaNumber)
        bug = Bug(**bug_from_api.bug_dict())
        db_package.session.add(bug)
      if case not in bug.cases:
        bug.cases.append(case)
      db_package.session.flush()
      air_table.add(bug=bug)
  db_package.session.commit()

if __name__ == '__main__':
  args = bug_report_parse_args()
  LOG = Log(debug=args.debug, log_file=args.log_file)
  CONF = Config(config_file=args.config_file)
  db_package.init_model(CONF.sql['database'])
  LOG.info("Customer %s" % args.customer)
  get_bug_cases()
