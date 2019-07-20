#!/usr/bin/env python3.6
"""
encoding: utf-8
Copyright (C) 2019 David Vallee Delisle <me@dvd.dev>
Notification tool for Red Hat's hydra API

"""

from __future__ import print_function
import time
import argparse
import unicodedata  # pylint: disable=unused-import
import persistent.dict # pylint: disable=unused-import
from pid import PidFile
from lib.event import Event
from lib.log import Log
from lib.zoodb import Zoo
from lib.hydra import Hydra
from lib.config import Config

def parse_args():
  """
  Function to parse arguments
  """
  parser = argparse.ArgumentParser(description='Hydra Case notifier Daemon')
  parser.add_argument('--debug',
                      default=False,
                      action='store_true',
                      help='Display debug information')
  parser.add_argument('-l',
                      '--log-file',
                      default='hydra-notifierd.log',
                      help='Log file')
  parser.add_argument('-w', '--working-dir', default='./')
  parser.add_argument('-c',
                      '--config-file',
                      nargs='+',
                      default=['hydra-notifierd.conf',
                               'hydra-notifierd-secrets.conf'])
  return parser.parse_args()

def hydra_poll(customer):
  """
  function that polls the hydra api and stores
  the data in the ZooDB
  """
  hydra = Hydra(CONF, customer)
  cases = hydra.poll()
  for case in cases:
    if case.caseNumber in CASE_DB.root['cases']:
      old_case = CASE_DB.root['cases'][case.caseNumber]
      case.notified = old_case.notified
      if hasattr(old_case, 'events'):
        case.events = old_case.events
      case.validate_case(old_case)
    # The check for new case is done here because validate_case
    # requires 2 cases, and new cases aren't already in DB normally
    if case.internalStatus == 'Unassigned':
      case.events.append(Event(case, 'internalStatus', 'New Case in Queue', notify=True, conf=CONF))
    # We must set this to make sure ZODB to saves the object to disk
    case._p_changed = True # pylint: disable=protected-access
    CASE_DB.root['cases'][case.caseNumber] = case
    LOG.debug(CASE_DB.root['cases'][case.caseNumber])

def start_daemon(args): # pylint: disable=redefined-outer-name
  """
  Function that starts the daemon
  """
  global CASE_DB # pylint: disable=global-variable-undefined
  try:
    with PidFile('hydra-notifierd', args.working_dir):
      LOG.info("Aguments: %s" % (args))
      while True:
        CONF.notifierd['debug'] = str(args.debug)
        LOG.debug("Conf %s" % (CONF))
        CASE_DB = Zoo(CONF.notifierd['database']) # pylint: disable=redefined-outer-name
        LOG.info("{0} cases in memory, sleep every {1} seconds"
                 .format(len(CASE_DB.root["cases"]), CONF.notifierd.getint('sleep')))
        for sec in CONF.configparser.sections():
          section = getattr(CONF, sec)
          if 'customer_' in sec and section.getboolean('enabled'):
            LOG.info("Checking %s Config: %s" % (sec, section))
            for key in section:
              LOG.debug("Customerconf: Key %s Value: %s" % (key, section[key]))
            hydra_poll(sec)

        LOG.info("Expiring objects older than %s days" % CONF.notifierd['expire'])
        CASE_DB.expire(CONF.notifierd.getint('expire'))
        CASE_DB.close()
        time.sleep(CONF.notifierd.getint('sleep'))

  except Exception as error: # pylint: disable=broad-except
    LOG.error("Daemon failed: %s" % error)

if __name__ == '__main__':
  args = parse_args()
  LOG = Log(debug=args.debug, log_file=args.log_file)
  CONF = Config(config_file=args.config_file)

  start_daemon(args)
