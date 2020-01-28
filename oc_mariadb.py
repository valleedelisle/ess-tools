#!/usr/bin/env python3
import logging
from kubernetes import client
import argparse

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

  maria = Mariapod(**args)


if __name__ == '__main__':
    main()
