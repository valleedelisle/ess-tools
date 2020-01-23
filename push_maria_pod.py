#!/usr/bin/env python3
import logging
from kubernetes import client
import argparse

LOG = logging.getLogger("push_maria")
from lib.mariapod import Mariapod
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
  parser.add_argument('--list',
                      action='store_true',
                      default=False,
                      help='Only list stuff')
  parser.add_argument('-t', '--token',
                      action='store',
                      type=str,
                      help='Token used for authentication')
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
                      type=str,
                      help='MySQL dump file used to feed the container')
 
  return parser.parse_args()

def main():
  args = parse_args().__dict__
  CONF = Config(config_file=args['config_file'])
  if not args['cluster']:
    args['cluster'] = CONF.paas['url']
  if not args['token']:
    args['token'] = CONF.paas['token']
  maria = Mariapod(**args)
  maria.check_pvc(maria)
  maria.check_pv(maria)
  maria.check_svc(maria)
  maria.check_pod(maria)


if __name__ == '__main__':
    main()
