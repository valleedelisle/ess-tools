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
import argparse
import sys
from kubernetes import client # pylint: disable=unused-import
from lib.log import Log
from lib.shift.make_mariapod import MakeMariapod
from lib.config import Config
from lib.argparse import mariadb_parse_args, add_osc_creds

def main():
  """
  Main function
  """
  args = mariadb_parse_args().__dict__
  LOG = Log(debug=args['debug'], log_file=args['log_file'])
  CONF = Config(config_file=args['config_file'])
  args = add_osc_args(CONF, args)
  args['command'] = sys.argv[1:]
  LOG.debug("Starting script: %s" % (args))
  MakeMariapod(**args)


if __name__ == '__main__':
  main()
