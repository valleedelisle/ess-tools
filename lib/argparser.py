# pylint: disable=no-member
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

library to parse args

"""
import sys
import argparse

def mariadb_parse_args():
  """
  Function to parse arguments from oc_mariadb.py
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
                      help='Size in Gi of the persistent volume ' + \
                      '(auto-calculated when providing --case and --attachment-id)')
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
  parser.add_argument('--dump-url',
                      action='store',
                      default=None,
                      type=str,
                      help='URL of the MySQL dump file used to feed the container')
  parser.add_argument('--case',
                      action='store',
                      default=None,
                      required='--attachment-id' in sys.argv,
                      type=str,
                      help='Case Number where we should download the attachment')
  parser.add_argument('--attachment-id',
                      action='store',
                      default=None,
                      type=str,
                      required='--case' in sys.argv,
                      help='Attachment UUID from the case where we download the attachment')


  return parser.parse_args()

def notifier_parse_args():
  """
  Function to parse arguments from hydra-notifierd.py
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

def bug_report_parse_args():
  """
  Function to parse arguments from bug-report.py
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



def add_osc_creds(conf, args):
  """
  Adds the openshift credentials to the arguments
  if they are not specifically defined
  """
  if not args['cluster']:
    args['cluster'] = conf.paas['url']
  if not args['token']:
    args['token'] = conf.paas['token']
  if not args['username']:
    args['username'] = conf.hydra['username']
  if not args['password']:
    args['password'] = conf.hydra['password']
  return args
