"""
Returns the configuration object
"""

import configparser
import os

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
    config = CaseConfigParser(os.environ)
    config.read(config_file)
    self.__dict__.update(config)
    self.configparser = config
    self.config_file = config_file

  def __repr__(self):
    args = ['{} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
    return self.__class__.__name__ + '({})'.format(', '.join(args))
