# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""Attachment model"""

from datetime import datetime, timedelta
import logging

from db.models import sa, sao
from db.models import DeclarativeBase, session
from db.models.cases import Case # pylint: disable=unused-import
import db.models as db_package

LOG = logging.getLogger("db.attachments")

__all__ = ['Attachment']

class Attachment(DeclarativeBase):
  """
  Attachment DB Object
  """
  __tablename__ = 'cases'
  id = sa.Column(sa.String(32), primary_key=True)
  uuid = sa.Column(sa.String(32))
  caseNumber = sa.Column(sa.String(8), unique=True)
  checksum = sa.Column(sa.String(64))
  createdDate = sa.Column(sa.DateTime)
  createdBy = sa.Column(sa.String(64))
  fileName = sa.Column(sa.String(200))
  fileType = sa.Column(sa.String(32))
  isArchived = sa.Column(sa.Boolean)
  isDeprecated = sa.Column(sa.Boolean)
  isPrivate = sa.Column(sa.Boolean)
  lastModifiedDate = sa.Column(sa.DateTime)
  link = sa.Column(sa.String(200))
  modifiedBy = sa.Column(sa.String(64))
  size = sa.Column(sa.Integer)
  downloadRestricted = sa.Column(sa.Boolean)
  importedDumpStatus = sa.Column(sa.String(32))
  importedDumpContainer = sa.Column(sa.String(32))
  importedDumpHostIp = sa.Column(sa.String(32))
  importedDumpHostPort = sa.Column(sa.String(32))
  conf_customer_name = sa.Column(sa.String(20))
  case = sao.relationship("Case", back_populates="Attachments")

  def __init__(self, **kwargs):
    # Initializing some defaults
    self.__dict__.update(kwargs)
    self.lastModifiedDate = datetime.strptime(self.lastModifiedDate, "%Y-%m-%dT%H:%M:%SZ")
    self.createdDate = datetime.strptime(self.createdDate, "%Y-%m-%dT%H:%M:%SZ")
