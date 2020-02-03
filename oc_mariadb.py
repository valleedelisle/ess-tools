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

from kubernetes import client # pylint: disable=unused-import
from lib.log import Log
from lib.shift.mariapod import Mariapod
from lib.config import Config


def parse_args():
  """
  Function to parse arguments
  """
  parser = argparse.ArgumentParser(description='source database into container')
  parser.add_argument('--debug',
                      action='store_true',
                      default=False,
                      help='Display debug information')
  parser.add_argument('--gunzip',
                      action='store_true',
                      default=None,
                      help='Gunzip dump file after download')
  parser.add_argument('--xunzip',
                      action='store_true',
                      default=None,
                      help='unxz the dump file after download')
  parser.add_argument('--delete',
                      action='store_true',
                      dest='delete_deploy',
                      default=False,
                      help='Delete all resources for a deployment')
  parser.add_argument('--deploy',
                      action='store_true',
                      default=False,
                      help='Only list stuff')
  parser.add_argument('-u', '--username',
                      action='store',
                      type=str,
                      help='Salesforce username')
  parser.add_argument('-p', '--password',
                      action='store',
                      type=str,
                      help='Salesforce password')
  parser.add_argument('-t', '--token',
                      action='store',
                      type=str,
                      help='Token used for OpenShift authentication')
  parser.add_argument('-n', '--name',
                      action='store',
                      required=True,
                      type=str,
                      help='Name for the container, normally this is the case number')
  parser.add_argument('--cluster',
                      action='store',
                      type=str,
                      help='OpenShift Cluster address')
  parser.add_argument('--vol-size',
                      action='store',
                      default='20Gi',
                      dest='storage_size',
                      type=str,
                      help='Size of the persistent volume')
  parser.add_argument('--namespace',
                      action='store',
                      default='ess',
                      type=str,
                      help='Namespace or openshift project')
  parser.add_argument('-l',
                      '--log-file',
                      default='alembic/hydra-notifierd.log',
                      help='Log file')
  parser.add_argument('-c',
                      '--config-file',
                      nargs='+',
                      default=['hydra-notifierd.conf',
                               'hydra-notifierd-secrets.conf'])
  parser.add_argument('--dump-file',
                      action='store',
                      default=None,
                      type=str,
                      help='URL of the MySQL dump file used to feed the container')

  return parser.parse_args()

def main():
  """
  Main function
  """
  args = parse_args().__dict__
  LOG = Log(debug=args['debug'], log_file=args['log_file'])
  CONF = Config(config_file=args['config_file'])
  if not args['cluster']:
    args['cluster'] = CONF.paas['url']
  if not args['token']:
    args['token'] = CONF.paas['token']
  if not args['username']:
    args['username'] = CONF.hydra['username']
  if not args['password']:
    args['password'] = CONF.hydra['password']

  LOG.debug("Starting script: %s" % (args))
  Mariapod(**args)


if __name__ == '__main__':
  main()
