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


LOG = logging.getLogger("db.bugs")

__all__ = ['Bug']


class Bug(DeclarativeBase):
  """
  Bug DB Object
  """
  __tablename__ = 'bugs'
  id = sa.Column(sa.String(32), primary_key=True)
  case_number = sa.Column(sa.String(8))
  cases = sao.relationship("Case", back_populates="bugs", secondary=bugs_cases_table)
  status = sa.Column(sa.String(12))
  summary = sa.Column(sa.String(200))
  assigned_to = sa.Column(sa.String(100))
  product = sa.Column(sa.String(100))
  component = sa.Column(sa.String(100))
  version = sa.Column(sa.String(12))
#  creation_time = sa.Column(DateTime)
#  last_change_time = sa.Column(DateTime)
  creator = sa.Column(sa.String(100))
  pm_ack = sa.Column(sa.Boolean)
  devel_ack = sa.Column(sa.Boolean)
  qa_ack = sa.Column(sa.Boolean)
  priority = sa.Column(sa.String(12))
  severity = sa.Column(sa.String(12))
  #description = sa.column(sa.LongText)
  #external_bugs=[{'ext_description': '[RFE][osp13] Overcloud drive partioning via template', 'ext_bz_id': 60, 'ext_priority': '4 (Low)', 'bug_id': 1644671, 'ext_bz_bug_id': '02241364', 'id': 862145, 'ext_status': 'Waiting on Red Hat', 'type': {'must_send': True, 'can_send': True, 'description': 'Red Hat Customer Portal', 'can_get': True, 'url': 'https://access.redhat.com', 'id': 60, 'send_once': True, 'type': 'SFDC', 'full_url': 'https://access.redhat.com/support/cases/%id%'}}, 
  internal_whiteboard = sa.Column(sa.String(100))
  is_open = sa.Column(sa.Boolean)
  resolution = sa.Column(sa.String(100))
