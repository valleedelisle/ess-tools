"""
Base object
"""

class Base(): # pylint: disable=too-few-public-methods
  """
  Base object
  """
  def __repr__(self):
    return '%s(%s)' % (
      (self.__class__.__name__),
      ', '.join(['%s=%r' % (key, getattr(self, key))
                 for key in sorted(self.__dict__.keys())
                 if not key.startswith('_') and not isinstance(getattr(self, key), Base)]))
