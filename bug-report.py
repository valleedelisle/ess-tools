#!/usr/bin/env python3.6
"""
encoding: utf-8
Copyright (C) 2019 David Vallee Delisle <me@dvd.dev>
Notification tool for Red Hat's hydra API

"""

from __future__ import print_function
import argparse
from lib.log import Log
from lib.config import Config
from lib.bz import Bzapi, Bz
from lib.air import Air
import db.models as db_package

from db.models.cases import Case
from db.models.bugs import Bug

def parse_args():
  """
  Function to parse arguments
  """
  parser = argparse.ArgumentParser(description='Bug report tool')
  parser.add_argument('--debug',
                      default=False,
                      action='store_true',
                      help='Display debug information')
  parser.add_argument('--customer',
                      required=True,
                      type=lambda d: "customer_%s" % d,
                      help='Customer name')

  parser.add_argument('-l',
                      '--log-file',
                      default='bug-report.log',
                      help='Log file')
  parser.add_argument('-b',
                      '--get-bz',
                      default=False,
                      action='store_true',
                      help='Download BZ information from bugzilla.redhat.com')
  parser.add_argument('-c',
                      '--config-file',
                      nargs='+',
                      default=['hydra-notifierd.conf',
                               'hydra-notifierd-secrets.conf'])
  return parser.parse_args()


def get_bug_cases():
  """
  Wrapper that will download the bz info from api,
  update table and airtable
  """
  if args.get_bz:
    bzapi = Bzapi(CONF)
  air_table = Air(conf=CONF)
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
  args = parse_args()
  LOG = Log(debug=args.debug, log_file=args.log_file)
  CONF = Config(config_file=args.config_file)
  db_package.init_model(CONF.sql['database'])
  LOG.info("Customer %s" % args.customer)
  get_bug_cases()
