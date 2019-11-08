"""
Returns the configuration object
"""

import configparser
from os import environ
import re
import logging
LOG = logging.getLogger("root.config")

class CaseConfigParser(configparser.SafeConfigParser):# pylint: disable=too-many-ancestors
  """
  SafeConfigParser returns lower case attributes
  This is a workaround to prevent this
  """
  def optionxform(self, optionstr):
    return optionstr

class Config(object): # pylint: disable=useless-object-inheritance,too-few-public-methods
  """
  Returns the configuration object
  """
  def __init__(self, config_file=None):
    # Since we use dynamic service names, and configparser doesn't support nested interpolation
    # we need to rewrite environment to set MARIADB_SERVICE_HOST and MARIADB_SERVICE_PORT
    instance_name = environ['INSTANCE_NAME'].replace('-', '_').upper()
    pattern = r'^' + re.escape(instance_name) + r'_(MARIADB_SERVICE_(HOST|PORT))$'
    for key in environ:
      print("Checking %s = %s Pattern: %s Instancename: %s" %
            (key, environ[key], pattern, instance_name))
      match = re.match(pattern, key)
      if match:
        print("MATCH: %s = %s = %s" % (match.group(1), key, environ[key]))
        environ[match.group(1)] = environ[key]
    config = CaseConfigParser(environ)
    config.read(config_file)
    self.__dict__.update(config)
    self.configparser = config
    self.config_file = config_file

  def __repr__(self):
    args = ['{} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
    return self.__class__.__name__ + '({})'.format(', '.join(args))
