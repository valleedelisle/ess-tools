"""
Logging class
"""

import logging
import logging.config


class Log():
  """
  Logging class object
  """
  def __init__(self, log_file=None, debug=False):
    # Logging options
    self.level = logging.INFO
    if debug is True:
      self.level = logging.DEBUG
    self.log_format = '%(asctime)s %(name)s %(levelname)s %(message)s at %(module)s:%(lineno)s'
    self.handlers = [logging.StreamHandler()]
    if log_file is not None:
      self.handlers.append(logging.FileHandler(log_file, encoding="utf8", mode='w'))
    logging.basicConfig(level=self.level,
                        format=self.log_format,
                        handlers=self.handlers)

    self.logger = logging.getLogger("root")
    self.logger.setLevel(self.level)
    self.logger.propagate = True
    if debug is True:
      requests_log = logging.getLogger("requests.packages.urllib3")
      requests_log.setLevel(logging.DEBUG)
      requests_log.propagate = True

  def get_log_file_handles(self, logger=None):
    """ Get a list of filehandle numbers from logger
        to be handed to DaemonContext.files_preserve
    """
    handles = []
    if logger is None:
      logger = self.logger
    for handler in logger.handlers:
      handles.append(handler.stream.fileno())
    if logger.parent:
      handles += self.get_log_file_handles(logger.parent)
    return handles

  def debug(self, msg):
    """
    Debug message
    """
    self.logger.debug(msg)

  def info(self, msg):
    """
    Info message
    """
    self.logger.info(msg)

  def warning(self, msg):
    """
    Warning message
    """
    self.logger.warning(msg)

  def error(self, msg):
    """
    Error message
    """
    self.logger.error(msg)
