#!/usr/bin/env python3
"""
encoding: utf-8
Copyright (C) 2020 David Vallee Delisle <dvd@redhat.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

### Description
Notification tool for Red Hat's hydra API

"""

from __future__ import print_function
import time
import traceback
import unicodedata  # pylint: disable=unused-import
from datetime import timedelta
from pid import PidFile
from lib.log import Log
from lib.hydra import Hydra
from lib.config import Config
from lib.jwt import Jwt
import db.models as db_package
from db.models.cases import Case
from lib.argparser import notifier_parse_args

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
    if case.last_update <= timedelta(minutes=CONF.hydra['attachment_time']):
      LOG.debug("Checking attachments for case %s", case.caseNumber)
      attachments = hydra.find_attachments(case_number)
      for att in attachments:
        old_att = db_package.session.query(Attachment).filter_by(id=att.id)
        if old_att.count() == 0:
          db_package.session.add(att)
          db_package.session.commit()
        else:
          old_att.update(att.__dict_repr__())
        if self.conf.hydra.getboolean('auto_dump_sql') is True:
          LOG.debug("Autodumping %s", att)


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
  args = notifier_parse_args()
  LOG = Log(debug=args.debug, log_file=args.log_file)
  CONF = Config(config_file=args.config_file)

  start_daemon(args)
