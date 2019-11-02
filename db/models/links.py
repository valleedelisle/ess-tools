# -*- coding: utf-8 -*-#
#!/usr/bin/env python
# pylint: disable=invalid-name,too-many-instance-attributes,import-outside-toplevel,cyclic-import
"""Link model"""

from datetime import datetime, timedelta
import logging

from db.models import sa, sao
from db.models import DeclarativeBase, session
import db.models as db_package


LOG = logging.getLogger("db.links")

__all__ = ['Link']


class Link(DeclarativeBase):
  """
  Link DB Object
  """
  __tablename__ = 'links'
  id = sa.Column(sa.Integer , primary_key=True , autoincrement=True)
  description = sa.Column(sa.String(250))
  status = sa.Column(sa.String(32))
  priority = sa.Column(sa.String(32))
  severity = sa.Column(sa.String(32))
  url = sa.Column(sa.String(150))
  bug_id = sa.Column(sa.Integer, sa.ForeignKey('bugs.id', ondelete='CASCADE'))
  bug = sao.relationship("Bug", back_populates="links")


