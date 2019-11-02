#!/usr/bin/env python3
"""
encoding: utf-8
Copyright (C) 2019 David Vallee Delisle <me@dvd.dev>
Notification tool for Red Hat's hydra API

"""

from __future__ import print_function
import time
import argparse
import traceback
import bugzilla
from lib.log import Log
from lib.config import Config
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
 
def bz_login():
  bzapi = bugzilla.Bugzilla('https://bugzilla.redhat.com', api_key=CONF.bugzilla['api_key'])
  return bzapi

def get_bug_cases(args):
  case = db_package.session.query(Case).filter(Case.bugzillaNumber > 0).filter(Case.conf_customer_name == args.customer).first()
  if args.get_bz:
    LOG.info("Logging into BZ")
    bzapi = bz_login()
  LOG.info("BZ: %s" % (case.bugzillaNumber))
  if args.get_bz:
    bug = bzapi.getbug(case.bugzillaNumber)
    print(bug)
    bz = ',\n'.join(["%s=%r" % (key, getattr(bug, key))
                 for key in sorted(bug.__dict__.keys())
                 if not key.startswith('_')])
    print(bz)

#  print("Fetched bug #%s:" % bug.id)
#  print("  Product   = %s" % bug.product)
#  print("  Component = %s" % bug.component)
#  print("  Status    = %s" % bug.status)
#  print("  Resolution= %s" % bug.resolution)
#  print("  Summary   = %s" % bug.summary)
#
if __name__ == '__main__':
  args = parse_args()
  LOG = Log(debug=args.debug, log_file=args.log_file)
  CONF = Config(config_file=args.config_file)
  db_package.init_model(CONF.sql['database'])
  LOG.info("Customer %s" % args.customer)
  get_bug_cases(args)
