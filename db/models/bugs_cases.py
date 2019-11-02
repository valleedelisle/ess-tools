# -*- coding: utf-8 -*-#
#!/usr/bin/env python
# pylint: disable=cyclic-import
""" BugCase Link model """

from db.models import sa
from db.models import DeclarativeBase

bugs_cases_table = sa.Table('bugs_cases', DeclarativeBase.metadata,
  sa.Column('bug_id', sa.Integer, sa.ForeignKey('bugs.id'), primary_key = True),
  sa.Column('case_id', sa.String(32), sa.ForeignKey('cases.id'), primary_key = True)
)
