# -*- coding: utf-8 -*-#
#!/usr/bin/env python
# pylint: disable=cyclic-import
""" BugLink model """

from db.models import sa
from db.models import DeclarativeBase

bugs_links_table = sa.Table('bugs_links', DeclarativeBase.metadata,
  sa.Column('bug_id', sa.Integer, sa.ForeignKey('bugs.id'), primary_key = True),
  sa.Column('link_id', sa.String(32), sa.ForeignKey('link.id'), primary_key = True)
)
