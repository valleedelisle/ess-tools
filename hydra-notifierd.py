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
import unicodedata  # pylint: disable=unused-import
from pid import PidFile
from lib.log import Log
from lib.hydra import Hydra
from lib.config import Config
from lib.jwt import Jwt
import db.models as db_package
from db.models.cases import Case


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
                      default='alembic/hydra-notifierd.log',
                      help='Log file')
  parser.add_argument('-w', '--working-dir', default='./')
  parser.add_argument('-c',
                      '--config-file',
                      nargs='+',
                      default=['hydra-notifierd.conf',
                               'hydra-notifierd-secrets.conf'])
  return parser.parse_args()

def hydra_poll(customer, jwt):
  """
  function that polls the hydra api and stores
  the data in the DB
  """
  hydra = Hydra(CONF, customer, jwt)
  cases = hydra.poll()
  for case in cases:
    old_case = db_package.session.query(Case).filter_by(id=case.id)
    if old_case.count() == 0:
      db_package.session.add(case)
      db_package.session.commit()
    if old_case.count() > 0:
      if hasattr(old_case, 'events'):
        case.events = old_case.events
      case.validate_case(old_case)
      old_case.update(case.__dict_repr__())
    if case.internalStatus == 'Unassigned':
      old_case.first().store_event('internalStatus', 'New Case in Queue', notify=True, cooldown=10)
    db_package.session.commit()

def start_daemon(args): # pylint: disable=redefined-outer-name
  """
  Function that starts the daemon
  """
  db_package.init_model(CONF.sql['database'])
  try:
    with PidFile('hydra-notifierd', args.working_dir):
      LOG.info("Aguments: %s" % (args))
      # Building the JWT object
      jwt = Jwt(CONF)
      while True:
        CONF.notifierd['debug'] = str(args.debug)
        LOG.debug("Conf %s" % (CONF))
        for sec in CONF.configparser.sections():
          section = getattr(CONF, sec)
          if 'customer_' in sec and section.getboolean('enabled'):
            LOG.info("Checking %s Config: %s" % (sec, section))
#            for key in section:
#              LOG.debug("Customerconf: Key %s Value: %s" % (key, section[key]))
            hydra_poll(sec, jwt)
            time.sleep(CONF.notifierd.getint('sleep'))

  except Exception as error: # pylint: disable=broad-except
    LOG.error("Daemon failed: %s" % error)
    LOG.error("%s" % traceback.format_exc())

if __name__ == '__main__':
  args = parse_args()
  LOG = Log(debug=args.debug, log_file=args.log_file)
  CONF = Config(config_file=args.config_file)

  start_daemon(args)
