"""
Returns the configuration object
"""

import configparser
from os import environ
import re

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
    for key in environ:
      match = re.match('.*(MARIADB_SERVICE_(HOST|PORT))', key)
      if match:
        environ[match.group(1)] = environ[key]
    config = CaseConfigParser(environ)
    config.read(config_file)
    self.__dict__.update(config)
    self.configparser = config
    self.config_file = config_file

  def __repr__(self):
    args = ['{} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
    return self.__class__.__name__ + '({})'.format(', '.join(args))
