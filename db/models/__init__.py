# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""SQLAlchemy models for the application
In a smaller application you could have all models in this file, but we
assumed this will grow and have there split things up, in which case you
should import you sub model at the bottom of this module.
"""

import sys
import sqlalchemy as sa
import sqlalchemy.orm as sao
import sqlalchemy.sql as sasql
import sqlalchemy.ext.declarative as sad
from sqlalchemy.ext.hybrid import hybrid_property


if not hasattr(sys, 'frozen'):
  # needed when having multiple versions of SA installed
  try:
    # only do this if pkg_resources are installed
    import pkg_resources
    pkg_resources.require("sqlalchemy>=1.3") # get latest version
  except ImportError:
    pass

maker = sao.sessionmaker(autoflush=True, autocommit=False)
session = sao.scoped_session(maker)

class ReprBase(): # pylint: disable=too-few-public-methods
  """Extend the base class
  Provides a nicer representation when a class instance is printed.
  """
  def __dict_repr__(self):
    dicts = {}
    mapper = sa.inspect(self.__class__)
    for key in sorted(self.__dict__.keys()):
      if key in mapper.columns.keys() and not key.startswith('_'):
        dicts[key] = getattr(self, key)
    return dicts

  def update(self, **kwargs):
    for key, value in kwargs.items():
      setattr(self, key, value)

  def __repr__(self):
    return "%s(%s)" % (
      (self.__class__.__name__),
      ', '.join(["%s=%r" % (key, getattr(self, key))
                 for key in sorted(self.__dict__.keys())
                 if not key.startswith('_')]))

DeclarativeBase = sad.declarative_base(cls=ReprBase)
metadata = DeclarativeBase.metadata

def init_model(connection_string):
  """Call me before using any of the tables or classes in the model."""
  engine = sa.create_engine(connection_string, echo=True)
  session.configure(bind=engine)

#from db.models.events import Event # pylint: disable=wrong-import-position
#from db.models.cases import Case # pylint: disable=wrong-import-position
