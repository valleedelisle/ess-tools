#!/usr/bin/env python3.6
"""
encoding: utf-8
Copyright (C) 2019 David Vallee Delisle <me@dvd.dev>
Report tool for Red Hat's cases
"""

from __future__ import print_function
from datetime import datetime, timedelta
from collections import defaultdict
import argparse
import unicodedata  # pylint: disable=unused-import
import persistent.dict # pylint: disable=unused-import
from lib.log import Log
from lib.zoodb import Zoo
from lib.config import Config

def parse_args():
  """
  Function to parse arguments
  """
  parser = argparse.ArgumentParser(description='Hydra Case Report tool')
  parser.add_argument('--debug',
                      default=False,
                      action='store_true',
                      help='Display debug information')
  parser.add_argument('-l',
                      '--log-file',
                      default='hydra-report.log',
                      help='Log file')
  parser.add_argument('-c',
                      '--config-file',
                      nargs='+',
                      default=['hydra-notifierd.conf',
                               'hydra-notifierd-secrets.conf'])
  parser.add_argument('-t',
                      '--time',
                      type=int, default=12, metavar="[1-288]",
                      choices=range(1, 288), help="Time to look back")
  return parser.parse_args()

def gen_report(args): # pylint: disable=redefined-outer-name
  """
  Function that starts the daemon
  """
  LOG.info("Aguments: %s" % (args))
  CONF.notifierd['debug'] = str(args.debug)
  LOG.debug("Conf %s" % (CONF))
  CASE_DB = Zoo(CONF.zodb['database'], CONF) # pylint: disable=redefined-outer-name
  LOG.info("{0} cases in memory".format(len(CASE_DB.root["cases"])))
  event_customer = defaultdict(dict)
  customer_cases = defaultdict(list)
  now = datetime.now()
  for case in CASE_DB.root['cases']:
    case_obj = CASE_DB.root['cases'][case]
    if case_obj.events:
      for event in sorted(case_obj.events, key=lambda x: x.time, reverse=True):
        if now-timedelta(hours=args.time) <= event.time:
          customer_cases[case_obj.customer].append(event)
  for customer in customer_cases:
    LOG.info("Customer %s" % customer)
    for event in customer_cases[customer]:
      LOG.info("Event: %s" % event.case)
  CASE_DB.close()

if __name__ == '__main__':
  args = parse_args()
  LOG = Log(debug=args.debug, log_file=args.log_file)
  CONF = Config(config_file=args.config_file)

  gen_report(args)
