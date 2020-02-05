#!/usr/bin/env python3
"""
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

Script that generates a container and imports a SQL file

"""
import sys

from kubernetes import client # pylint: disable=unused-import
from lib.log import Log
from lib.shift.mariapod import Mariapod
from lib.config import Config
from lib.hydra import Hydra
import db.models as db_package
from lib.argparser import mariadb_parse_args, add_osc_creds

def main():
  """
  Main function
  """
  args = mariadb_parse_args().__dict__
  LOG = Log(debug=args['debug'], log_file=args['log_file'])
  CONF = Config(config_file=args['config_file'])
  db_package.init_model(CONF.sql['database'])
  args = add_osc_creds(CONF, args)
  if args['case']:
    attachment = Hydra(CONF).find_attachments(args['case'], args['attachment_id'])
    LOG.info("Found attachment %s" % attachment)
    vol_size_multiplier = 5
    if not attachment:
      LOG.error("Attachment %s not found under case %s" % (args['attachment_id'], args['case']))
      sys.exit(1)
    if attachment.fileType == "application/x-xz" or attachment.fileName.endswith('.xz'):
      args['xunzip'] = True
      vol_size_multiplier = 25
    if attachment.fileType == "application/gzip" or attachment.fileName.endswith('.gz'):
      args['gunzip'] = True
      vol_size_multiplier = 10
    args['storage_size'] = max(round(attachment.size * vol_size_multiplier / 1000 / 1000 / 1000), 1)
    args['dump_file'] = attachment.link.replace('https://access.redhat.com/hydra/rest',
                                               CONF.hydra['attachments_url'])
  LOG.debug("Starting script: %s" % (args))
  Mariapod(**args)


if __name__ == '__main__':
  main()
