# -*- coding: utf-8 -*-#
#!/usr/bin/env python
# pylint: disable=invalid-name,too-many-instance-attributes,import-outside-toplevel,cyclic-import
"""Bug model"""

from datetime import datetime, timedelta
import logging

from db.models import sa, sao
from db.models import DeclarativeBase, session
from db.models.bugs_cases import bugs_cases_table
import db.models as db_package
from db.models.links import Link


LOG = logging.getLogger("db.bugs")

__all__ = ['Bug']


class Bug(DeclarativeBase):
  """
  Bug DB Object
  """
  __tablename__ = 'bugs'
  id = sa.Column(sa.String(32), primary_key=True)
  status = sa.Column(sa.String(12))
  summary = sa.Column(sa.String(200))
  assigned_to = sa.Column(sa.String(100))
  product = sa.Column(sa.String(100))
  component = sa.Column(sa.String(100))
  version = sa.Column(sa.String(12))
  creation_time = sa.Column(sa.DateTime)
  last_change_time = sa.Column(sa.DateTime)
  last_comment_time = sa.Column(sa.DateTime)
  creator = sa.Column(sa.String(100))
  pm_ack = sa.Column(sa.Boolean)
  devel_ack = sa.Column(sa.Boolean)
  qa_ack = sa.Column(sa.Boolean)
  priority = sa.Column(sa.String(12))
  severity = sa.Column(sa.String(12))
  description = sa.column(sa.Text)
  internal_whiteboard = sa.Column(sa.String(100))
  is_open = sa.Column(sa.Boolean)
  resolution = sa.Column(sa.String(100))
  cases = sao.relationship("Case", secondary=bugs_cases_table, back_populates="bugs")
  links = sao.relationship("Link", back_populates="bug")
  bool_flags = ('pm_ack', 'qa_ack', 'devel_ack')

  def __init__(self, **kwargs):

    self.__dict__.update(kwargs)
    self.creation_time = datetime.strptime(str(self.creation_time), "%Y%m%dT%H:%M:%S")
    self.last_change_time = datetime.strptime(str(self.last_change_time), "%Y%m%dT%H:%M:%S")
    self.last_comment_time = datetime.strptime(str(self.last_comment_time), "%Y%m%dT%H:%M:%S")
